# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-02-28 10:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_collectioncenter_productquantityvariationprice_productquantityvariationpricetrace'),
    ]

    operations = [
        migrations.AddField(
            model_name='counter',
            name='collection_center',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.CollectionCenter'),
            preserve_default=False,
        ),
    ]