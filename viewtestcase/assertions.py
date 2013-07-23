from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect


class RedirectsAssertionsMixin(object):
    redirect_codes = [
        HttpResponseRedirect.status_code,
        HttpResponsePermanentRedirect.status_code
    ]

    def assert_redirect(self, response, expected_url=None):
        self.assertIn(response.status_code, self.redirect_codes)
        if expected_url:
            self.assertEqual(
                response._headers.get('location', None),
                ('Location', str(expected_url)),
            )

    def assert_not_redirect(self, response):
        self.assertNotIn(response.status_code, self.redirect_codes)
