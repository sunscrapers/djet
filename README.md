django-viewtestcase
===================

TestCase extension for Django views unit testing.

Example
=======

```python
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
        request = self.factory.create_post_request(data={'next': '/'})

        response = self.view(request)

        self.assert_redirect(response, '/')
        self.assertIn(
            Message(level=messages.SUCCESS, message='Success!'),
            messages.get_messages(request),
        )
```
