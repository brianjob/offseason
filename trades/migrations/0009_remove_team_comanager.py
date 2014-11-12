# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0008_auto_20141111_1612'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='comanager',
        ),
    ]
