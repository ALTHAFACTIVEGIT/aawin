# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-08 10:46
from __future__ import unicode_literals

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20200108_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(default='', max_length=1000, upload_to=main.models.get_user_profile_image),
            preserve_default=False,
        ),
    ]
