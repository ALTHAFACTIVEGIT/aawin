# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-08-24 08:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0100_auto_20200820_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrequest',
            name='ordered_via',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='main.OrderedVia'),
            preserve_default=False,
        ),
    ]
