# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-02-09 10:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_messsage', '0004_department_short_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='personmessage',
            name='acknowledged_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='personmessage',
            name='is_acknowledged',
            field=models.BooleanField(default=False),
        ),
    ]
