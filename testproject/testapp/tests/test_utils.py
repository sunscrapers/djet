from django.test.testcases import TestCase
from django.conf import settings
from djet.util import update_settings


class TestUpdateSettings(TestCase):
    def test_update_settings(self):
        with update_settings(
            TEST_DICT={'parameter1': 'other_value'}, OTHER_DICT={'parameter3': 'value3'}
        ):
            self.assertEqual(settings.TEST_DICT['parameter1'], 'other_value')
            self.assertEqual(settings.TEST_DICT['parameter2'], 'value2')
            self.assertEqual(settings.OTHER_DICT['parameter3'], 'value3')
        self.assertEqual(settings.TEST_DICT['parameter1'], 'value1')
        with self.assertRaises(AttributeError):
            settings.OTHER_DICT
