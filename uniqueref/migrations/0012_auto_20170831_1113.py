# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-31 09:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uniqueref', '0011_auto_20170831_1102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seqsummary',
            name='relscreen',
        ),
        migrations.DeleteModel(
            name='SeqSummary',
        ),
    ]
