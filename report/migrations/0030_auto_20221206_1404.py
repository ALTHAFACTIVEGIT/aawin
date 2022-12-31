# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2022-12-06 14:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0029_auto_20221206_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinessllysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllybusinesstypellysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='dailysessionllyroutellysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyunionllysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='dailysessionllyzonallysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='monthlysessionllybusinessllysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='monthlysessionllybusinessllysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='monthlysessionllybusinesstypellysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='monthlysessionllybusinesstypellysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='monthlysessionllyroutellysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='monthlysessionllyroutellysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='monthlysessionllyunionllysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='monthlysessionllyunionllysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='monthlysessionllyzonallysale',
            name='tea_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='monthlysessionllyzonallysale',
            name='tea_litre',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        ),
    ]