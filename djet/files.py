import os
import datetime
from django.core.files.storage import Storage, default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import six


class InMemoryStorage(Storage):

    def __init__(self):
        self.files = {}

    def _open(self, name, mode):
        return self.files[name]

    def _save(self, name, content):
        self.files[name] = content
        return name

    def delete(self, name):
        del self.files[name]

    def exists(self, name):
        return name in self.files

    def listdir(self, path):
        directories, files = set(), []
        for name in self.files:
            if name.startswith(path):
                without_path = name[len(path):]
                try:
                    slash_index = without_path.index('/')
                    directories.add(without_path[:slash_index])
                except ValueError:
                    files.append(without_path)
        return list(directories), files

    def size(self, name):
        file_instance = self.files[name]
        file_instance.seek(0, 2)
        return file_instance.tell()

    def url(self, name):
        return name

    def accessed_time(self, name):
        return datetime.datetime.now()

    def created_time(self, name):
        return datetime.datetime.now()

    def modified_time(self, name):
        return datetime.datetime.now()

    def clear(self):
        self.files = {}


class InMemoryStorageMixin(object):
    storage = InMemoryStorage

    def _pre_setup(self):
        self._wrapped_storage = default_storage._wrapped
        default_storage._wrapped = self.storage()
        super(InMemoryStorageMixin, self)._pre_setup()

    def _post_teardown(self):
        super(InMemoryStorageMixin, self)._post_teardown()
        try:
            default_storage.clear()
        except AttributeError:
            pass
        default_storage._wrapped = self._wrapped_storage


def create_inmemory_file(file_name='tmp.txt', content=b'', content_type=None):
    stream = six.BytesIO()
    stream.write(content)
    file = InMemoryUploadedFile(stream, None, file_name, content_type, stream.tell(), None)
    file.seek(0)
    return file


def create_inmemory_image(file_name='tmp.png', format=None, width=200, height=200, content_type=None):
    from PIL import Image
    if not format:
        _, extension = os.path.splitext(file_name)
        format = extension[1:].upper()
    if not content_type:
        content_type = 'image/{0}'.format(format)
    stream = six.BytesIO()
    size = (width, height)
    color = (255, 0, 0, 0)
    image = Image.new('RGBA', size, color)
    image.save(stream, format=format)
    image_file = InMemoryUploadedFile(stream, None, file_name, content_type, stream.tell(), None)
    image_file.seek(0)
    return image_file
