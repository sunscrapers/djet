from django.test import TestCase
from testapp import models


class RefreshTest(TestCase):

    def test_refresh_should_update_instance_when_instance_changed(self):
        instance = models.MockModel.objects.create(field='old')

        models.MockModel.objects.filter(pk=instance.pk).update(field='new')

        instance.refresh_from_db()
        self.assertEqual(instance.field, 'new')
