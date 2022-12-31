# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-02-09 07:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_messsage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personmessage',
            name='response_json',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='personmessage',
            name='response_message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='personmessage',
            name='response_status_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
