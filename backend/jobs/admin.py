from django.contrib import admin
from .models import UserProfile, CV, Category, Job, Application, ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'location')

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('user', 'title')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'category', 'job_type', 'created_at')
    list_filter = ('job_type', 'category')
    search_fields = ('title', 'description', 'company__username')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'student', 'status', 'applied_at')
    list_filter = ('status',)