# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-02-12 08:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0041_auto_20220212_0515'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesswisedailysaleupdate',
            name='edit_expiry_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='businesswisedailysaleupdate',
            name='is_edit_expired',
            field=models.BooleanField(default=False),
        ),
    ]
