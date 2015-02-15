# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overlay', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='rtt',
            field=models.DecimalField(decimal_places=3, max_digits=10, default=255.0),
            preserve_default=True,
        ),
    ]
