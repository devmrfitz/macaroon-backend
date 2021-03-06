# Generated by Django 4.0.1 on 2022-01-09 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('macaroonApp', '0008_transaction_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=200)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts_created', to='macaroonApp.profile')),
                ('intermediary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='intermediary_received', to='macaroonApp.profile')),
            ],
        ),
    ]
