# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-08-26 02:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0102_businesstypewiseoveralllitrelimit'),
    ]

    operations = [
        migrations.CreateModel(
            name='ICustomerOrderEndDateMonthWise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.PositiveIntegerField()),
                ('date', models.PositiveIntegerField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
