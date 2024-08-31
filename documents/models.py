# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Document_type(models.Model):
    id_document_type = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200, default="", blank=False)

    class Meta:
        db_table = "document_type"

    def __str__(self):
        return self.description


class Document_department(models.Model):
    id_document_department = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200, default="", blank=False)

    class Meta:
        db_table = "document_department"

    def __str__(self):
        return self.description


class Document_category(models.Model):
    id_document_category = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200, default="", blank=False)

    class Meta:
        db_table = "document_category"

    def __str__(self):
        return self.description


class Document(models.Model):
    subject = models.CharField(max_length=200, default="", blank=False)
    resume = models.CharField(max_length=800, default="", blank=False)
    document_path = models.CharField(max_length=1024, default="", blank=False)
    s3_document_path = models.CharField(max_length=1024, default="", blank=False)
    id_document_type = models.ForeignKey(
        Document_type, related_name="documents", on_delete=models.PROTECT
    )
    id_document_category = models.ForeignKey(
        Document_category, related_name="documents", on_delete=models.PROTECT
    )
    id_document_department = models.ForeignKey(
        Document_department, related_name="documents", on_delete=models.PROTECT
    )
    id_vdb = models.CharField(max_length=50, default="", blank=False)
    owner = models.ForeignKey(User, related_name="documents", on_delete=models.PROTECT)
    creation_date = models.DateTimeField(default=now)
    name = models.CharField(max_length=100, default="", blank=False)

    class Meta:
        db_table = "document"

    def __str__(self):
        return self.resume
