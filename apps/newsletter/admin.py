from django.contrib import admin
from django.utils.html import format_html
from .models import Subscriber

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'status_badge', 'subscribed_at', 'unsubscribed_at')
    list_filter = ('is_active', 'subscribed_at', 'unsubscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    date_hierarchy = 'subscribed_at'
    list_per_page = 50

    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'is_active')
        }),
        ('Timeline', {
            'fields': ('subscribed_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #D1FAE5; color: #065F46; padding: 4px 12px; '
                'border-radius: 12px; font-size: 12px; font-weight: 500;">Active</span>'
            )
        return format_html(
            '<span style="background: #FEE2E2; color: #991B1B; padding: 4px 12px; '
            'border-radius: 12px; font-size: 12px; font-weight: 500;">Unsubscribed</span>'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'is_active'

    actions = ['activate_subscribers', 'deactivate_subscribers', 'export_emails']

    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, f'{updated} subscriber(s) activated.')
    activate_subscribers.short_description = "Activate selected subscribers"

    def deactivate_subscribers(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f'{updated} subscriber(s) deactivated.')
    deactivate_subscribers.short_description = "Deactivate selected subscribers"

    def export_emails(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'

        writer = csv.writer(response)
        writer.writerow(['Email', 'Status', 'Subscribed At', 'Unsubscribed At'])

        for subscriber in queryset:
            writer.writerow([
                subscriber.email,
                'Active' if subscriber.is_active else 'Unsubscribed',
                subscriber.subscribed_at,
                subscriber.unsubscribed_at or ''
            ])

        return response
    export_emails.short_description = "Export selected subscribers to CSV"
