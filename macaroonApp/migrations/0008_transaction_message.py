# Generated by Django 4.0.1 on 2022-01-09 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macaroonApp', '0007_rename_receiver_transaction_intermediary'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]