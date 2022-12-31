# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-07-28 12:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0133_businesstypewisefutureorderconfig_orderdatemodifytoggle'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessTypeWiseFreeProductConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_free', models.BooleanField(default=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('business_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.BusinessType')),
                ('free_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='free_product_id_business_type_wise', to='main.Product')),
                ('main_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_product_id_business_type_wise', to='main.Product')),
            ],
        ),
        migrations.AddField(
            model_name='orderdatemodifytoggle',
            name='time_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdatemodifytoggle',
            name='time_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]