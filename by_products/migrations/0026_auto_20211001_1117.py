# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-10-01 11:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0025_auto_20211001_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='byproduct',
            name='code',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
