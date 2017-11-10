from django.db import models


class MockModel(models.Model):
    field = models.CharField(max_length=100)


class MockFileModel(models.Model):
    field = models.CharField(max_length=100)
    file = models.FileField(upload_to='files')
