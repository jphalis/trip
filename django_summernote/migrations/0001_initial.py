# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-04 16:16
from __future__ import unicode_literals

from django.db import migrations, models
import django_summernote.settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('file', models.FileField(upload_to=django_summernote.settings.uploaded_filepath)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
