# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-07-28 08:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0078_auto_20200727_0631'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentRequestFor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SaleGroupEditPaymentRequestMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_done', models.BooleanField(default=False)),
                ('payment_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.PaymentRequest')),
                ('sale_group', models.ManyToManyField(to='main.SaleGroup')),
            ],
        ),
        migrations.CreateModel(
            name='TempSaleForEdit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.FloatField()),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('main_sale', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Sale')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temp_sale_for_edit_modified_by', to=settings.AUTH_USER_MODEL)),
                ('ordered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temp_sale_for_edit_ordered_by', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Product')),
            ],
        ),
        migrations.CreateModel(
            name='TempSaleGroupForEdit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Business')),
                ('main_sale_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.SaleGroup')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temp_sale_group_for_edit_modified_by', to=settings.AUTH_USER_MODEL)),
                ('ordered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temp_sale_group_for_edit_created_by', to=settings.AUTH_USER_MODEL)),
                ('ordered_via', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.OrderedVia')),
                ('payment_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.PaymentStatus')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Route')),
                ('sale_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.SaleStatus')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Session')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Zone')),
            ],
        ),
        migrations.AlterField(
            model_name='salegrouppaymentrequestmap',
            name='sale_group',
            field=models.ManyToManyField(to='main.SaleGroup'),
        ),
        migrations.AddField(
            model_name='tempsaleforedit',
            name='temp_sale_group_for_edit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.TempSaleGroupForEdit'),
        ),
        migrations.AddField(
            model_name='salegroupeditpaymentrequestmap',
            name='temp_sale_group_for_edit',
            field=models.ManyToManyField(to='main.TempSaleGroupForEdit'),
        ),
        migrations.AddField(
            model_name='paymentrequest',
            name='payment_request_for',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.PaymentRequestFor'),
        ),
    ]
