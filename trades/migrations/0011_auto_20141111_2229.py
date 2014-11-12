# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0010_auto_20141111_2033'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='can_trade_picks',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='league',
            name='is_auction_draft',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='league',
            name='scoring_type',
            field=models.CharField(default='head', max_length=50),
            preserve_default=False,
        ),
    ]
