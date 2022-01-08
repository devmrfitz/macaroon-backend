from datetime import timedelta, datetime
from rest_framework.authtoken.models import Token

from django.db import models
from django.contrib.auth.models import AbstractUser

from macaroonBackend import settings
from macaroonBackend.settings import TOKEN_VALIDITY_IN_DAYS


def time_delay():
    return datetime.now() + timedelta(days=TOKEN_VALIDITY_IN_DAYS)


class RefreshToken(models.Model):
    token = models.OneToOneField(Token, on_delete=models.CASCADE)
    expiry = \
        models.DateTimeField(default=time_delay)


class User(AbstractUser):
    email = models.EmailField('email address', blank=True, unique=True)


class Profile(models.Model):
    id = models.CharField(primary_key=True, unique=True,
                          max_length=32, editable=False)
    First_Name = models.CharField(max_length=30)
    Last_Name = models.CharField(max_length=50, blank=True)
    public_key = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return self.id
