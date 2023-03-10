# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-09-23 01:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0104_auto_20200826_0244'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='icustomersalegroup',
            unique_together=set([('business', 'icustomer', 'date', 'session')]),
        ),
        migrations.AlterUniqueTogether(
            name='sale',
            unique_together=set([('sale_group', 'product')]),
        ),
    ]
