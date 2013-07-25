import StringIO
import os
from django.conf import UserSettingsHolder, settings
from django.core.files.storage import Storage, default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile


class InMemoryStorage(Storage):
    files = {}

    def _open(self, name, mode):
        return self.files[name]

    def _save(self, name, content):
        self.files[name] = content
        return name

    def exists(self, name):
        return name in self.files

    def clear(self):
        self.files = {}


class InMemoryStorageMixin(object):
    storage = 'djet.files.InMemoryStorage'

    def __init__(self, *args, **kwargs):
        self.wrapped = settings._wrapped
        super(InMemoryStorageMixin, self).__init__(*args, **kwargs)

    def _pre_setup(self):
        override = UserSettingsHolder(settings._wrapped)
        override.DEFAULT_FILE_STORAGE = self.storage
        settings._wrapped = override
        super(InMemoryStorageMixin, self)._pre_setup()

    def _post_teardown(self):
        super(InMemoryStorageMixin, self)._post_teardown()
        default_storage.clear()
        settings._wrapped = self.wrapped


def create_inmemory_file(file_name='tmp.txt', content=None, content_type=None):
    io = StringIO.StringIO()
    io.write(content)
    file = InMemoryUploadedFile(io, None, file_name, content_type, io.len, None)
    file.seek(0)
    return file


def create_inmemory_image(file_name='tmp.png', format=None, width=200, height=200):
    from PIL import Image
    if not format:
        _, extension = os.path.splitext(file_name)
        format = extension[1:].upper()
    io = StringIO.StringIO()
    size = (width, height)
    color = (255, 0, 0, 0)
    image = Image.new('RGBA', size, color)
    image.save(io, format=format)
    image_file = InMemoryUploadedFile(io, None, file_name, format, io.len, None)
    image_file.seek(0)
    return image_file
