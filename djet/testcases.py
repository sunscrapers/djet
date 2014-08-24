from functools import partial
import django
from django import test as django_test
from django.template.response import TemplateResponse


class RequestFactory(django_test.RequestFactory):

    def __init__(self, middleware_classes=None, **defaults):
        super(RequestFactory, self).__init__(**defaults)
        self.middleware_classes = middleware_classes or []
        self._override_shortcuts()

    def _override_shortcuts(self):
        for method in ('get', 'post', 'head', 'delete', 'options', 'put'):
            shortcut = partial(self._request, method)
            setattr(self, method, shortcut)

    def _request(self, method, user=None, path='', **kwargs):
        super_method = getattr(super(RequestFactory, self), method.lower())
        request = super_method(path=path, **kwargs)
        request.user = user
        return request


class MiddlewareType:
    PROCESS_REQUEST = 'process_request'
    PROCESS_VIEW = 'process_view'
    PROCESS_EXCEPTION = 'process_exception'
    PROCESS_RESPONSE = 'process_response'
    PROCESS_TEMPLATE_RESPONSE = 'process_template_response'


class ViewTestCaseMixin(object):
    view_class = None
    view_function = None
    view_kwargs = None
    factory_class = RequestFactory
    middleware_classes = None

    def _pre_setup(self, *args, **kwargs):
        super(ViewTestCaseMixin, self)._pre_setup(*args, **kwargs)
        if self.factory_class:
            self.factory = self.factory_class(self.get_middleware_classes())

    def get_view_kwargs(self):
        return self.view_kwargs or {}

    def get_middleware_classes(self):
        return self.middleware_classes or []

    def create_view_object(self, request=None, *args, **kwargs):
        view_object = self.view_class(**self.get_view_kwargs())
        view_object.request = request
        view_object.args = args
        view_object.kwargs = kwargs
        return view_object

    def view(self, request, *args, **kwargs):
        response = self._create_middlewares_processor(
            middleware_type=MiddlewareType.PROCESS_REQUEST,
            reverse=False,
            return_fast=True,
        )(request)
        if not response:
            response = self._create_middlewares_processor(
                middleware_type=MiddlewareType.PROCESS_VIEW,
                reverse=False,
                return_fast=True,
            )(request, self.view, args, kwargs)
            if not response:
                try:
                    response = self._run_view(request, args, kwargs)
                except Exception as exception:
                    response = self._create_middlewares_processor(
                        middleware_type=MiddlewareType.PROCESS_EXCEPTION,
                        reverse=True,
                        return_fast=True,
                    )(request, exception)
                    if not response:
                        raise
        if isinstance(response, TemplateResponse):
            response = self._create_middlewares_processor(
                middleware_type=MiddlewareType.PROCESS_TEMPLATE_RESPONSE,
                reverse=True,
                return_fast=False,
                start_with=response,
            )(request, response)
        response = self._create_middlewares_processor(
            middleware_type=MiddlewareType.PROCESS_RESPONSE,
            reverse=True,
            return_fast=False,
            start_with=response,
        )(request, response)
        return response

    def _run_view(self, request, args, kwargs):
        if self.view_class:
            response = self.view_class.as_view(**self.get_view_kwargs())(request, *args, **kwargs)
        elif self.view_function:
            response = self.__class__.__dict__['view_function'](request, *args, **kwargs)
        return response

    def _create_middlewares_processor(self, middleware_type, reverse, return_fast, start_with=None):
        middleware_classes = self.middleware_classes or []
        if reverse:
            middleware_classes = reversed(middleware_classes)

        def processor(*args, **kwargs):
            result = start_with
            for mw_class in middleware_classes:
                if isinstance(mw_class, tuple):
                    mw_class, mw_types = mw_class[0], mw_class[1:]
                else:
                    mw_types = None
                mw_instance = mw_class()
                if hasattr(mw_instance, middleware_type) and \
                        (not mw_types or middleware_type in mw_types):
                    result = getattr(mw_instance, middleware_type)(*args, **kwargs) or result
                    if return_fast and result:
                        break
            return result

        return processor


class ViewTransactionTestCase(ViewTestCaseMixin, django_test.TransactionTestCase):
    pass


class ViewTestCase(ViewTestCaseMixin, django_test.TestCase):
    pass


if django.VERSION >= (1, 4):
    class ViewLiveServerTestCase(ViewTestCaseMixin, django_test.LiveServerTestCase):
        pass

if django.VERSION >= (1, 5):
    class ViewSimpleTestCase(ViewTestCaseMixin, django_test.SimpleTestCase):
        pass
