# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-03-26 07:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0011_auto_20210324_1136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='byproduct',
            name='gst_percent',
        ),
        migrations.AddField(
            model_name='byproduct',
            name='cgst_percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='byproduct',
            name='igst_percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='byproduct',
            name='sgst_percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
