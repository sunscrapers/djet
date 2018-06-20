from django import test as django_test
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from rest_framework import generics, authentication, permissions, status, serializers
from rest_framework import viewsets
from rest_framework.response import Response as RestFrameworkResponse
from djet import assertions, files, restframework as djet_restframework

from testapp import models


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


class MockModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MockModel
        fields = ('field',)


class MockFileModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MockFileModel
        fields = ('field', 'file')


class MockViewSet(viewsets.ViewSet):
    def list(self, request):
        return RestFrameworkResponse('test')

    def retrieve(self, request, pk=None):
        return RestFrameworkResponse('test {}'.format(pk))


class RetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = models.MockModel.objects.all()
    serializer_class = MockModelSerializer


class LoginRequiredRetrieveAPIView(generics.RetrieveAPIView):
    queryset = models.MockModel.objects.all()
    serializer_class = MockModelSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class CreateAPIView(generics.CreateAPIView):
    queryset = models.MockModel.objects.all()
    serializer_class = MockModelSerializer


class MockFileModelCreateAPIView(generics.CreateAPIView):
    queryset = models.MockFileModel.objects.all()
    serializer_class = MockFileModelSerializer


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
        instance.refresh_from_db()
        self.assertEqual(instance.field, data['field'])


class CreateAPIViewTestCaseTest(assertions.StatusCodeAssertionsMixin, djet_restframework.APIViewTestCase):
    view_class = CreateAPIView

    def test_post_should_create_model(self):
        data = {
            'field': 'test value',
        }
        request = self.factory.post(data=data, format='json')

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)


class LoginRequiredRetrieveAPIViewCaseTest(assertions.StatusCodeAssertionsMixin, djet_restframework.APIViewTestCase):
    view_class = LoginRequiredRetrieveAPIView

    def test_get_should_return_json(self):
        user = User.objects.create_user(username='test_user', email='test@example.com')
        instance = models.MockModel.objects.create(field='test')
        request = self.factory.get(user=user)

        response = self.view(request, pk=instance.pk)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue('field' in response.data)


class MockFileModelCreateAPIViewTestCaseTest(
    assertions.StatusCodeAssertionsMixin,
    files.InMemoryStorageMixin,
    djet_restframework.APIViewTestCase
):
    view_class = MockFileModelCreateAPIView

    def test_post_should_create_model(self):
        data = {
            'field': 'test value',
            'file': files.create_inmemory_file('test.txt', content=b'Hello multipart!'),
        }
        request = self.factory.post(data=data, format='multipart')

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)


class TestAPIViewTestCase(djet_restframework.APIViewTestCase):
    viewset = MockViewSet

    def test_list(self):
        request = self.factory.get(actions={'get': 'list'})
        response = self.view(request)

        self.assertEqual(response.data, 'test')

    def test_detail(self):
        request = self.factory.get(actions={'get': 'retrieve'})

        pk = 1
        response = self.view(request, pk=pk)

        self.assertEqual(response.data, 'test {}'.format(pk))
