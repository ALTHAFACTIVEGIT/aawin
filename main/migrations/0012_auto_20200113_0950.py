# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-13 09:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0011_icustomeridbank'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductTrace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('name', models.CharField(max_length=50)),
                ('short_name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=30)),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=9)),
                ('mrp', models.DecimalField(decimal_places=2, max_digits=9)),
                ('gst_percent', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('snf', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('fat', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('is_homogenised', models.BooleanField(default=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='fat',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_homogenised',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='snf',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='producttrace',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Product'),
        ),
        migrations.AddField(
            model_name='producttrace',
            name='product_price_ended_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_price_end_date_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='producttrace',
            name='product_price_started_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_price_start_date_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='producttrace',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ProductUnit'),
        ),
    ]