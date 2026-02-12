from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import UserProfile, CV, Category, Job, Application, ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'location', 'get_date_joined', 'get_hits')

    def get_hits(self, obj):
        from hitcount.models import HitCount
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(obj)
        try:
            return HitCount.objects.get(content_type=ct, object_pk=obj.pk).hits
        except HitCount.DoesNotExist:
            return 0
    get_hits.short_description = 'Profile Views'

    def get_date_joined(self, obj):
        return obj.user.date_joined
    get_date_joined.short_description = 'Date Joined'
    get_date_joined.admin_order_field = 'user__date_joined'

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('user', 'title')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'get_hits', 'category', 'job_type', 'created_at')
    list_filter = ('job_type', 'category')
    search_fields = ('title', 'description', 'company__username')

    def get_hits(self, obj):
        from hitcount.models import HitCount
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(obj)
        try:
            return HitCount.objects.get(content_type=ct, object_pk=obj.pk).hits
        except HitCount.DoesNotExist:
            return 0
    get_hits.short_description = 'Views'

    def changelist_view(self, request, extra_context=None):
        # 1. Jobs per Category
        category_data = (
            Job.objects.values('category__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # 2. Jobs over Time
        time_series_data = (
            Job.objects.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        chart_data = {
            'categories': {
                'labels': [item['category__name'] or 'N/A' for item in category_data],
                'values': [item['count'] for item in category_data],
            },
            'time_series': {
                'labels': [item['day'].strftime('%Y-%m-%d') for item in time_series_data if item['day']],
                'values': [item['count'] for item in time_series_data],
            }
        }
        
        extra_context = extra_context or {}
        extra_context['chart_data'] = chart_data
        
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'student', 'status', 'applied_at')
    list_filter = ('status',)

    def changelist_view(self, request, extra_context=None):
        # 1. Applications per Category
        category_data = (
            Application.objects.values('job__category__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # 2. Applications over Time
        time_series_data = (
            Application.objects.annotate(day=TruncDay('applied_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        chart_data = {
            'categories': {
                'labels': [item['job__category__name'] or 'N/A' for item in category_data],
                'values': [item['count'] for item in category_data],
            },
            'time_series': {
                'labels': [item['day'].strftime('%Y-%m-%d') for item in time_series_data if item['day']],
                'values': [item['count'] for item in time_series_data],
            }
        }
        
        extra_context = extra_context or {}
        extra_context['chart_data'] = chart_data
        
        return super().changelist_view(request, extra_context=extra_context)