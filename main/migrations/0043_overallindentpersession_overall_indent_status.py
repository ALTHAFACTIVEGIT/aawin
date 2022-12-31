# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-03-01 08:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_transactionlog_transacted_via'),
    ]

    operations = [
        migrations.AddField(
            model_name='overallindentpersession',
            name='overall_indent_status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.IndentStatus'),
            preserve_default=False,
        ),
    ]