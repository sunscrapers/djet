from django.contrib import messages
from django.contrib.messages.storage.base import Message
from django.core import mail
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect


class StatusCodeAssertionsMixin(object):
    redirect_codes = [
        HttpResponseRedirect.status_code,
        HttpResponsePermanentRedirect.status_code
    ]

    def assert_status_equal(self, response, status_code):
        self.assertEqual(
            response.status_code,
            status_code,
            'Response status code is {0}, expected {1}'.format(
                response.status_code,
                status_code,
            )
        )

    def assert_status_in(self, response, status_codes):
        self.assertIn(
            response.status_code,
            status_codes,
            'Response status code is {0}, expected one of: {1}'.format(
                response.status_code,
                ', '.join(str(code) for code in status_codes),
            )
        )

    def _get_redirect_assertion_message(self, response):
        return 'Response should redirect, but status code is {0}'.format(
            response.status_code
        )

    def assert_redirect(self, response, expected_url=None):
        """
        assertRedirects from Django TestCase follows the redirects chains,
        this assertion does not - which is more like real unit testing
        """
        self.assertIn(
            response.status_code,
            self.redirect_codes,
            self._get_redirect_assertion_message(response),
        )
        if expected_url:
            location_header = response._headers.get('location', None)
            self.assertEqual(
                location_header,
                ('Location', str(expected_url)),
                'Response should redirect to {0}, but it redirects to {1} instead'.format(
                    expected_url,
                    location_header[1],
                )
            )

    def assert_not_redirect(self, response):
        self.assertNotIn(
            response.status_code,
            self.redirect_codes,
            self._get_redirect_assertion_message(response)
        )


class EmailAssertionsMixin(object):
    def assert_emails_in_mailbox(self, count):
        self.assertEqual(
            len(mail.outbox),
            count,
            'There is {0} e-mails in mailbox, expected {1}'.format(
                len(mail.outbox),
                count,
            )
        )

    def _is_email_matching_criteria(self, email, **kwargs):
        for key, value in kwargs.items():
            if getattr(email, key) != value:
                return False
        return True

    def assert_email(self, email, **kwargs):
        for key, value in kwargs.items():
            self.assertEqual(
                getattr(email, key),
                value,
                'Email does not match criteria, expected {0} to be {1} but it is {2}'.format(
                    key,
                    value,
                    getattr(email, key),
                )
            )

    def assert_email_exists(self, **kwargs):
        for email in mail.outbox:
            if self._is_email_matching_criteria(email, **kwargs):
                return
        raise AssertionError('Email matching criteria was not sent')


class MessagesAssertionsMixin(object):
    def assert_messages_sent(self, request, count):
        sent = len(messages.get_messages(request))
        self.assertEqual(
            sent,
            count,
            'There was {0} messages sent, expected {1}.'.format(
                sent,
                count,
            )
        )

    def assert_message_exists(self, request, level, message):
        self.assertIn(
            Message(level=level, message=message),
            messages.get_messages(request),
            'Message matching criteria does not exist'
        )