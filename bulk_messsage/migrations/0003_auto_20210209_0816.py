# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-02-09 08:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_messsage', '0002_auto_20210209_0745'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('session', models.CharField(max_length=100)),
                ('time_start', models.CharField(max_length=10)),
                ('time_end', models.CharField(max_length=10)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='person',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bulk_messsage.Department'),
        ),
    ]
