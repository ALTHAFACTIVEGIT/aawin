# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-04-17 06:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0004_auto_20210416_1225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banktransaction',
            name='cheque_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
