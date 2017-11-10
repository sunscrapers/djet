Function Based Views
====================

If you want to test function-based view you should do it like this:

.. code-block:: python

    from djet import testcases

    from fooapp.views import foo_view

    class FooViewTest(testcases.ViewTestCase):
        view_function = foo_view

        def test_foo_view_get(self):
            request = self.factory.get()
            # assertions for request

            response = self.view(request)
            # assertions for response
