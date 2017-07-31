# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-31 15:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pylims.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('description', models.TextField(blank=True)),
                ('geometry', models.TextField(blank=True)),
                ('user_created', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LocationMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=55, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('value', models.TextField()),
                ('tags', pylims.models.TagsField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pylims.Location')),
                ('user_created', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55, unique=True)),
                ('description', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('user_created', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=55)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('value', models.TextField()),
                ('tags', pylims.models.TagsField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pylims.Project')),
                ('user_created', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('sample_id', models.CharField(max_length=55, unique=True)),
                ('collected', models.DateTimeField(verbose_name='collected')),
                ('comment', models.TextField(blank=True)),
                ('tags', pylims.models.TagsField()),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='pylims.Location')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pylims.Project')),
                ('user_created', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SampleMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('value', models.FloatField(blank=True, null=True)),
                ('RDL', models.FloatField(blank=True, null=True)),
                ('non_detect', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
                ('tags', pylims.models.TagsField()),
            ],
        ),
        migrations.CreateModel(
            name='SampleMetaKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('short_name', models.CharField(blank=True, max_length=55, unique=True)),
                ('description', models.TextField(blank=True)),
                ('user_created', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('short_name', models.CharField(blank=True, max_length=55, unique=True)),
                ('description', models.TextField(blank=True)),
                ('user_created', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='samplemeta',
            name='key',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pylims.SampleMetaKey'),
        ),
        migrations.AddField(
            model_name='samplemeta',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pylims.Sample'),
        ),
        migrations.AddField(
            model_name='samplemeta',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='pylims.Unit'),
        ),
        migrations.AddField(
            model_name='samplemeta',
            name='user_created',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='projectmeta',
            unique_together=set([('project', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='locationmeta',
            unique_together=set([('location', 'key')]),
        ),
    ]