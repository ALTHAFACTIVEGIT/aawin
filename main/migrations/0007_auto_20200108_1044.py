# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-08 10:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0006_temporaryregistration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ICustomerTypeWiseProductDiscountTrace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('mrp', models.DecimalField(decimal_places=2, max_digits=9)),
                ('discounted_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='ICustomerProductDiscount',
            new_name='ICustomerTypeWiseProductDiscount',
        ),
        migrations.RemoveField(
            model_name='icustomerproductdiscounttrace',
            name='product_discount_customer',
        ),
        migrations.RemoveField(
            model_name='icustomerproductdiscounttrace',
            name='product_discount_ended_by',
        ),
        migrations.RemoveField(
            model_name='icustomerproductdiscounttrace',
            name='product_discount_started_by',
        ),
        migrations.RemoveField(
            model_name='agent',
            name='image',
        ),
        migrations.AddField(
            model_name='business',
            name='pincode',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ICustomerProductDiscountTrace',
        ),
        migrations.AddField(
            model_name='icustomertypewiseproductdiscounttrace',
            name='icostomer_type_wiser_product_discount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ICustomerTypeWiseProductDiscount'),
        ),
        migrations.AddField(
            model_name='icustomertypewiseproductdiscounttrace',
            name='product_discount_ended_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='icustomer_product_product_discount_end_date_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='icustomertypewiseproductdiscounttrace',
            name='product_discount_started_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='icustomer_product_discount_start_date_created_by', to=settings.AUTH_USER_MODEL),
        ),
    ]