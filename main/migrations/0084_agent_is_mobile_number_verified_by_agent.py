# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-08-03 02:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0083_icustomer_is_mobile_number_verified_by_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='is_mobile_number_verified_by_agent',
            field=models.BooleanField(default=False),
        ),
    ]
