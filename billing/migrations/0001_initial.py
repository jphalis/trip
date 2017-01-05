# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-05 14:03
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('auto_renew', models.BooleanField(default=True)),
                ('next_billing_fee', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(default=datetime.datetime(2018, 1, 5, 14, 3, 40, 420951))),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'membership',
                'verbose_name_plural': 'memberships',
            },
        ),
    ]