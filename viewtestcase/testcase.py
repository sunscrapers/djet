from functools import partial
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django import test as django_test


class RequestFactory(django_test.RequestFactory):

    class Method:
        ALL = GET, POST, HEAD, DELETE, OPTIONS, PUT = (
            'get',
            'post',
            'head',
            'delete',
            'options',
            'put',
        )

    def __init__(self, middleware_classes=None, **defaults):
        super(RequestFactory, self).__init__(**defaults)
        self.middleware_classes = middleware_classes or []
        self._initialize_shortcuts()

    def create_request(self, method, data=None, user=None, path='',
                       middleware_classes=None):
        request = getattr(self, method.lower())(path, data or {})
        request.user = user
        self._process_middleware_classes(middleware_classes or [], request)
        return request

    def _initialize_shortcuts(self):
        for method in self.Method.ALL:
            shortcut = partial(self.create_request, method)
            setattr(self, 'create_{0}_request'.format(method), shortcut)

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
