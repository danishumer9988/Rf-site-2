from django.contrib import admin
from django.utils.html import format_html
from .models import Internship, SavedInternship, InternshipView


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'type_badge', 'internship_type_badge', 'category', 'duration', 'is_active', 'posted_at')
    list_filter = ('type', 'internship_type', 'category', 'is_active', 'posted_at', 'company', 'duration')
    search_fields = ('title', 'company', 'description', 'requirements', 'location')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'posted_at'
    list_per_page = 25
    readonly_fields = ('posted_at', 'views', 'likes', 'clicks', 'applications_count', 'field_purpose')

    # ----------------------------------------------
    # FIELDSETS – organised and with purpose note
    # ----------------------------------------------
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'company', 'location', 'type', 'internship_type', 'category')
        }),
        ('Content', {
            'fields': ('description', 'requirements')
        }),
        ('Internship Details', {
            'fields': ('stipend', 'duration', 'apply_url', 'company_website')
        }),
        ('Status & Timeline', {
            'fields': ('is_active', 'posted_at', 'expires_at'),
            'classes': ('wide',)
        }),
        ('Analytics', {
            'fields': ('views', 'likes', 'clicks', 'applications_count'),
            'classes': ('wide',)
        }),
        # ---- Purpose note at the bottom ----
        ('📖 Purpose of Fields', {
            'fields': ('field_purpose',),
            'classes': ('collapse',),
        }),
    )

    # ----------------------------------------------
    # CUSTOM METHOD FOR PURPOSE NOTE
    # ----------------------------------------------
    def field_purpose(self, obj):
        return format_html("""
            <div style="background: #f8f9fa; padding: 15px 20px; border-radius: 8px; border-left: 4px solid #2563eb; margin: 5px 0;">
                <h4 style="margin-top:0; color: #1e293b;">Why these fields?</h4>
                <ul style="margin-bottom:0; padding-left:20px; line-height:1.8;">
                    <li><strong>Type</strong> – Remote or Physical – indicates where the internship takes place.</li>
                    <li><strong>Internship Type</strong> – Full-Time or Part-Time – defines the weekly commitment.</li>
                    <li><strong>Stipend</strong> – The financial compensation (monthly, fixed, or range).</li>
                    <li><strong>Duration</strong> – How long the internship lasts (e.g., 3 months, 6 months).</li>
                    <li><strong>Apply URL</strong> – Link where candidates can apply directly.</li>
                    <li><strong>Company Website</strong> – For additional company information.</li>
                </ul>
            </div>
        """)
    field_purpose.short_description = ''

    # ----------------------------------------------
    # CUSTOM DISPLAY METHODS
    # ----------------------------------------------

    def type_badge(self, obj):
        colors = {
            'remote': '#8B5CF6',
            'physical': '#F59E0B'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{}</span>',
            colors.get(obj.type, '#6B7280'),
            obj.get_type_display()
        )
    type_badge.short_description = 'Type'
    type_badge.admin_order_field = 'type'

    def internship_type_badge(self, obj):
        colors = {
            'full_time': '#2563EB',
            'part_time': '#F59E0B'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{}</span>',
            colors.get(obj.internship_type, '#6B7280'),
            obj.get_internship_type_display()
        )
    internship_type_badge.short_description = 'Employment Type'
    internship_type_badge.admin_order_field = 'internship_type'

    # ----------------------------------------------
    # ACTIONS
    # ----------------------------------------------

    actions = ['make_active', 'make_inactive', 'mark_as_remote', 'mark_as_physical', 'mark_as_full_time', 'mark_as_part_time']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} internship(s) marked as active.')
    make_active.short_description = "Mark selected internships as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} internship(s) marked as inactive.')
    make_inactive.short_description = "Mark selected internships as inactive"

    def mark_as_remote(self, request, queryset):
        updated = queryset.update(type='remote')
        self.message_user(request, f'{updated} internship(s) marked as remote.')
    mark_as_remote.short_description = "Mark selected as remote"

    def mark_as_physical(self, request, queryset):
        updated = queryset.update(type='physical')
        self.message_user(request, f'{updated} internship(s) marked as physical.')
    mark_as_physical.short_description = "Mark selected as physical"

    def mark_as_full_time(self, request, queryset):
        updated = queryset.update(internship_type='full_time')
        self.message_user(request, f'{updated} internship(s) marked as full-time.')
    mark_as_full_time.short_description = "Mark selected as full-time"

    def mark_as_part_time(self, request, queryset):
        updated = queryset.update(internship_type='part_time')
        self.message_user(request, f'{updated} internship(s) marked as part-time.')
    mark_as_part_time.short_description = "Mark selected as part-time"


@admin.register(SavedInternship)
class SavedInternshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'internship_link', 'saved_at')
    list_filter = ('saved_at', 'internship__type', 'internship__internship_type', 'internship__category')
    search_fields = ('user__username', 'user__email', 'internship__title', 'internship__company')
    raw_id_fields = ('user', 'internship')
    date_hierarchy = 'saved_at'
    list_per_page = 50

    def internship_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:internships_internship_change', args=[obj.internship.id])
        return format_html('<a href="{}">{}</a>', url, obj.internship.title)
    internship_link.short_description = 'Internship'
    internship_link.admin_order_field = 'internship__title'


@admin.register(InternshipView)
class InternshipViewAdmin(admin.ModelAdmin):
    list_display = ('internship', 'user', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('internship__title', 'internship__company', 'user__username', 'ip_address')
    readonly_fields = ('viewed_at',)
    date_hierarchy = 'viewed_at'
    list_per_page = 50