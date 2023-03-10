# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-08-23 13:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0135_auto_20210818_1425'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessWilkMilkLitreLimit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limit_in_litre', models.DecimalField(decimal_places=7, max_digits=9)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Business')),
            ],
        ),
    ]
