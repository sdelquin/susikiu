# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-09 13:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DancingLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('code', models.CharField(max_length=8, unique=True)),
                ('level', models.PositiveSmallIntegerField()),
                ('description', models.CharField(blank=True, max_length=256)),
                ('timetable', models.CharField(blank=True, max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='DancingStyle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('code', models.CharField(max_length=8, unique=True)),
                ('description', models.CharField(blank=True, max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='DifficultyLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('code', models.CharField(max_length=8, unique=True)),
                ('level', models.PositiveSmallIntegerField()),
                ('description', models.CharField(blank=True, max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='EndUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher', models.BooleanField(default=False)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('why_dance', models.CharField(blank=True, max_length=140)),
                ('bio', models.TextField(blank=True)),
                ('twitter_username', models.SlugField(blank=True)),
                ('facebook_username', models.SlugField(blank=True)),
                ('snapchat_username', models.SlugField(blank=True)),
                ('instagram_username', models.SlugField(blank=True)),
                ('dancing_level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.DancingLevel')),
                ('favourite_dancing_style', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.DancingStyle')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=191, unique=True)),
                ('artist', models.CharField(max_length=256)),
                ('spotify_url', models.URLField(blank=True)),
                ('youtube_url', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_url', models.URLField(unique=True)),
                ('title', models.CharField(blank=True, max_length=191, unique=True)),
                ('recorded', models.DateField(blank=True, null=True)),
                ('youtube_id', models.CharField(blank=True, max_length=64, unique=True)),
                ('api_url', models.URLField(blank=True, max_length=191, unique=True)),
                ('embed_url', models.CharField(blank=True, max_length=191, unique=True)),
                ('thumbnail_url', models.URLField(blank=True, unique=True)),
                ('duration', models.PositiveSmallIntegerField(blank=True)),
                ('duration_string', models.CharField(blank=True, max_length=32)),
                ('views_count', models.IntegerField(default=0)),
                ('likes_count', models.IntegerField(default=0)),
                ('dancer1', models.CharField(default='Ad\xe1n', max_length=128)),
                ('dancer2', models.CharField(blank=True, default='Nelisa', max_length=128)),
                ('dancing_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.DancingLevel')),
                ('dancing_style', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.DancingStyle')),
                ('difficulty_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.DifficultyLevel')),
                ('likes', models.ManyToManyField(blank=True, to='app.EndUser')),
                ('song', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Song')),
            ],
        ),
    ]
