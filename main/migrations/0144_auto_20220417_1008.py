# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-04-17 10:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0143_productshotnameandquantitytrace'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductShotnameAndQuantityTrace',
            new_name='ProductNameAndQuantityTrace',
        ),
    ]