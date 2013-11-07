from functools import partial
from django import test as django_test


class RequestFactory(django_test.RequestFactory):

    def __init__(self, middleware_classes=None, **defaults):
        super(RequestFactory, self).__init__(**defaults)
        self.middleware_classes = middleware_classes or []
        self._override_shortcuts()

    def _override_shortcuts(self):
        for method in ('get', 'post', 'head', 'delete', 'options', 'put'):
            shortcut = partial(self._request, method)
            setattr(self, method, shortcut)

    def _request(self, method, user=None, path='',
                 middleware_classes=None, **kwargs):
        super_method = getattr(super(RequestFactory, self), method.lower())
        request = super_method(path=path, **kwargs)
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
    view_function = None
    view_kwargs = None
    factory_class = RequestFactory
    middleware_classes = None

    def _pre_setup(self, *args, **kwargs):
        super(ViewTestCase, self)._pre_setup(*args, **kwargs)
        if self.view_class:
            self.view = self.view_class.as_view(**self.get_view_kwargs())
        elif self.view_function:
            self.view = self.__class__.__dict__['view_function']
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
