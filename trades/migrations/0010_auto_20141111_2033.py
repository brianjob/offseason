# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0009_remove_team_comanager'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='trade_reject_time',
            field=models.IntegerField(default=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='team',
            name='manager',
            field=models.ForeignKey(to='trades.Manager'),
            preserve_default=True,
        ),
    ]
