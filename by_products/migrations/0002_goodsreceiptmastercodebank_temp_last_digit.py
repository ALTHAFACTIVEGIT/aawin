# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-03-12 09:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodsreceiptmastercodebank',
            name='temp_last_digit',
            field=models.CharField(default='', max_length=15),
            preserve_default=False,
        ),
    ]
