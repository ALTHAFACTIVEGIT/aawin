# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-03-29 04:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0019_auto_20210327_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodsreceiptrecordbysalemap',
            name='cgst_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='goodsreceiptrecordbysalemap',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='goodsreceiptrecordbysalemap',
            name='sgst_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='goodsreceiptrecordbysalemap',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
