# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-08-06 04:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0088_paymentrequest_is_amount_returened_to_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='icustomer',
            name='is_aadhar_number_verified_by_customer',
            field=models.BooleanField(default=False),
        ),
    ]
