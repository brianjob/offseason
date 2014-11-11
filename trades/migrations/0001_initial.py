# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('yahoo_id', models.CharField(max_length=200, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yahoo_id', models.CharField(max_length=200)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('round', models.IntegerField()),
                ('year', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PickPiece',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pick', models.ForeignKey(to='trades.Pick')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('position', models.CharField(max_length=25)),
                ('real_team', models.CharField(max_length=25)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlayerPiece',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('player', models.ForeignKey(to='trades.Player')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('yahoo_id', models.CharField(max_length=200, null=True)),
                ('league', models.ForeignKey(to='trades.League')),
                ('manager', models.OneToOneField(to='trades.Manager')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('proposed_date', models.DateTimeField(null=True, verbose_name=b'date proposed')),
                ('accepted_date', models.DateTimeField(null=True, verbose_name=b'date accepted')),
                ('rejected_date', models.DateTimeField(null=True, verbose_name=b'date rejected')),
                ('completed_date', models.DateTimeField(null=True, verbose_name=b'date completed')),
                ('team1', models.ForeignKey(related_name='trades_proposed', to='trades.Team')),
                ('team2', models.ForeignKey(related_name='trades_received', to='trades.Team')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Veto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('manager', models.ForeignKey(to='trades.Manager')),
                ('trade', models.ForeignKey(to='trades.Trade')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='playerpiece',
            name='trade',
            field=models.ForeignKey(to='trades.Trade'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='player',
            name='fantasy_team',
            field=models.ForeignKey(to='trades.Team'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pickpiece',
            name='trade',
            field=models.ForeignKey(to='trades.Trade'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pick',
            name='team',
            field=models.ForeignKey(to='trades.Team'),
            preserve_default=True,
        ),
    ]
