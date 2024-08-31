from django.db import models
from documents.models import Document
from django.contrib.auth.models import User


class Chat_session_end_reason(models.Model):
    id_end_reason = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50, blank=False, default="")

    class Meta:
        db_table = "chat_session_end_reason"

    def __str__(self):
        return str(self.description)


class Chat_session(models.Model):
    id_chat_session = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(
        User, related_name="chat_sessions", on_delete=models.PROTECT
    )
    started = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField()
    id_end_reason = models.ForeignKey(Chat_session_end_reason, on_delete=models.PROTECT)

    class Meta:
        db_table = "chat_session"

    def __str__(self):
        return self.id_chat_session


class Chat_history(models.Model):
    id_chat_history = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(
        User, related_name="chat_historys", on_delete=models.PROTECT
    )
    id_chat_session = models.ForeignKey(Chat_session, on_delete=models.PROTECT)
    human_entry = models.CharField(max_length=2000)
    ia_entry = models.CharField(max_length=2000)
    creation_date = models.DateTimeField()
    useful = models.BooleanField()

    class Meta:
        db_table = "chat_history"

    def __str__(self):
        return str(self.human_entry)


class Chat_assistant(models.Model):
    id_chat_assistant = models.AutoField(primary_key=True)
    role = models.CharField(max_length=2000, blank=False, default="")
    name = models.CharField(max_length=2000, blank=False, default="")
    llm_model = models.CharField(max_length=50, blank=False, default="GPT-4o mini")
    temperature = models.FloatField(default=0.0, blank=False)
    created_by = models.ForeignKey(
        User, default=1, related_name="chat_assistants", on_delete=models.PROTECT
    )

    class Meta:
        db_table = "chat_assistant"

    def __str__(self):
        return str(self.name)


class Chat_assistant_documents(models.Model):
    id_chat_assistant_document = models.AutoField(primary_key=True)
    id_chat_assistant = models.ForeignKey(Chat_assistant, on_delete=models.PROTECT)
    id_document = models.ForeignKey(Document, on_delete=models.PROTECT)
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, related_name="chat_assistant_documents", on_delete=models.PROTECT
    )

    class Meta:
        db_table = "chat_assistant_documents"

    def __str__(self):
        return str(self.id_chat_assistant_document)
