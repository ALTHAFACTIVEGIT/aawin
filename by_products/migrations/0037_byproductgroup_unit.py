# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-02-01 11:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0036_auto_20220124_0606'),
    ]

    operations = [
        migrations.AddField(
            model_name='byproductgroup',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='by_products.ByProductUnit'),
        ),
    ]
