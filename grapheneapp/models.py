from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    published_date = models.DateField()

    def clean(self):
        if not self.title or not self.author:
            raise ValidationError('Title and Author fields cannot be empty.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
