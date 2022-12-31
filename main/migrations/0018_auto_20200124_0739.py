# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-24 07:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_routetrace_indent_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businesstypewiseproductcommissiontrace',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='businesstypewiseproductcommissiontrace',
            name='start_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='businesstypewiseproductdiscounttrace',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='businesstypewiseproductdiscounttrace',
            name='start_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='businesswiseproductdiscounttrace',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='businesswiseproductdiscounttrace',
            name='start_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='icustomertypewiseproductdiscounttrace',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='icustomertypewiseproductdiscounttrace',
            name='start_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='producttrace',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='producttrace',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]
