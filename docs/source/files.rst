Files
=====

An example of test using all files goodies from **djet**:

.. code-block:: python

    from djet import files
    from django.core.files.storage import default_storage
    from django.test.testcases import TestCase

    class YourFilesTests(files.InMemoryStorageMixin, TestCase):

        def test_creating_file(self):
            created_file = files.create_inmemory_file('file.txt', 'Avada Kedavra')

            default_storage.save('file.txt', created_file)

            self.assertTrue(default_storage.exists('file.txt'))
