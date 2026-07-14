from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read_status', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25

    fieldsets = (
        ('Sender Information', {
            'fields': ('name', 'email')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )

    def is_read_status(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="color: #10B981;">✅ Read</span>'
            )
        return format_html(
            '<span style="color: #EF4444; font-weight: bold;">📬 Unread</span>'
        )
    is_read_status.short_description = 'Status'
    is_read_status.admin_order_field = 'is_read'

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')
    mark_as_unread.short_description = "Mark selected messages as unread"