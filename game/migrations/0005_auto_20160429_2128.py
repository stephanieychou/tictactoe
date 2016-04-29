# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-29 21:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20160429_1708'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='letter',
        ),
        migrations.AddField(
            model_name='board',
            name='playerO',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='playerO', to='game.Player'),
        ),
        migrations.AddField(
            model_name='board',
            name='playerX',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='playerX', to='game.Player'),
        ),
    ]
