django-viewtestcase
===================

Extended TestCase for easy unit testing of Django views.

[![Build Status](https://travis-ci.org/sunscrapers/django-viewtestcase.png)](https://travis-ci.org/sunscrapers/django-viewtestcase)

Why django-viewtestcase?
========================
Django test client in fact performs integration tests. All middlewares, resolvers, decorators and so on are in fact
tested. Just single failure in middleware can break all view tests.

[One technique](http://tech.novapost.fr/static/images/slides/djangocon-europe-2013-unit-test-class-based-views.html)
was presented at DjangoCon Europe 2013 Warsaw. Our approach used for a long time was somehow different so we wanted
to share it as an alternative.

**django-viewtestcase** makes it easier to make better unit tests for your views. Instead of `self.client` you will use
`self.factory` which is an extended `RequestFactory` with useful shortcuts for creating requests. There are also some
additional assertions like `assert_redirect` in ViewTestCase.

Sometimes middlewares are required for view to test it, so there is an option to specify which middlewares
should be used in a single test or whole test case by giving `middleware_classes` argument.

Examples
========

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

If you want to test function-based view you should do it like this (we know it is not pretty, but you can probably
live it with for now):
```python
class YourFunctionViewTest(viewtestcase.ViewTestCase):
    view = staticmethod(tested_view_function)
```

There is no special method for testing single view methods, because it is really easy to do something like:
```python
class YourViewObjectMethodTest(viewtestcase.ViewTestCase):
    view_class = YourView

    def test_test_some_view_method(self):
        view_object = self.view_class()

        view_object.some_method()

        self.assertTrue(view_object.some_method_called)
```