# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-04-16 06:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0122_freeproductproperty'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='freeproductproperty',
            name='product',
        ),
        migrations.AddField(
            model_name='freeproductproperty',
            name='free_product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='free_product_id', to='main.Product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='freeproductproperty',
            name='main_product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='main_product_id', to='main.Product'),
            preserve_default=False,
        ),
    ]