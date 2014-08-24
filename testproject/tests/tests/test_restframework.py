from django import test as django_test
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from rest_framework import generics, authentication, permissions, status
from tests import models
from djet import assertions, utils, restframework as djet_restframework


class APIRequestFactoryTest(django_test.TestCase):

    def setUp(self):
        self.factory = djet_restframework.APIRequestFactory()

    def test_create_request_should_return_request(self):
        request = self.factory.get()

        self.assertIsInstance(request, WSGIRequest)

    def test_init_should_create_shortcuts(self):
        request = self.factory.get()

        self.assertEqual(request.method, 'GET')

    def test_create_request_with_user_should_force_authenticate_user(self):
        user_mock = User.objects.create_user(username='test_user', email='test@example.com')

        request = self.factory.get(user=user_mock)

        self.assertEqual(request.user, user_mock)
        self.assertEqual(request._force_auth_user, user_mock)


class RetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    model = models.MockModel


class LoginRequiredRetrieveAPIView(generics.RetrieveAPIView):
    model = models.MockModel
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class CreateAPIView(generics.CreateAPIView):
    model = models.MockModel


class RetrieveUpdateAPIViewTestCaseTest(assertions.StatusCodeAssertionsMixin, djet_restframework.APIViewTestCase):
    view_class = RetrieveUpdateAPIView

    def test_get_should_return_json(self):
        instance = models.MockModel.objects.create(field='test')
        request = self.factory.get()

        response = self.view(request, pk=instance.pk)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue('field' in response.data)

    def test_put_should_update_model(self):
        instance = models.MockModel.objects.create(field='test value')
        data = {
            'field': 'test new value',
        }
        request = self.factory.put(data=data)

        response = self.view(request, pk=instance.pk)

        self.assert_status_equal(response, status.HTTP_200_OK)
        instance = utils.refresh(instance)
        self.assertEqual(instance.field, data['field'])


class LoginRequiredRetrieveAPIViewCaseTest(assertions.StatusCodeAssertionsMixin, djet_restframework.APIViewTestCase):
    view_class = LoginRequiredRetrieveAPIView

    def test_get_should_return_json(self):
        user = User.objects.create_user(username='test_user', email='test@example.com')
        instance = models.MockModel.objects.create(field='test')
        request = self.factory.get(user=user)

        response = self.view(request, pk=instance.pk)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue('field' in response.data)


class CreateAPIViewTestCaseTest(assertions.StatusCodeAssertionsMixin, djet_restframework.APIViewTestCase):
    view_class = CreateAPIView

    def test_post_should_create_model(self):
        data = {
            'field': 'test value',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)

