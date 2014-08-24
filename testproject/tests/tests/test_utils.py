from django.test import TestCase
from djet import utils
from tests import models


class RefreshTest(TestCase):

    def test_refresh_should_update_instance_when_instance_changed(self):
        instance = models.MockModel.objects.create(field='old')

        models.MockModel.objects.filter(pk=instance.pk).update(field='new')

        instance = utils.refresh(instance)
        self.assertEqual(instance.field, 'new')
