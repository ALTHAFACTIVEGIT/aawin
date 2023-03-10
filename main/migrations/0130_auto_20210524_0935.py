# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-05-24 09:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0129_employeeorderchangelog_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeorderchangelog',
            name='cost_per_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='employeeorderchangelog',
            name='count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employeeorderchangelog',
            name='total_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='employeeorderchangelog',
            name='total_days',
            field=models.PositiveIntegerField(),
        ),
    ]
