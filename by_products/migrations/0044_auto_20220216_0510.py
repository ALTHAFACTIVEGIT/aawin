# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-02-16 05:10
from __future__ import unicode_literals

import by_products.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('by_products', '0043_businesswisedailysaleedittrace'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleGatepass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_start_time', models.TimeField()),
                ('gatepass_file', models.FileField(blank=True, max_length=1000, null=True, upload_to=by_products.models.get_vehicle_gatepass)),
                ('prepated_at', models.DateTimeField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver_name', models.CharField(max_length=15)),
                ('vehicle_number', models.CharField(max_length=15)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='bysalegroup',
            name='is_vehicle_gatepass_taken',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehiclegatepass',
            name='by_sale_group',
            field=models.ManyToManyField(to='by_products.BySaleGroup'),
        ),
        migrations.AddField(
            model_name='vehiclegatepass',
            name='prepared_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vehiclegatepass',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='by_products.VehicleMaster'),
        ),
    ]
