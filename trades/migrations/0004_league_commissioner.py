# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0003_auto_20141101_0440'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='commissioner',
            field=models.ForeignKey(default=0, to='trades.Manager'),
            preserve_default=False,
        ),
    ]
