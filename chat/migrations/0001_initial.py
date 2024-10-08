# Generated by Django 5.0.7 on 2024-08-31 20:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('documents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat_session_end_reason',
            fields=[
                ('id_end_reason', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(default='', max_length=50)),
            ],
            options={
                'db_table': 'chat_session_end_reason',
            },
        ),
        migrations.CreateModel(
            name='Chat_assistant',
            fields=[
                ('id_chat_assistant', models.AutoField(primary_key=True, serialize=False)),
                ('role', models.CharField(default='', max_length=2000)),
                ('name', models.CharField(default='', max_length=2000)),
                ('llm_model', models.CharField(default='GPT-4o mini', max_length=50)),
                ('temperature', models.FloatField(default=0.0)),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='chat_assistants', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'chat_assistant',
            },
        ),
        migrations.CreateModel(
            name='Chat_assistant_documents',
            fields=[
                ('id_chat_assistant_document', models.AutoField(primary_key=True, serialize=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chat_assistant_documents', to=settings.AUTH_USER_MODEL)),
                ('id_chat_assistant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='chat.chat_assistant')),
                ('id_document', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='documents.document')),
            ],
            options={
                'db_table': 'chat_assistant_documents',
            },
        ),
        migrations.CreateModel(
            name='Chat_session',
            fields=[
                ('id_chat_session', models.AutoField(primary_key=True, serialize=False)),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('ended', models.DateTimeField()),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chat_sessions', to=settings.AUTH_USER_MODEL)),
                ('id_end_reason', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='chat.chat_session_end_reason')),
            ],
            options={
                'db_table': 'chat_session',
            },
        ),
        migrations.CreateModel(
            name='Chat_history',
            fields=[
                ('id_chat_history', models.AutoField(primary_key=True, serialize=False)),
                ('human_entry', models.CharField(max_length=2000)),
                ('ia_entry', models.CharField(max_length=2000)),
                ('creation_date', models.DateTimeField()),
                ('useful', models.BooleanField()),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chat_historys', to=settings.AUTH_USER_MODEL)),
                ('id_chat_session', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='chat.chat_session')),
            ],
            options={
                'db_table': 'chat_history',
            },
        ),
    ]
