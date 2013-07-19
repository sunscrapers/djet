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
        data = {
            'next': '/'
        }
        request = self.factory.create_request(
            method=self.factory.Method.POST,
            data=data,
        )

        response = self.view(request)

        self.assert_redirect(response, data['next'])
        self.assertIn(
            Message(level=level, message=message),
            messages.get_messages(request),
        )
```
