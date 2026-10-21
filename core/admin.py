from django.contrib import admin
from .models import Job, UserSession, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'created_at')
    list_filter = ('is_active', 'category')
    search_fields = ('title', 'description')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'state', 'selected_job', 'updated_at')
    search_fields = ('phone_number', 'applicant_name')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant_name', 'job', 'phone_number', 'applied_at')
    search_fields = ('applicant_name', 'phone_number')