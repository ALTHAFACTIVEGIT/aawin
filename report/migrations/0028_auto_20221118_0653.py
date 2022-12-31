# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-11-18 06:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0027_auto_20210416_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='curd5000_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='curd5000_kgs',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='curd5000_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='curd5000_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='curd5000_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='curd5000_kgs',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='curd5000_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='curd5000_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='curd5000_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='curd5000_kgs',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='curd5000_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='curd5000_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='curd5000_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='curd5000_kgs',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='curd5000_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='curd5000_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='curd5000_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='curd5000_kgs',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='curd5000_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='curd5000_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]