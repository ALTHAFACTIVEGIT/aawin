# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-02-12 05:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0039_auto_20220210_1043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cashreceiptaccountbusinesstypemap',
            name='business_type',
        ),
        migrations.AddField(
            model_name='cashreceiptaccountbusinesstypemap',
            name='payment_method',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='by_products.BySaleGroupPaymentMethod'),
            preserve_default=False,
        ),
    ]
