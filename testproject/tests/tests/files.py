import os
from django.core.files.storage import default_storage
from django.test.testcases import TestCase
from django.utils import unittest
from djet import files
try:
    import PIL
except ImportError:
    PIL = None


class InMemoryFilesTestCase(TestCase):

    def test_make_inmemory_file_should_pass(self):
        file = files.create_inmemory_file('test.txt', 'Avada Kedavra')

        self.assertEqual(file.name, 'test.txt')
        self.assertIn('Avada Kedavra', file.readlines())

    @unittest.skipUnless(PIL, 'PIL is not installed')
    def test_make_inmemory_image_should_pass(self):
        file = files.create_inmemory_image('test.jpg', format='JPEG')

        self.assertEqual(file.name, 'test.jpg')


class InMemoryStorageTestCase(files.InMemoryStorageMixin, TestCase):

    def setUp(self):
        self.file_name = 'test.txt'
        self.file = files.create_inmemory_file(self.file_name, 'Avada Kedavra')
        default_storage.save(self.file_name, self.file)

    def test_aaa_just_saving_file(self):
        default_storage.save('cross.txt', files.create_inmemory_file('aa.txt'))

        self.assertTrue(default_storage.exists('cross.txt'))

    def test_bbb_saved_file_should_not_exist_in_another_test(self):
        self.assertFalse(default_storage.exists('cross.txt'))

    def test_file_should_not_be_saved_on_disk_when_saved(self):
        self.assertFalse(os.path.exists(self.file_name))

    def test_file_should_exist_when_saved(self):
        self.assertTrue(default_storage.exists(self.file_name))

    def test_file_should_be_the_same_when_opened(self):
        uploaded_file = default_storage.open(self.file_name)

        self.assertEqual(uploaded_file, self.file)
