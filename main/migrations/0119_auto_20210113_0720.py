# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-01-13 07:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0118_employeemonthlyorderlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeemonthlyorderlog',
            name='order_for',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ICustomerType'),
        ),
    ]
