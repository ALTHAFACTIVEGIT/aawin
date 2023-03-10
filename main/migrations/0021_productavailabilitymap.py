# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-28 10:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20200128_0952'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductAvailabilityMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_available', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Product')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Session')),
            ],
        ),
    ]
