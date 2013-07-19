from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django import test as django_test


class RequestFactory(django_test.RequestFactory):

    class Method:
        GET = 'get'
        POST = 'post'
        HEAD = 'head'
        DELETE = 'delete'
        OPTIONS = 'options'
        PUT = 'put'

    def __init__(self, middleware_classes=None, **defaults):
        super(RequestFactory, self).__init__(**defaults)
        self.middleware_classes = middleware_classes or []

    def create_request(self, name, data=None, user=None, path='',
                       middleware_classes=None):
        method = getattr(self, name.lower())
        request = method(path, data or {})
        request.user = user
        self._process_middleware_classes(middleware_classes or [], request)
        return request

    def _process_middleware_classes(self, middleware_classes, request):
        for mw_class in self.middleware_classes + middleware_classes:
            mw_instance = mw_class()
            if hasattr(mw_instance, 'process_request'):
                mw_instance.process_request(request)


class ViewTestCase(django_test.TestCase):
    view_class = None
    factory_class = RequestFactory
    middleware_classes = None
    redirect_codes = [
        HttpResponseRedirect.status_code,
        HttpResponsePermanentRedirect.status_code
    ]

    def _pre_setup(self, *args, **kwargs):
        super(ViewTestCase, self)._pre_setup(*args, **kwargs)
        if self.view_class:
            self.view = self.view_class.as_view()
        if self.factory_class:
            self.factory = self.factory_class(self.middleware_classes)

    def assert_redirect(self, response, expected_url=None):
        self.assertIn(response.status_code, self.redirect_codes)
        if expected_url:
            self.assertEqual(
                response._headers.get('location', None),
                ('Location', str(expected_url)),
            )

    def assert_not_redirect(self, response):
        self.assertNotIn(response.status_code, self.redirect_codes)
