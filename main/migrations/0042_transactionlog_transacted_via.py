# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-02-29 07:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_auto_20200229_0742'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionlog',
            name='transacted_via',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.TransactedVia'),
            preserve_default=False,
        ),
    ]
