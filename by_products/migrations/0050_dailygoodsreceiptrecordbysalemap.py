# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-02-22 06:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0049_dailysaleclosetrace_goodsreceiptrecordfordaily'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyGoodsReceiptRecordBySaleMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_dispatched', models.DecimalField(decimal_places=2, max_digits=9)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('by_sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='by_products.BySale')),
                ('daily_goods_receipt_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='by_products.GoodsReceiptRecordForDaily')),
            ],
        ),
    ]
