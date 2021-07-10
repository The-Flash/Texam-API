from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from . import models

# Register your models here.
class StudentAdmin(ImportExportModelAdmin):
    resource_class = models.StudentResource

admin.site.register(models.User, BaseUserAdmin)
admin.site.register(models.Student, StudentAdmin)
admin.site.register(models.Test)
admin.site.register(models.TestSubmission)