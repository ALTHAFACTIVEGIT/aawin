# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-02-22 06:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('by_products', '0048_auto_20220221_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailySaleCloseTrace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_date', models.DateField()),
                ('is_sale_closed', models.BooleanField(default=False)),
                ('closed_at', models.DateTimeField()),
                ('opened_at', models.DateTimeField(blank=True, null=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('closed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_closed_by', to=settings.AUTH_USER_MODEL)),
                ('opened_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_opened_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GoodsReceiptRecordForDaily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_date', models.DateField()),
                ('grn_number', models.CharField(max_length=15)),
                ('quantity_at_receipt', models.DecimalField(decimal_places=2, max_digits=9)),
                ('quantity_now', models.DecimalField(decimal_places=2, max_digits=9)),
                ('quantity_now_time', models.DateTimeField()),
                ('price_per_unit', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('by_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='by_products.ByProduct')),
            ],
        ),
    ]
