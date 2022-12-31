# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-08-02 00:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0146_bsnlsmstemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cgst_percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='product',
            name='hsn_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='igst_percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='product',
            name='sgst_percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]