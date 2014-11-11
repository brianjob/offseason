# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0002_auto_20141101_0332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manager',
            name='yahoo_id',
        ),
        migrations.AddField(
            model_name='manager',
            name='email',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
