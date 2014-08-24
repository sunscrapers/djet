import django
from rest_framework import test
from djet import testcases


class APIRequestFactory(testcases.RequestFactory, test.APIRequestFactory):

    def _request(self, method, **kwargs):
        request = super(APIRequestFactory, self)._request(method, **kwargs)
        user = kwargs.get('user')
        token = kwargs.get('token')
        test.force_authenticate(request, user, token)
        return request


class APIViewTransactionTestCase(testcases.ViewTransactionTestCase):
    factory_class = APIRequestFactory


class APIViewTestCase(testcases.ViewTestCase):
    factory_class = APIRequestFactory


if django.VERSION >= (1, 4):
    class APIViewLiveServerTestCase(testcases.ViewLiveServerTestCase):
        factory_class = APIRequestFactory

if django.VERSION >= (1, 5):
    class APIViewSimpleTestCase(testcases.ViewSimpleTestCase):
        factory_class = APIRequestFactory
