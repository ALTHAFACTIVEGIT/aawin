# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-05-13 06:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0007_dailysessionllybusinessllysale_cupcurd_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dailysessionllybusinessllysale',
            old_name='total_price',
            new_name='total_cost',
        ),
    ]
