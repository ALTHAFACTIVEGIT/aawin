# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-05-24 12:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0130_auto_20210524_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeorderchangelog',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Session'),
        ),
    ]