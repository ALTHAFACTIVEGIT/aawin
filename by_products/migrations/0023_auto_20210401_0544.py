# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-04-01 05:44
from __future__ import unicode_literals

import by_products.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('by_products', '0022_auto_20210331_0910'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodsReceiptRecordEmployeeOrderBySaleMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_dispatched', models.DecimalField(decimal_places=2, max_digits=9)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cgst_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sgst_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('employee_order_by_sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='by_products.EmployeeOrderBySale')),
                ('goods_receipt_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='by_products.GoodsReceiptRecord')),
            ],
        ),
        migrations.AlterField(
            model_name='employeeorderbysalegroupgatepass',
            name='dc_file',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=by_products.models.get_agent_by_product_gatepass_dc_for_employee_order),
        ),
    ]
