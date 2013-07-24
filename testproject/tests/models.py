from django.db import models


class MockModel(models.Model):
    field = models.CharField(max_length=100)
