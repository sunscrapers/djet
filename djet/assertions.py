from django.contrib import messages
from django.contrib.messages.storage.base import Message
from django.core import mail
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect


class StatusCodeAssertionsMixin(object):
    redirect_codes = [
        HttpResponseRedirect.status_code,
        HttpResponsePermanentRedirect.status_code
    ]

    def assert_status_equal(self, response, status_code_or_response):
        status_code = self._get_status_code(status_code_or_response)
        self.assertEqual(
            response.status_code,
            status_code,
            'Response status code is {0}, expected {1}'.format(
                response.status_code,
                status_code,
            )
        )

    def assert_status_in(self, response, status_codes_or_responses):
        status_codes = list(map(self._get_status_code, status_codes_or_responses))
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

    def _get_status_code(self, status_code_or_response):
        try:
            return status_code_or_response.status_code
        except AttributeError:
            return status_code_or_response


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


class _InstanceContext(object):
    """
    Context manager returned by assert_instance_created/deleted.
    """
    def __init__(self, enter_assertion, exit_assertion, model_class, **kwargs):
        self.enter_assertion = enter_assertion
        self.exit_assertion = exit_assertion
        self.model_class = model_class
        self.kwargs = kwargs

    def __enter__(self):
        self.enter_assertion(self.model_class, **self.kwargs)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit_assertion(self.model_class, **self.kwargs)
        return True


class InstanceAssertionsMixin(object):
    """
    ORM-related assertions for testing instance creation and deletion.
    """
    def assert_instance_exists(self, model_class, **kwargs):
        try:
            obj = model_class._default_manager.get(**kwargs)
            self.assertIsNotNone(obj)
        except model_class.DoesNotExist:
            raise AssertionError('No {0} found matching the criteria.'.format(
                    model_class.__name__,
                )
            )

    def assert_instance_does_not_exist(self, model_class, **kwargs):
        try:
            instance = model_class._default_manager.get(**kwargs)
            raise AssertionError('A {0} was found matching the criteria. ({1})'.format(
                model_class.__name__,
                instance,
            ))
        except model_class.DoesNotExist:
            pass

    def assert_instance_created(self, model_class, **kwargs):
        """
        Checks if a model instance was created in the database.

        For example::

        >>> with self.assert_instance_created(Article, slug='lorem-ipsum'):
        ...     Article.objects.create(slug='lorem-ipsum')
        """
        return _InstanceContext(
            self.assert_instance_does_not_exist,
            self.assert_instance_exists,
            model_class,
            **kwargs
        )

    def assert_instance_deleted(self, model_class, **kwargs):
        """
        Checks if the model instance was deleted from the database.

        For example::

        >>> with self.assert_instance_deleted(Article, slug='lorem-ipsum'):
        ...     Article.objects.get(slug='lorem-ipsum').delete()
        """
        return _InstanceContext(
            self.assert_instance_exists,
            self.assert_instance_does_not_exist,
            model_class,
            **kwargs
        )


class CompleteAssertionsMixin(
    StatusCodeAssertionsMixin,
    EmailAssertionsMixin,
    MessagesAssertionsMixin,
    InstanceAssertionsMixin,
):
    pass
