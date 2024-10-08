# Generated by Django 5.0.7 on 2024-09-12 19:27

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_document_s3_document_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='id',
        ),
        migrations.RemoveField(
            model_name='document',
            name='id_vdb',
        ),
        migrations.RemoveField(
            model_name='document',
            name='name',
        ),
        migrations.RemoveField(
            model_name='document',
            name='s3_document_path',
        ),
        migrations.AddField(
            model_name='document',
            name='company_id',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='document',
            name='document_name',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='document',
            name='id_document',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='document',
            name='last_update',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='document_path',
            field=models.CharField(default='', max_length=200),
        ),
    ]
