# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-06 11:09
from __future__ import unicode_literals

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20200106_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='aadhar_document',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=main.models.get_agent_aadhar_image),
        ),
    ]