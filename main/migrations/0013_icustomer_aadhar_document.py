# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-18 06:28
from __future__ import unicode_literals

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20200113_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='icustomer',
            name='aadhar_document',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=main.models.get_icustomer_aadhar_image),
        ),
    ]