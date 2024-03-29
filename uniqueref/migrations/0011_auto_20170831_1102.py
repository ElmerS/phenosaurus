# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-31 09:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uniqueref', '0010_auto_20161215_1444'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variable_name', models.CharField(max_length=50)),
                ('value', models.TextField()),
                ('comment', models.TextField()),
            ],
            options={
                'verbose_name': 'Manual setting entry',
                'verbose_name_plural': 'Settings for Phenosaurus',
            },
        ),
        migrations.DeleteModel(
            name='CustomVariables',
        ),
    ]
