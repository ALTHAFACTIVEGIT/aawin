# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-02-17 04:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_auto_20200217_0433'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='contract_strart_from',
            new_name='contract_start_from',
        ),
    ]
