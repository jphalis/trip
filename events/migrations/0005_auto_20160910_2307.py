# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-10 23:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20160910_2248'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['date'], 'verbose_name': 'event', 'verbose_name_plural': 'events'},
        ),
    ]