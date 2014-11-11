# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0005_auto_20141104_0304'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manager',
            name='code',
        ),
        migrations.RemoveField(
            model_name='manager',
            name='email',
        ),
    ]
