from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    face_embedding = models.BinaryField(null=True, blank=True)