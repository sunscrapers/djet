Integration with DRF
====================

Below there is an example of Django REST Framework authentication mocking.
Pay attention to ``djet.restframework.APIViewTestCase`` base class and ``user``
parameter in request factory call.

.. code-block:: python

    from django.contrib.auth import get_user_model
    from djet import assertions, utils, restframework
    import views

    class SetUsernameViewTest(restframework.APIViewTestCase,
                              assertions.StatusCodeAssertionsMixin):
        view_class = views.SetUsernameView

        def test_post_should_set_new_username(self):
            password = 'secret'
            user = get_user_model().objects.create_user(username='john', password=password)
            data = {
                'new_username': 'ringo',
                'current_password': password,
            }
            request = self.factory.post(user=user, data=data)

            response = self.view(request)

            self.assert_status_equal(response, status.HTTP_200_OK)
            user.refresh_from_db()
            self.assertEqual(data['new_username'], user.username)

For more comprehensive examples we recommend to
`check out how djoser library tests are crafted <https://github.com/sunscrapers/djoser/blob/master/testproject/testapp/tests.py>`__.
