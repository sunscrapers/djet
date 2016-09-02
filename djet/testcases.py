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
    middleware = None

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
        self.args = args
        self.kwargs = kwargs
        self._load_middleware()
        if self.middleware:
            response = self._middleware_chain(request)
        else:
            response = None
            for middleware_method in self._request_middleware:
                response = middleware_method(request)
                if response:
                    break

            if response is None:
                response = self._get_response(request)

        for middleware_method in self._response_middleware:
            response = middleware_method(request, response)

        return response

    def _load_middleware(self):
        self._request_middleware = []
        self._view_middleware = []
        self._template_response_middleware = []
        self._response_middleware = []
        self._exception_middleware = []

        if self.middleware is None:
            middleware_classes = self.middleware_classes or []
            for mw_class in middleware_classes:
                if isinstance(mw_class, tuple):
                    mw_class, mw_types = mw_class[0], mw_class[1:]
                else:
                    mw_types = None
                mw_instance = mw_class()

                if self._add_middleware(mw_instance, mw_types, MiddlewareType.PROCESS_REQUEST):
                    self._request_middleware.append(mw_instance.process_request)
                if self._add_middleware(mw_instance, mw_types, MiddlewareType.PROCESS_VIEW):
                    self._view_middleware.append(mw_instance.process_view)
                if self._add_middleware(mw_instance, mw_types, MiddlewareType.PROCESS_TEMPLATE_RESPONSE):
                    self._template_response_middleware.insert(0, mw_instance.process_template_response)
                if self._add_middleware(mw_instance, mw_types, MiddlewareType.PROCESS_RESPONSE):
                    self._response_middleware.insert(0, mw_instance.process_response)
                if self._add_middleware(mw_instance, mw_types, MiddlewareType.PROCESS_EXCEPTION):
                    self._exception_middleware.insert(0, mw_instance.process_exception)
        else:
            if django.VERSION < (1, 10):
                raise NotImplementedError('New style middleware is not intended to be used with older django versions')
            from django.core.handlers.exception import convert_exception_to_response
            handler = convert_exception_to_response(self._get_response)
            middleware_classes = reversed(self.middleware or [])
            for mw_class in middleware_classes:
                if isinstance(mw_class, tuple):
                    mw_class, mw_types = mw_class[0], mw_class[1:]
                else:
                    mw_types = None
                mw_instance = mw_class(handler)

                if self._add_middleware(mw_instance, mw_types, MiddlewareType.PROCESS_VIEW):
                    self._view_middleware.insert(0, mw_instance.process_view)
                if self._add_middleware(mw_instance, mw_types, MiddlewareType.PROCESS_TEMPLATE_RESPONSE):
                    self._template_response_middleware.append(mw_instance.process_template_response)
                if self._add_middleware(mw_instance, mw_types, MiddlewareType.PROCESS_EXCEPTION):
                    self._exception_middleware.append(mw_instance.process_exception)

                handler = convert_exception_to_response(mw_instance)
            self._middleware_chain = handler

    def _get_response(self, request):
        response = None
        for middleware_method in self._view_middleware:
            response = middleware_method(request, self._run_view, self.args, self.kwargs)
            if response:
                break
        if response is None:
            try:
                response = self._run_view(request)
            except Exception as e:
                response = self._process_exception_by_middleware(e, request)
        if hasattr(response, 'render') and callable(response.render):
            for middleware_method in self._template_response_middleware:
                response = middleware_method(request, response)

        return response

    def _process_exception_by_middleware(self, exception, request):
        for middleware_method in self._exception_middleware:
            response = middleware_method(request, exception)
            if response:
                return response
        raise

    def _add_middleware(self, mw_instance, mw_types, middleware_type):
        return hasattr(mw_instance, middleware_type) and (not mw_types or middleware_type in mw_types)

    def _run_view(self, request):
        if self.view_class:
            response = self.view_class.as_view(**self.get_view_kwargs())(request, *self.args, **self.kwargs)
        elif self.view_function:
            response = self.__class__.__dict__['view_function'](request, *self.args, **self.kwargs)
        return response


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
