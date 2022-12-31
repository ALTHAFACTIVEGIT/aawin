# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-08-18 14:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0134_auto_20210728_1232'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessOwnParlourTypeMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Business')),
            ],
        ),
        migrations.CreateModel(
            name='OwnParlourType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentGatewayConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enable', models.BooleanField(default=True)),
                ('alert_message', models.TextField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('ordered_via', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.OrderedVia')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentGatewayCrashLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crash_happend_at', models.DateTimeField()),
                ('error_message', models.TextField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='businessownparlourtypemap',
            name='own_parlour_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.OwnParlourType'),
        ),
    ]