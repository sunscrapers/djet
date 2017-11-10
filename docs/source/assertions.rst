We encourage you to import whole djet modules, not classes.

.. code-block:: python

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

You can also make assertions about the lifetime of model instances.
The ``assert_instance_created`` and ``assert_instance_deleted`` methods of
``InstanceAssertionsMixin`` can be used as context managers. They ensure
that the code inside the ``with`` statement resulted in either creating
or deleting a model instance.

.. code-block:: python

    from django.test import TestCase
    from djet import assertions
    from yourapp.models import YourModel

    class YourModelTest(assertions.InstanceAssertionsMixin, TestCase):

        def test_model_instance_is_created(self):
            with self.assert_instance_created(YourModel, field='value'):
                YourModel.objects.create(field='value')
