django-viewtestcase
===================

Extended TestCase for easy unit testing of Django views.

|Build Status|

Installation
============

To install **django-viewtestcase** use PyPI:

``$ pip install django-viewtestcase``

Why django-viewtestcase?
========================

Django test client performs integration tests. All middlewares, resolvers, decorators and so on are tested.
Just a single failure in a middleware can break all the view tests.

`One technique <http://tech.novapost.fr/static/images/slides/djangocon-europe-2013-unit-test-class-based-views.html>`__
of performing the tests was presented at DjangoCon Europe 2013 Warsaw. We have always used a slightly different method,
which we would like to present as an alternative to the DjangoCon approach.

**django-viewtestcase** makes performing unit tests for your views easier.
Instead of ``self.client`` you will use ``self.factory`` which is an extended RequestFactory
with with overridden shortcuts for creating requests (eg. ``path`` is not required parameter).
There are also some additional assertions like ``assert_redirect`` in ``ViewTestCase``.

Sometimes you would need middlewares to be applied in order to test the view. there is an option that helps
specify which middlewares should be used in a single test or a whole test case by applying
``middleware_classes`` argument.

Developed by `SUNSCRAPERS <http://sunscrapers.com>`__ with passion & patience.

Examples
========

.. code:: python

    import viewtestcase
    from django.contrib import messages
    from django.contrib.messages.storage.base import Message
    from django.contrib.messages.middleware import MessageMiddleware
    from django.contrib.sessions.middleware import SessionMiddleware
    from yourapp.views import YourView

    class YourViewTest(viewtestcase.ViewTestCase):
        view_class = YourView
        middleware_classes = [
            SessionMiddleware,
            MessageMiddleware,
        ]

        def test_post_should_redirect_and_add_message_when_next_parameter(self):
            request = self.factory.post(data={'next': '/'})

            response = self.view(request)

            self.assert_redirect(response, '/')
            self.assertIn(
                Message(level=messages.SUCCESS, message='Success!'),
                messages.get_messages(request),
            )

If you want to test function-based view you should do it like this:

.. code:: python

    class YourFunctionViewTest(viewtestcase.ViewTestCase):
        view_function = your_view

There is no special method for testing single view methods, because it
is really easy to do something like:

.. code:: python

    class YourViewObjectMethodTest(viewtestcase.ViewTestCase):
        view_class = YourView

        def test_test_some_view_method(self):
            view_object = self.view_class()

            view_object.some_method()

            self.assertTrue(view_object.some_method_called)



.. |Build Status| image:: https://travis-ci.org/sunscrapers/django-viewtestcase.png
   :target: https://travis-ci.org/sunscrapers/django-viewtestcase
