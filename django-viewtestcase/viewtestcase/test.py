from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponsePermanentRedirect
from django.test import TestCase
from django.test.client import RequestFactory


class ViewTestCase(TestCase):
    view_class = None
    auth_next_parameter_name = 'next'
    auth_url = settings.LOGIN_URL
    redirect_codes = [HttpResponseRedirect.status_code, HttpResponsePermanentRedirect.status_code]

    def _pre_setup(self, *args, **kwargs):
        super(ViewTestCase, self)._pre_setup(*args, **kwargs)
        if self.view_class:
            self.view = self.view_class.as_view()

    def prepare_request(self, request, user):
        if user:
            request.user = request._user = user
        request.session = FakeSession()
        request.csrf_processing_done = True
        if 'django.contrib.messages' in settings.INSTALLED_APPS:
            messages = FallbackStorage(request)
            request._messages = messages
        return request

    def create_get_request(self, *args, **kwargs):
        return self.create_request('get', *args, **kwargs)

    def create_post_request(self, *args, **kwargs):
        return self.create_request('post', *args, **kwargs)

    def create_put_request(self, *args, **kwargs):
        return self.create_request('put', *args, **kwargs)

    def create_delete_request(self, *args, **kwargs):
        return self.create_request('delete', *args, **kwargs)
    
    def create_request(self, name, data=None, user=None, path=None):
        factory = RequestFactory()
        method = getattr(factory, name)
        request = method(factory, path or '', data or {})
        return self.prepare_request(request, user)
   
    def assert_redirect(self, response, expected_url=None):
        self.assertIn(response.status_code, self.redirect_codes)
        if expected_url:
            self.assertEqual(response._headers.get('location', None), ('Location', str(expected_url)))

    def assert_not_redirect(self, response):
        self.assertNotIn(response.status_code, self.redirect_codes)

    def assert_forbidden(self, response):
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        
    def assert_login_required(self, response):
        self.assert_redirect(response,
            '{auth_url}?{next}={request_url}'.format(
                auth_url=self.auth_url,
                next=self.auth_next_parameter_name,
                request_url=response.request.get('PATH_INFO')
        ))
        

class FakeSession(dict):

    def cycle_key(self):
        pass

    def set_test_cookie(self):
        pass

    def test_cookie_worked(self):
        return True

    def delete_test_cookie(self):
        pass

    def set_expiry(self, expiry):
        self.expiry = expiry
