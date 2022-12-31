# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-02-15 05:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0141_agentprofile_gst_number'),
        ('by_products', '0042_auto_20220212_0810'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessWiseDailySaleEditTrace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_date', models.DateField(db_index=True)),
                ('opening_quantity', models.PositiveIntegerField(default=0)),
                ('old_opening_quantity', models.PositiveIntegerField(default=0)),
                ('received_quantity', models.PositiveIntegerField(default=0)),
                ('old_received_quantity', models.PositiveIntegerField(default=0)),
                ('sales_quantity', models.PositiveIntegerField(default=0)),
                ('old_sales_quantity', models.PositiveIntegerField(default=0)),
                ('closing_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('old_closing_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('edited_at', models.DateTimeField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Business')),
                ('by_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='by_products.ByProduct')),
                ('edited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_sale_edited_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]