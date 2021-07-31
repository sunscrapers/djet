from rest_framework import test

from djet import testcases


class APIRequestFactory(testcases.RequestFactory, test.APIRequestFactory):
    def _request(self, method, **kwargs):
        request = super(APIRequestFactory, self)._request(method, **kwargs)
        user = kwargs.get("user")
        token = kwargs.get("token")
        test.force_authenticate(request, user, token)
        return request


class APIViewTransactionTestCase(testcases.ViewTransactionTestCase):
    factory_class = APIRequestFactory


class APIViewTestCase(testcases.ViewTestCase):
    factory_class = APIRequestFactory
    viewset = None

    def _get_view(self, request):
        if self.viewset:
            actions = request.META.pop("actions")
            return self.viewset.as_view(actions=actions, **self.get_view_kwargs())
        return super(APIViewTestCase, self)._get_view(request)


class APIViewLiveServerTestCase(testcases.ViewLiveServerTestCase):
    factory_class = APIRequestFactory


class APIViewSimpleTestCase(testcases.ViewSimpleTestCase):
    factory_class = APIRequestFactory
