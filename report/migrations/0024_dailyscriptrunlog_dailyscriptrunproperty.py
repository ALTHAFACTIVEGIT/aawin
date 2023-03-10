# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-12-30 06:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('report', '0023_monthlysessionllybusinessllysale_monthlysessionllybusinesstypellysale_monthlysessionllyroutellysale_'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyScriptRunLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_start_time', models.DateTimeField()),
                ('run_end_time', models.DateTimeField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('run_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DailyScriptRunProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script_name', models.CharField(max_length=150)),
                ('run_start_time', models.DateTimeField()),
                ('run_end_time', models.DateTimeField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('daily_script_run_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report.DailyScriptRunLog')),
            ],
        ),
    ]
