import os
from django.test.testcases import TestCase
from djet import files


class InMemoryFilesTestCase(TestCase):

    def test_make_inmemory_file_should_pass(self):
        file = files.make_inmemory_file('test.txt', 'Avada Kedavra')

        self.assertEqual(file.name, 'test.txt')
        self.assertIn('Avada Kedavra', file.readlines())

    def test_make_inmemory_image_should_pass(self):
        file = files.make_inmemory_image('test.jpg', format='JPEG')

        self.assertEqual(file.name, 'test.jpg')


class InMemoryStorageTestCase(TestCase):

    def setUp(self):
        self.storage = files.InMemoryStorage()
        self.file_name = 'test.txt'
        self.file = files.make_inmemory_file(self.file_name, 'Avada Kedavra')
        self.storage.save(self.file_name, self.file)

    def test_file_should_not_be_saved_on_disk_when_saved(self):
        self.assertFalse(os.path.exists(self.file_name))

    def test_file_should_exist_when_saved(self):
        self.assertTrue(self.storage.exists(self.file_name))

    def test_file_should_be_the_same_when_opened(self):
        uploaded_file = self.storage.open(self.file_name)

        self.assertEqual(uploaded_file, self.file)
