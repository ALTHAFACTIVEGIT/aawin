# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-01-10 10:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0030_auto_20220110_0703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='byproduct',
            name='hsn_code',
        ),
        migrations.AddField(
            model_name='byproductgroup',
            name='account_code',
            field=models.CharField(default=0, max_length=10),
        ),
        migrations.AddField(
            model_name='byproductgroup',
            name='hsn_code',
            field=models.CharField(default=0, max_length=10),
        ),
    ]
