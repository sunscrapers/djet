import django
from django.core.handlers.wsgi import WSGIRequest
from django import test as django_test
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views import generic
from djet import testcases


class MockMiddleware(object):

    def process_request(self, request):
        request.process_request_was_here = True

    def process_response(self, request, response):
        response.process_response_was_here = True
        return response

    def process_template_response(self, request, response):
        response.process_template_response_was_here = True
        return response

    def process_exception(self, request, exception):
        respone = HttpResponse()
        respone.process_exception_was_here = True
        return respone


class NewStyleMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.new_middleware = True
        return response


class ProcessViewMockMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        response = HttpResponse()
        response.process_view_was_here = True
        return response


class RequestFactoryTest(django_test.TestCase):

    def setUp(self):
        self.factory = testcases.RequestFactory()

    def test_create_request_should_return_request(self):
        request = self.factory.get()

        self.assertIsInstance(request, WSGIRequest)

    def test_init_should_create_shortcuts(self):
        request = self.factory.get()

        self.assertEqual(request.method, 'GET')

    def test_create_patch_request_factory(self):
        request = self.factory.patch()

        self.assertEqual(request.method, 'PATCH')


class MockView(generic.View):

    def mock_method(self):
        self.mock_method_called = True


class KwargsMockView(generic.View):
    test = None

    def get(self, *args, **kwargs):
        return self.test


class RaiseExceptionMockView(generic.View):

    def get(self, *args, **kwargs):
        raise Exception()


class TemplateResponseMockView(generic.View):

    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, 'template.html')


def mock_function_view(request):
    return HttpResponse(status=200)


class ViewTestCaseTestMixin(object):
    view_class = MockView
    middleware_classes = [MockMiddleware]

    def test_init_should_create_factory_instance_with_middleware_classes(self):
        self.assertIsInstance(self.factory, testcases.RequestFactory)
        self.assertIn(MockMiddleware, self.factory.middleware_classes)

    def test_creating_view_object(self):
        view_object = self.view_class()

        view_object.mock_method()

        self.assertTrue(view_object.mock_method_called)

    def test_view_object_should_have_request_and_arguments(self):
        request = 'request'
        args = ('a', 'b')
        kwargs = {'c': 'c'}

        view_object = self.create_view_object(request, *args, **kwargs)

        self.assertEqual(view_object.request, 'request')
        self.assertEqual(view_object.args, args)
        self.assertEqual(view_object.kwargs, kwargs)

    def test_view_should_processes_request_by_middleware(self):
        request = self.factory.get()

        self.view(request)

        self.assertTrue(request.process_request_was_here)

    def test_view_should_processes_response_by_middleware(self):
        request = self.factory.get()

        response = self.view(request)

        self.assertTrue(response.process_response_was_here)


class ViewTestCaseTest(ViewTestCaseTestMixin, testcases.ViewTestCase):
    pass


class ViewTransactionTestCaseTest(ViewTestCaseTestMixin, testcases.ViewTransactionTestCase):
    pass

if django.VERSION >= (1, 4):
    class ViewLiveServerTestCaseTest(ViewTestCaseTestMixin, testcases.ViewLiveServerTestCase):
        pass

if django.VERSION >= (1, 5):
    class ViewSimpleTestCaseTest(ViewTestCaseTestMixin, testcases.ViewSimpleTestCase):
        pass


class ProcessExceptionMiddlewareViewTestCaseTest(testcases.ViewTestCase):
    view_class = RaiseExceptionMockView
    middleware_classes = [MockMiddleware]

    def test_view_should_processes_exception_by_middleware(self):
        request = self.factory.get()

        response = self.view(request)

        self.assertTrue(response.process_exception_was_here)


class ProcessViewMiddlewareViewTestCaseTest(testcases.ViewTestCase):
    view_class = MockView
    middleware_classes = [ProcessViewMockMiddleware]

    def test_view_should_processes_exception_by_middleware(self):
        request = self.factory.get()

        response = self.view(request)

        self.assertTrue(response.process_view_was_here)


class ProcessTemplateResponseMiddlewareViewTestCaseTest(testcases.ViewTestCase):
    view_class = TemplateResponseMockView
    middleware_classes = [MockMiddleware]

    def test_view_should_processes_exception_by_middleware(self):
        request = self.factory.get()

        response = self.view(request)

        self.assertTrue(response.process_template_response_was_here)


class ProcessOnlyIndicatedMiddlewaresViewTestCaseTest(testcases.ViewTestCase):
    view_class = RaiseExceptionMockView
    middleware_classes = [(MockMiddleware, testcases.MiddlewareType.PROCESS_REQUEST)]

    def test_view_should_not_processes_exception_by_middleware(self):
        request = self.factory.get()

        with self.assertRaises(Exception):
            self.view(request)


class KwargsViewTestCaseTest(testcases.ViewTestCase):
    view_class = KwargsMockView
    view_kwargs = {'test': 'test'}

    def test_view_should_have_kwargs_when_view_kwargs_specified(self):
        request = self.factory.get()

        response = self.view(request)

        self.assertEqual(response, 'test')

    def test_view_object_should_have_kwargs_when_view_kwargs_specified(self):
        view_object = self.create_view_object()

        self.assertEqual(view_object.test, 'test')


class ViewTestCaseFunctionViewTest(testcases.ViewTestCase):
    view_function = mock_function_view

    def test_assert_response_when_function_view_used(self):
        request = self.factory.get()

        response = self.view(request)

        self.assertEqual(response.status_code, 200)


class NewStyleMiddlewareTest(testcases.ViewTestCase):
    view_class = MockView
    middleware = [NewStyleMiddleware]

    def test_new_middleware(self):
        request = self.factory.get()

        try:
            response = self.view(request)
        except NotImplementedError:
            if django.VERSION >= (1, 10):
                assert True

        if django.VERSION >= (1, 10):
            self.assertTrue(response.new_middleware)


class NoViewClassDefined(testcases.ViewTestCase):
    def test_no_view_class_defined_raises_exception(self):
        request = self.factory.get()

        with self.assertRaises(Exception):
            self.view(request)



