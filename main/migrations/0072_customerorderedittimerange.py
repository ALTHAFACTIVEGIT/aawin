# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-07-01 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0071_auto_20200618_0605'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerOrderEditTimeRange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_time', models.TimeField()),
                ('to_time', models.TimeField()),
                ('description', models.TextField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
