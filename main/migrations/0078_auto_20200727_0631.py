# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-07-27 06:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0077_auto_20200727_0616'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salegrouppaymentrequestmap',
            name='sale_group',
        ),
        migrations.AddField(
            model_name='salegrouppaymentrequestmap',
            name='sale_group',
            field=models.ManyToManyField(blank=True, null=True, to='main.SaleGroup'),
        ),
        migrations.RemoveField(
            model_name='salegrouppaymentrequestmap',
            name='temp_sale_group',
        ),
        migrations.AddField(
            model_name='salegrouppaymentrequestmap',
            name='temp_sale_group',
            field=models.ManyToManyField(to='main.TempSaleGroup'),
        ),
    ]