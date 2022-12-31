# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-05-14 05:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0014_auto_20200514_0529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='buttermilk200_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='cupcurd_box',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='cupcurd_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='curd150_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='curd500_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='curd_bucket',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='fcm500_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='fcmcan',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='lassi200_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='smcan',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='std250_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='std500_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='tm500_pkt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailysessionllyroutellysale',
            name='tmcan',
            field=models.PositiveIntegerField(default=0),
        ),
    ]