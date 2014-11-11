# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='manager',
            name='code',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='manager',
            name='yahoo_guid',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='league',
            name='yahoo_id',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='manager',
            name='user',
            field=models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='manager',
            field=models.ForeignKey(to='trades.Manager'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='yahoo_id',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
