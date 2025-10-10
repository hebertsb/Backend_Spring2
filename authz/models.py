from django.db import models

from core.models import TimeStampedModel

# Create your models here.
class Rol(TimeStampedModel):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
