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

    def __str__(self):
        return self.email


class Profile(models.Model):
    id = models.CharField(primary_key=True, unique=True,
                          max_length=32, editable=False)
    First_Name = models.CharField(max_length=30)
    Last_Name = models.CharField(max_length=50, blank=True)
    public_key = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name='profile')
    contacts = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return str(self.user)


class CustomGroup(models.Model):
    name = models.CharField(max_length=30)
    members = models.ManyToManyField(Profile, blank=True, related_name='customGroups')
    description = models.TextField(blank=True)
    slug = models.CharField(unique=True, max_length=30)

    def __str__(self):
        return self.slug


class Transaction(models.Model):  # aka contract
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='transactions_sent')
    intermediary = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='transactions_received')
    destination = models.ManyToManyField(Profile, blank=True)
    amount = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    contract_address = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    expiry = models.DateField(blank=True, null=True)


class FinalPayment(models.Model):
    moneySender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='contracts_created')
    moneyReceiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='intermediary_received')
    amount = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    # transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payments')

