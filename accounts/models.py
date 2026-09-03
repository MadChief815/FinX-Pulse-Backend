from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	email = models.EmailField(unique=True)

	REQUIRED_FIELDS = ["email"]

	def __str__(self):
		return self.username
