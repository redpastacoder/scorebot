# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-11-21 21:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sbehost', '0014_auto_20161121_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameticket',
            name='game_team',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sbehost.GameTeam'),
            preserve_default=False,
        ),
    ]
