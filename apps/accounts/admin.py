from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'email_verified_status', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    def email_verified_status(self, obj):
        if hasattr(obj, 'profile'):
            if obj.profile.email_verified:
                return "✅ Verified"
            return "❌ Not Verified"
        return "-"
    email_verified_status.short_description = 'Email Verified'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type_display', 'phone_number', 'email_verified_display', 'created_at')
    list_filter = ('user_type', 'email_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'first_name', 'last_name')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'phone_number', 'user_type', 'bio', 'location')
        }),
        ('Social Links', {
            'fields': ('website', 'linkedin', 'github'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('email_verified', 'verification_code', 'verification_code_created_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'verification_code', 'verification_code_created_at')

    def user_type_display(self, obj):
        if obj.user_type:
            return obj.get_user_type_display()
        return '-'
    user_type_display.short_description = 'User Type'

    def email_verified_display(self, obj):
        if obj.email_verified:
            return "✅ Verified"
        return "❌ Not Verified"
    email_verified_display.short_description = 'Email Verified'