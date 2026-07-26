from django.contrib import admin
from django.utils.html import format_html
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_display', 'job_count', 'internship_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    list_per_page = 25

    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)

    def icon_display(self, obj):
        if obj.icon:
            return format_html('<span style="font-size: 24px;">{}</span>', obj.icon)
        return '-'
    icon_display.short_description = 'Icon'

    def job_count(self, obj):
        count = obj.jobs.filter(is_active=True).count()
        url = f"/admin/jobs/job/?category__id__exact={obj.id}"
        return format_html('<a href="{}">{} jobs</a>', url, count)
    job_count.short_description = 'Active Jobs'

    def internship_count(self, obj):
        count = obj.internships.filter(is_active=True).count()
        url = f"/admin/internships/internship/?category__id__exact={obj.id}"
        return format_html('<a href="{}">{} internships</a>', url, count)
    internship_count.short_description = 'Active Internships'