from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User

class Cat(models.Model):
  name = models.CharField(max_length=100)
  # add user_id FK column
  user = models.ForeignKey(User, on_delete=models.CASCADE)