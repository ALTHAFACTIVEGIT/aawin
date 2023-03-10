# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-04-08 06:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0052_vehicle_tray_capacity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carrier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, null=True)),
                ('publish_from', models.DateTimeField(help_text="With Published chosen, won't be shown until this time", verbose_name='Published from')),
                ('expires_on', models.DateTimeField(help_text="With Expired chosen, won't be shown after this time", verbose_name='Expires on')),
                ('is_active', models.BooleanField(default=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CarrierFileMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=1000, upload_to=main.models.get_carrier_file_upload_destination)),
                ('carrier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Carrier')),
            ],
        ),
        migrations.CreateModel(
            name='Tender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, null=True)),
                ('publish_from', models.DateTimeField(help_text="With Published chosen, won't be shown until this time", verbose_name='Published from')),
                ('expires_on', models.DateTimeField(help_text="With Expired chosen, won't be shown after this time", verbose_name='Expires on')),
                ('is_active', models.BooleanField(default=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TenderFileMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=1000, upload_to=main.models.get_tender_file_upload_destination)),
                ('tender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Tender')),
            ],
        ),
    ]
