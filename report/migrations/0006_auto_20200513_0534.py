# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-05-13 05:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0058_businesstype_display_ordinal'),
        ('report', '0005_auto_20200513_0310'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailySessionllyBusinessllySale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_date', models.DateField()),
                ('sold_to', models.CharField(max_length=50)),
                ('tm500_pkt', models.PositiveSmallIntegerField(default=0)),
                ('tm500_litre', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('tm500_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tm500_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('std250_pkt', models.PositiveSmallIntegerField(default=0)),
                ('std250_litre', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('std250_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('std250_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('std500_pkt', models.PositiveSmallIntegerField(default=0)),
                ('std500_litre', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('std500_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('std500_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('fcm500_pkt', models.PositiveSmallIntegerField(default=0)),
                ('fcm500_litre', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('fcm500_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('fcm500_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tmcan', models.PositiveSmallIntegerField(default=0)),
                ('tmcan_litre', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('tmcan_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tmcan_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('smcan', models.PositiveSmallIntegerField(default=0)),
                ('smcan_litre', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('smcan_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('smcan_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('fcmcan', models.PositiveSmallIntegerField(default=0)),
                ('fcmcan_litre', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('fcmcan_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('fcmcan_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('curd500_pkt', models.PositiveSmallIntegerField(default=0)),
                ('curd500_kgs', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('curd500_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('curd500_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('curd150_pkt', models.PositiveSmallIntegerField(default=0)),
                ('curd150_kgs', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('curd150_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('curd150_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cupcurd_box', models.PositiveSmallIntegerField(default=0)),
                ('cupcurd_kgs', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('cupcurd_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cupcurd_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('curd_bucket', models.PositiveSmallIntegerField(default=0)),
                ('curd_bucket_kgs', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('curd_bucket_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('curd_bucket_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('lassi200_pkt', models.PositiveSmallIntegerField(default=0)),
                ('lassi200_kgs', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('lassi200_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('lassi200_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('buttermilk200_pkt', models.PositiveSmallIntegerField(default=0)),
                ('buttermilk200_litre', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('buttermilk200_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('buttermilk200_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Business')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dsbs_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Route')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Session')),
            ],
        ),
        migrations.RemoveField(
            model_name='dailysessionllybusinessllysaleinpacketscansbuckets',
            name='business',
        ),
        migrations.RemoveField(
            model_name='dailysessionllybusinessllysaleinpacketscansbuckets',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='dailysessionllybusinessllysaleinpacketscansbuckets',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='dailysessionllybusinessllysaleinpacketscansbuckets',
            name='route',
        ),
        migrations.RemoveField(
            model_name='dailysessionllybusinessllysaleinpacketscansbuckets',
            name='session',
        ),
        migrations.DeleteModel(
            name='DailySessionllyBusinessllySaleInPacketsCansBuckets',
        ),
    ]
