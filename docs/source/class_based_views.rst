Class Based Views
=================

If you want to test class-based view you should do it like this:

.. code-block:: python

    from djet import testcases

    from fooapp.views import foo_view

    class FooViewTest(testcases.ViewTestCase):
        view_class = foo_view

        def test_foo_view_get(self):
            request = self.factory.get()
            # assertions for request

            response = self.view(request)
            # assertions for response

There is special ``create_view_object`` helper for testing single view methods,
which applies the view_kwargs specified to created view object.
You can also provide request, args and kwargs here and they will be bounded to view,
like it normally happens in dispatch method.

You can always create view object with different kwargs by using
``self.view_class`` constructor.

.. code-block:: python

    class YourViewObjectMethodTest(testcases.ViewTestCase):
        view_class = YourView
        view_kwargs = {'redirect_url': '/'}

        def test_some_view_method(self):
            request = self.factory.get()
            view_object = self.create_view_object(request, 'some arg', pk=1)

            view_object.some_method()

            self.assertTrue(view_object.some_method_called)