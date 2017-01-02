djet
====

|Build Status|
|Coverage|

**Django Extended Tests** is set of helpers for easy testing of Django apps.

Main features:

- easy unit testing of Django views (``ViewTestCase``)
- additional useful assertions for testing:

  - response status codes (``StatusCodeAssertionsMixin``)
  - emails (``EmailAssertionsMixin``)
  - messages (``MessagesAssertionsMixin``)
  - model instances (``InstanceAssertionsMixin``)

- handy helpers for testing file-related code (``InMemoryStorageMixin`` and others)
- smooth integration with Django REST Framework authentication mechanisim (``APIViewTestCase``)

Developed by `SUNSCRAPERS <http://sunscrapers.com>`__ with passion & patience.

Installation
============

To install **djet** use ``pip``:

``$ pip install djet``

Why djet?
=========

Testing views
-------------

Django test client performs integration tests. All middlewares, resolvers,
decorators and so on are tested. Just a single failure in a middleware can
break all the view tests.

`One technique <http://tech.novapost.fr/django-unit-test-your-views-en.html>`__
of performing the tests was presented at DjangoCon Europe 2013 Warsaw.
We have always used a slightly different method, which we would like to present
as an alternative to the DjangoCon approach.

**djet** makes performing unit tests for your views easier by providing ``ViewTestCase``.
Instead of ``self.client`` you will use ``self.factory`` which is an
extended ``RequestFactory`` with overridden shortcuts for creating requests
(eg. ``path`` is not required parameter).

Sometimes you would need middlewares to be applied in order to test the view.
There is an option that helps specify which middlewares should be used in
a single test or a whole test case by applying ``middleware_classes`` argument.
This argument should be a list of middleware classes (e.g. ``SessionMiddleware``)
or tuples where first argument is middleware class and rest items are middleware
types (from ``MiddlewareType`` class). In this case only indicated middleware methods
will be call.

Additional assertions
---------------------

There are also some additional useful assertions in different mixins in
``djet.assertions`` module.

Currently there are ``StatusCodeAssertionsMixin``, ``EmailAssertionsMixin``,
``MessagesAssertionsMixin`` and ``InstanceAssertionsMixin``
full of useful assertions.

Remember that if you want to use assertions eg. from ``MessagesAssertionsMixin``
you must also add ``middleware_classes`` required by messages to your test case.
We do not add them for you in mixin, because we believe those mixins shouldn't
mess with middlewares, as they are required by your view in fact.

Helpers for testing files uploads
---------------------------------

There are three main annoying things while testing files related things in Django
and ``djet.files`` module helps with all of them

First thing - you will not need any files put somewhere next to fixtures anymore.
``create_inmemory_file`` and ``create_inmemory_image`` are ready to use.
Those helpful functions are taken from
`great blog post by Piotr Maliński <http://www.rkblog.rk.edu.pl/w/p/temporary-files-django-tests-and-fly-file-manipulation/>`__
with just a few small changes.

You can also use ``InMemoryStorage`` which deals with files being saved to disk
during tests and speed ups tests by keeping them in memory.

``InMemoryStorageMixin`` does another great thing.
It replaces ``DEFAULT_FILE_STORAGE`` with ``InMemoryStorage`` for you and also
removes all files after test ``tearDown``, so you will no longer see any files
crossing between tests. You can also give here any storage you want,
it only should implement ``clear`` method which is invoked after tearDown.
``InMemoryStorageMixin`` cannot be used with bare ``unittest.TestCase``,
you have to use ``TestCase`` from Django or ``ViewTestCase`` from **djet**.

Other utils
-----------

``utils.refresh`` helps you get newer version of object from database
in a very simple way.

Examples
========

We encourage you to import whole djet modules, not classes.

.. code:: python

    from djet import assertions, testcases
    from django.contrib import messages
    from django.contrib.messages.middleware import MessageMiddleware
    from django.contrib.sessions.middleware import SessionMiddleware
    from yourapp.views import YourView
    from yourapp.factories import UserFactory

    class YourViewTest(assertions.StatusCodeAssertionsMixin,
                       assertions.MessagesAssertionsMixin,
                       testcases.ViewTestCase):
        view_class = YourView
        view_kwargs = {'some_kwarg': 'value'}
        middleware_classes = [
            SessionMiddleware,
            (MessageMiddleware, testcases.MiddlewareType.PROCESS_REQUEST),
        ]

        def test_post_should_redirect_and_add_message_when_next_parameter(self):
            request = self.factory.post(data={'next': '/'}, user=UserFactory())

            response = self.view(request)

            self.assert_redirect(response, '/')
            self.assert_message_exists(request, messages.SUCCESS, 'Success!')

If you want to test function-based view you should do it like this:

.. code:: python

    class YourFunctionViewTest(testcases.ViewTestCase):
        view_function = your_view

There is special ``create_view_object`` helper for testing single view methods,
which applies the view_kwargs specified to created view object.
You can also provide request, args and kwargs here and they will be bounded to view,
like it normally happens in dispatch method.

You can always create view object with different kwargs by using
``self.view_class`` constructor.

.. code:: python

    class YourViewObjectMethodTest(testcases.ViewTestCase):
        view_class = YourView
        view_kwargs = {'redirect_url': '/'}

        def test_some_view_method(self):
            request = self.factory.get()
            view_object = self.create_view_object(request, 'some arg', pk=1)

            view_object.some_method()

            self.assertTrue(view_object.some_method_called)

An example of test using all files goodies from **djet**:

.. code:: python

    from djet import files
    from django.core.files.storage import default_storage
    from django.test.testcases import TestCase

    class YourFilesTests(files.InMemoryStorageMixin, TestCase):

        def test_creating_file(self):
            created_file = files.create_inmemory_file('file.txt', 'Avada Kedavra')

            default_storage.save('file.txt', created_file)

            self.assertTrue(default_storage.exists('file.txt'))

You can also make assertions about the lifetime of model instances.
The ``assert_instance_created`` and ``assert_instance_deleted`` methods of
``InstanceAssertionsMixin`` can be used as context managers. They ensure
that the code inside the ``with`` statement resulted in either creating
or deleting a model instance.

.. code:: python

    from django.test import TestCase
    from djet import assertions
    from yourapp.models import YourModel

    class YourModelTest(assertions.InstanceAssertionsMixin, TestCase):

        def test_model_instance_is_created(self):
            with self.assert_instance_created(YourModel, field='value'):
                YourModel.objects.create(field='value')

Utils example:

.. code:: python

    from djet import utils, testcases
    from yourapp.models import Flower
    from yourapp.views import ChangeFlowerView

    class ChangeFlowerViewTest(testcases.ViewTestCase):

        def test_changing_flower_color(self):
            flower = Flower.objects.create(color='orange')
            post_data = {
                'color': 'blue',
                'id': flower.pk
            }
            request = self.factory.post(data=post_data)

            self.view(request)

            changed_flower = utils.refresh(flower)
            self.assertEqual('blue', changed_flower.color)

Below there is an example of Django REST Framework authentication mocking. Pay attantion to ``djet.restframework.APIViewTestCase`` base class and ``user`` parameter in request factory call.

.. code:: python

    from django.contrib.auth import get_user_model
    from djet import assertions, utils, restframework
    import views

    class SetUsernameViewTest(restframework.APIViewTestCase,
                              assertions.StatusCodeAssertionsMixin):
        view_class = views.SetUsernameView
  
        def test_post_should_set_new_username(self):
            password = 'secret'
            user = get_user_model().objects.create_user(username='john', password=password)
            data = {
                'new_username': 'ringo',
                'current_password': password,
            }
            request = self.factory.post(user=user, data=data)
    
            response = self.view(request)
    
            self.assert_status_equal(response, status.HTTP_200_OK)
            user = utils.refresh(user)
            self.assertEqual(data['new_username'], user.username)

For more comprehensive examples we really recommend to `check out how djoser library tests are crafted <https://github.com/sunscrapers/djoser/blob/master/testproject/testapp/tests.py>`__.

Development
===========

To start developing on **djet**, clone the repository:

``$ git clone git@github.com:sunscrapers/djet.git``

In order to run the tests create virtualenv, go to repo directory and then:

``$ pip install django``

``$ pip install -r requirements.txt``

``$ cd testproject``

``$ ./manage.py test``

``$ tox``

.. |Build Status| image:: https://travis-ci.org/sunscrapers/djet.png
   :target: https://travis-ci.org/sunscrapers/djet

.. |Coverage| image:: https://coveralls.io/repos/sunscrapers/djet/badge.png?branch=master
   :target: https://coveralls.io/r/sunscrapers/djet?branch=master
