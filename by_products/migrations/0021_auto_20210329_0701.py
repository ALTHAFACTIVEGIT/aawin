# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-03-29 07:01
from __future__ import unicode_literals

import by_products.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0020_auto_20210329_0445'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bysalegroupgatepass',
            name='gate_pass_file_for_history',
        ),
        migrations.RemoveField(
            model_name='bysalegroupgatepass',
            name='gate_pass_file_now',
        ),
        migrations.AddField(
            model_name='bysalegroupgatepass',
            name='bill_file',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=by_products.models.get_agent_by_product_gatepass_bill),
        ),
        migrations.AddField(
            model_name='bysalegroupgatepass',
            name='dc_file',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=by_products.models.get_agent_by_product_gatepass_dc),
        ),
    ]
