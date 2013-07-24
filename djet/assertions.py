from django.contrib import messages
from django.contrib.messages.storage.base import Message
from django.core import mail
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


class EmailAssertionsMixin(object):

    def assert_emails_in_mailbox(self, count):
        self.assertEqual(len(mail.outbox), count,
                         'There is {0} e-mails in mailbox, expected {1}.'.format(len(mail.outbox), count))

    def _is_email_matching_criteria(self, email, **kwargs):
        for key, value in kwargs.items():
            if getattr(email, key) != value:
                return False
        return True

    def assert_email(self, email, **kwargs):
        for key, value in kwargs.items():
            self.assertEqual(getattr(email, key), value)

    def assert_email_exists(self, **kwargs):
        for email in mail.outbox:
            if self._is_email_matching_criteria(email, **kwargs):
                return
        raise AssertionError('Email matching criteria was not sent')


class MessagesAssertionsMixin(object):

    def assert_messages_sent(self, request, count):
        sent = len(messages.get_messages(request))
        self.assertEqual(sent, count, 'There was {0} messages sent, expected {1}.'.format(sent, count))

    def assert_message_exists(self, request, level, message):
        self.assertIn(
                Message(level=level, message=message),
                messages.get_messages(request),
            )