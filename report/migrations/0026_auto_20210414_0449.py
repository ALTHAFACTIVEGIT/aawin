# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2021-04-14 04:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0025_dailyscriptrunlog_date_of_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='bm_jar200_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='bm_jar200_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='bm_jar200_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='bm_jar200_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='bm_jar200_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='bm_jar200_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='bm_jar200_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='bm_jar200_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='bm_jar200_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='bm_jar200_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='bm_jar200_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='bm_jar200_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='bm_jar200_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='bm_jar200_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='bm_jar200_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='bm_jar200_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='bm_jar200_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='bm_jar200_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='bm_jar200_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='bm_jar200_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]