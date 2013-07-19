import types
from django.core.handlers.wsgi import WSGIRequest
from django import test as django_test
from django.views import generic
import viewtestcase


class MockMiddleware(object):

    def process_request(self, request):
        request.middleware_was_here = True


class RequestFactoryTest(django_test.TestCase):

    def setUp(self):
        self.factory = viewtestcase.RequestFactory()

    def test_create_request_should_return_request(self):
        request = self.factory.create_request(self.factory.Method.GET)

        self.assertIsInstance(request, WSGIRequest)

    def test_create_request_should_return_request_processes_by_middleware(self):
        request = self.factory.create_request(
            self.factory.Method.GET,
            middleware_classes=[
                MockMiddleware,
            ]
        )

        self.assertTrue(request.middleware_was_here)


class MockView(generic.View):
    pass


class ViewTestCaseTest(viewtestcase.ViewTestCase):
    view_class = MockView
    middleware_classes = [MockMiddleware]

    def test_init_should_create_view_method_when_view_class_provided(self):
        self.assertIsInstance(self.view, types.FunctionType)

    def test_init_should_create_factory_instance_with_middleware_classes(self):
        self.assertIsInstance(self.factory, viewtestcase.RequestFactory)
        self.assertIn(MockMiddleware, self.factory.middleware_classes)

    def test_assert_not_redirect_should_pass_when_view_not_redirect(self):
        request = self.factory.create_request(self.factory.Method.GET)

        response = self.view(request)

        self.assert_not_redirect(response)

    def test_assert_redirect_should_pass_when_view_redirect(self):
        view = generic.RedirectView.as_view(url='/')
        request = self.factory.create_request(self.factory.Method.GET)

        response = view(request)

        self.assert_redirect(response)
