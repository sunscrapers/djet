from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.http import HttpResponse
from django.views import generic
from djet import assertions, testcases


class MockView(generic.View):

    def get(self, *args, **kwargs):
        return HttpResponse()


class StatusCodeAssertionsMixinTest(assertions.StatusCodeAssertionsMixin, testcases.ViewTestCase):
    view_class = MockView

    def test_assert_not_redirect_should_pass_when_view_not_redirect(self):
        request = self.factory.get()

        response = self.view(request)

        self.assert_not_redirect(response)

    def test_assert_redirect_should_pass_when_view_redirect(self):
        view = generic.RedirectView.as_view(url='/')
        request = self.factory.get()

        response = view(request)

        self.assert_redirect(response)

    def test_assert_status_code_should_pass_when_code_is_200(self):
        request = self.factory.get()

        response = self.view(request)

        self.assert_status_equal(response, 200)
        self.assert_status_in(response, [200, 201, 202])

    def test_assert_status_code_should_pass_when_responses_have_equal_codes(self):
        request = self.factory.get()

        response = self.view(request)

        self.assert_status_equal(response, HttpResponse)
        self.assert_status_in(response, [HttpResponse])

    def test_assert_status_code_should_raise_assertion_error_when_code_is_not_200(self):
        request = self.factory.get()

        response = self.view(request)

        with self.assertRaises(AssertionError):
            self.assert_status_equal(response, 400)
        with self.assertRaises(AssertionError):
            self.assert_status_in(response, [401, 404])


class EmailMockView(generic.View):

    def get(self, *args, **kwargs):
        for _ in range(int(self.request.GET.get('send'))):
            mail.send_mail('test', 'tasty test', 'glados@aperture.edu', ['you@testingchamber.com'])
        return HttpResponse()


class EmailAssertionsMixinTest(assertions.EmailAssertionsMixin, testcases.ViewTestCase):
    view_class = EmailMockView

    def test_assert_no_email_sent_when_not_sent(self):
        request = self.factory.get(data={'send': '0'})

        self.view(request)

        with self.assertRaises(AssertionError):
            self.assert_emails_in_mailbox(3)

    def test_assert_email_sent_when_really_sent(self):
        request = self.factory.get(data={'send': '3'})

        self.view(request)

        self.assert_emails_in_mailbox(3)

    def test_assert_email_exists_raising_assertion_error_when_no_matching_email(self):
        request = self.factory.get(data={'send': '1'})

        self.view(request)

        with self.assertRaises(AssertionError):
            self.assert_email_exists(subject='toast')

    def test_assert_email_exists_passes_when_matched_email(self):
        request = self.factory.get(data={'send': '1'})

        self.view(request)

        self.assert_email_exists(subject='test')


class MessagesMockView(generic.View):

    def get(self, *args, **kwargs):
        for _ in range(int(self.request.GET.get('send'))):
            messages.success(self.request, 'asap urgent')
        return HttpResponse()


class MessagesAssertionsMixin(assertions.MessagesAssertionsMixin, testcases.ViewTestCase):
    view_class = MessagesMockView
    middleware_classes = [
        SessionMiddleware,
        MessageMiddleware,
    ]

    def test_assert_messages_sent_when_not_sent(self):
        request = self.factory.get(data={'send': '0'})

        self.view(request)

        with self.assertRaises(AssertionError):
            self.assert_messages_sent(request, 3)

    def test_assert_messages_sent_when_really_sent(self):
        request = self.factory.get(data={'send': '3'})

        self.view(request)

        self.assert_messages_sent(request, 3)

    def test_assert_messages_raise_assertion_error_when_no_matching_message(self):
        request = self.factory.get(data={'send': '0'})

        self.view(request)

        with self.assertRaises(AssertionError):
            self.assert_message_exists(request, messages.SUCCESS, 'asap urgent')

    def test_assert_messages_passes_when_matched_message(self):
        request = self.factory.get(data={'send': '1'})

        self.view(request)

        self.assert_message_exists(request, messages.SUCCESS, 'asap urgent')
