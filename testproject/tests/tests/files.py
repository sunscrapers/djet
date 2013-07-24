import os
from django.core.files.storage import default_storage
from django.test.testcases import TestCase
from django.test.utils import override_settings
from djet import files


class InMemoryFilesTestCase(TestCase):

    def test_make_inmemory_file_should_pass(self):
        file = files.make_inmemory_file('test.txt', 'Avada Kedavra')

        self.assertEqual(file.name, 'test.txt')
        self.assertIn('Avada Kedavra', file.readlines())

    def test_make_inmemory_image_should_pass(self):
        file = files.make_inmemory_image('test.jpg', format='JPEG')

        self.assertEqual(file.name, 'test.jpg')


@override_settings(DEFAULT_FILE_STORAGE='djet.files.InMemoryStorage')
class InMemoryStorageTestCase(TestCase):

    def setUp(self):
        self.file_name = 'test.txt'
        self.file = files.make_inmemory_file(self.file_name, 'Avada Kedavra')
        default_storage.save(self.file_name, self.file)

    def test_file_should_not_be_saved_on_disk_when_saved(self):
        self.assertFalse(os.path.exists(self.file_name))

    def test_file_should_exist_when_saved(self):
        self.assertTrue(default_storage.exists(self.file_name))

    def test_file_should_be_the_same_when_opened(self):
        uploaded_file = default_storage.open(self.file_name)

        self.assertEqual(uploaded_file, self.file)
