# Generated by Django 4.0 on 2022-01-08 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authtoken', '0003_tokenproxy'),
        ('macaroonApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='refreshtoken',
            name='token',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='authtoken.token'),
            preserve_default=False,
        ),
    ]
