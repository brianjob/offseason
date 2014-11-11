# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0007_trade_vetoed_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='num_teams',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='league',
            name='url',
            field=models.CharField(default='', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='comanager',
            field=models.ForeignKey(related_name='teams_comanaged', to='trades.Manager', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='manager',
            field=models.ForeignKey(related_name='teams_managed', to='trades.Manager'),
            preserve_default=True,
        ),
    ]
