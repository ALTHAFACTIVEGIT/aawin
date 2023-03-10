# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-08 05:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20200106_1109'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemporaryRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('username', models.CharField(blank=True, max_length=30, null=True)),
                ('password', models.CharField(blank=True, max_length=30, null=True)),
                ('mobile', models.CharField(max_length=13)),
                ('email', models.CharField(blank=True, max_length=30, null=True)),
                ('otp', models.CharField(max_length=30)),
                ('union', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Union')),
            ],
        ),
    ]
