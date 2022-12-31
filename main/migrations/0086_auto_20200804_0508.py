# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-08-04 05:08
from __future__ import unicode_literals

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0085_monthlyagentcommissionruncolumncv_monthlyagentcommissionsubcolumn'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlyagentcommissionruncolumncv',
            name='document',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=main.models.get_monthly_agent_commission_column_document),
        ),
        migrations.AddField(
            model_name='monthlyagentcommissionruncolumncv',
            name='percentage_value',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
