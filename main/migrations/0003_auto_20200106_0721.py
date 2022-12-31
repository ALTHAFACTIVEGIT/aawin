# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-06 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20200106_0657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='businesstype',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='constituency',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='locationcategory',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='nominee',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='nominee',
            name='last_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='orderedvia',
            name='name',
            field=models.CharField(max_length=70, unique=True),
        ),
        migrations.AlterField(
            model_name='productgroup',
            name='name',
            field=models.CharField(max_length=60, unique=True),
        ),
        migrations.AlterField(
            model_name='relationtype',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='route',
            name='name',
            field=models.CharField(max_length=60, unique=True),
        ),
        migrations.AlterField(
            model_name='salestatus',
            name='name',
            field=models.CharField(max_length=70, unique=True),
        ),
        migrations.AlterField(
            model_name='saletype',
            name='name',
            field=models.CharField(max_length=70, unique=True),
        ),
        migrations.AlterField(
            model_name='taluk',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='transactiondirection',
            name='payment_from',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='transactiondirection',
            name='payment_to',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='transactionmode',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='usertype',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='ward',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
