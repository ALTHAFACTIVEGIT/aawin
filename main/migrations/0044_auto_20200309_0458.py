# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-03-09 04:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_overallindentpersession_overall_indent_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='KycIDProofDocumentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='icustomer',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='icustomer',
            name='kyc_idproof_document_value',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='icustomer',
            name='kyc_idproof_document_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.KycIDProofDocumentType'),
        ),
    ]