Getting started
===============

Django test client performs integration tests. All middleware classes, resolvers,
decorators and so on are tested. Just a single failure in a middleware can
break all the view tests.

`One technique <http://tech.novapost.fr/django-unit-test-your-views-en.html>`__
of performing the tests was presented at DjangoCon Europe 2013.
We, at Sunscrapers have decided to do it in slightly different way,
which is why djoser has been created.

Testing views
-------------

**djet** makes performing unit tests for your views easier by providing ``ViewTestCase``.
Instead of ``self.client``, you can use ``self.factory``, which is an
extended ``RequestFactory`` with overridden shortcuts for creating requests
(eg. ``path`` is not required parameter).

Sometimes you would need middleware to be applied in order to test the view.
There is an option that helps specify which middleware should be used in
a single test or a whole test case by applying ``middleware_classes`` argument.
This argument should be a list of middleware classes (e.g. ``SessionMiddleware``)
or tuples where first argument is middleware class and rest items are middleware
types (from ``MiddlewareType`` class). In this case only indicated middleware methods
will be call.

Assertions
----------

**djet** also provides additional assertions via mixin classes within
``djet.assertions`` module. They have been created to simplify common
testing scenarios and currently there is ``StatusCodeAssertionsMixin``,
``EmailAssertionsMixin``, ``MessagesAssertionsMixin`` and
``InstanceAssertionsMixin`` full of useful assertions.

Remember that if you want to use assertions e.g. from ``MessagesAssertionsMixin``
you must also add ``middleware_classes`` required by messages to your test case.
We do not add them for you in mixin, because we believe those mixin classes shouldn't
implicitly mess with middleware, because it would make it harder to understand
what and why exactly is happening in your tests.

Testing file uploads
--------------------

There are three primary issues, while testing file-related code in Django
and ``djet.files`` module attempts to solve all of these.

First thing - you won't need any files put somewhere next to fixtures anymore.
``create_inmemory_file`` and ``create_inmemory_image`` are ready to use.
Those helpful functions are taken from
`great blog post by Piotr Maliński <http://www.rkblog.rk.edu.pl/w/p/temporary-files-django-tests-and-fly-file-manipulation/>`__
with just a few small changes.

You can also use ``InMemoryStorage`` which deals with files being saved to disk
during tests and speed ups tests by keeping them in memory.

``InMemoryStorageMixin`` does another great thing.
It replaces ``DEFAULT_FILE_STORAGE`` with ``InMemoryStorage`` for you and also
removes all files after test ``tearDown``, so you will no longer see any files
crossing between tests. You can also provide any storage you want,
it should only implement ``clear`` method which is invoked after tearDown.
``InMemoryStorageMixin`` cannot be used with bare ``unittest.TestCase`` -
you have to use ``TestCase`` from Django or ``ViewTestCase`` from **djet**.
