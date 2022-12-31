# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-06-18 05:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0068_paymentrequestidbank'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductFinanceCodeMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=15)),
                ('finance_product_code', models.CharField(max_length=15)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('product', models.ManyToManyField(to='main.Product')),
            ],
        ),
        migrations.AddField(
            model_name='businesstype',
            name='finance_main_code',
            field=models.CharField(default=1, max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='counter',
            name='finance_sub_code',
            field=models.CharField(default=1, max_length=15),
            preserve_default=False,
        ),
    ]
