# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-07-27 06:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0076_auto_20200725_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempSale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.FloatField()),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temp_sale_modified_by', to=settings.AUTH_USER_MODEL)),
                ('ordered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temp_sale_ordered_by', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Product')),
            ],
        ),
        migrations.CreateModel(
            name='TempSaleGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Business')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temp_sale_group_modified_by', to=settings.AUTH_USER_MODEL)),
                ('ordered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temp_sale_group_created_by', to=settings.AUTH_USER_MODEL)),
                ('ordered_via', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.OrderedVia')),
                ('payment_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.PaymentStatus')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Route')),
                ('sale_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.SaleStatus')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Session')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Zone')),
            ],
        ),
        migrations.AddField(
            model_name='salegrouppaymentrequestmap',
            name='is_done',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='salegrouppaymentrequestmap',
            name='sale_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.SaleGroup'),
        ),
        migrations.AddField(
            model_name='tempsale',
            name='temp_sale_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.TempSaleGroup'),
        ),
        migrations.AddField(
            model_name='salegrouppaymentrequestmap',
            name='temp_sale_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.TempSaleGroup'),
            preserve_default=False,
        ),
    ]
