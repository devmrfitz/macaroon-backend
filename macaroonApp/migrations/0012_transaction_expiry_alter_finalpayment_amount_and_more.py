# Generated by Django 4.0.1 on 2022-01-09 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('macaroonApp', '0011_rename_transaction_id_transaction_contract_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='expiry',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='finalpayment',
            name='amount',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.CharField(max_length=200),
        ),
    ]