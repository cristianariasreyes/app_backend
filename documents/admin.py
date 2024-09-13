from django.contrib import admin
from .models import Document_type, Document_department, Document_category, Document

# Document Models
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id_document', 'document_name', 'subject', 'owner', 'creation_date', 'last_update')
    search_fields = ('document_name', 'owner__username', 'subject')
    list_filter = ('creation_date', 'last_update', 'owner')

class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id_document_type', 'description')

class DocumentDepartmentAdmin(admin.ModelAdmin):
    list_display = ('id_document_department', 'description')

class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('id_document_category', 'description')

# Register the models in the Django Admin
admin.site.register(Document_type, DocumentTypeAdmin)
admin.site.register(Document_department, DocumentDepartmentAdmin)
admin.site.register(Document_category, DocumentCategoryAdmin)
admin.site.register(Document, DocumentAdmin)
