# apps/jobs/admin.py
from django.contrib import admin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    Job, JobApplication, SavedJob, JobComment, JobLike, JobView,
    JobClick
)


# ============================================================
# JOB ADMIN
# ============================================================

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company', 'location', 'work_type', 'job_type_display',
        'experience_level_display', 'salary_range_display', 'expiry_status_display',
        'is_active', 'posted_at'
    )
    list_filter = (
        'work_type', 'employment_type', 'experience_level', 'category',
        'is_active', 'posted_at', 'company', 'expires_at',
        'payment_method', 'contract_type'
    )
    search_fields = (
        'title', 'company', 'description', 'requirements', 'location'
    )
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'posted_at'
    list_per_page = 25
    readonly_fields = ('posted_at', 'views', 'likes', 'clicks', 'applications_count')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'company', 'location', 'work_type', 'category')
        }),
        ('Content', {
            'fields': ('description', 'requirements')
        }),
        ('Links & Contact', {
            'fields': ('apply_url', 'company_website', 'contact_email', 'contact_phone')
        }),
        ('Status & Expiry', {
            'fields': ('is_active', 'is_featured', 'is_urgent', 'expires_at', 'posted_at', 'updated_at')
        }),
        ('Full Time / Part Time Details', {
            'fields': ('employment_type', 'experience_level', 'salary_min', 'salary_max',
                       'salary_currency', 'salary_period', 'benefits', 'is_remote',
                       'shift_type', 'hours_per_week', 'hourly_rate', 'salary_range',
                       'currency', 'is_flexible_schedule', 'is_weekend_available', 'is_immediate'),
            'classes': ('collapse',)
        }),
        ('Daily Wage Details', {
            'fields': ('payment_method', 'payment_amount', 'start_date', 'end_date',
                       'working_hours', 'is_immediate_joining'),
            'classes': ('collapse',)
        }),
        ('Contract Details', {
            'fields': ('contract_type', 'budget_min', 'budget_max', 'contract_currency',
                       'contract_experience_level', 'duration_type', 'estimated_duration',
                       'contract_start_date', 'contract_end_date', 'is_contract_remote',
                       'is_contract_urgent'),
            'classes': ('collapse',)
        }),
        ('Internship Details', {
            'fields': ('stipend', 'duration', 'internship_type'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('views', 'likes', 'clicks', 'applications_count'),
            'classes': ('collapse',)
        }),
    )

    def job_type_display(self, obj):
        """Display the job type based on which fields are populated"""
        if obj.employment_type == 'full_time':
            return '💼 Full Time'
        elif obj.employment_type == 'part_time':
            return '🕐 Part Time'
        elif obj.payment_method:
            return '⚡ Daily Wage'
        elif obj.contract_type:
            return '📄 Contract'
        elif obj.stipend:
            return '🎓 Internship'
        return '📌 Other'
    job_type_display.short_description = 'Job Type'

    def experience_level_display(self, obj):
        if obj.experience_level:
            return obj.get_experience_level_display()
        elif obj.contract_experience_level:
            return obj.get_contract_experience_level_display()
        return '-'
    experience_level_display.short_description = 'Experience'

    def salary_range_display(self, obj):
        if obj.salary_min and obj.salary_max:
            return f"{obj.salary_currency} {obj.salary_min:,} - {obj.salary_max:,} / {obj.get_salary_period_display()}"
        elif obj.salary_min:
            return f"{obj.salary_currency} {obj.salary_min:,}+ / {obj.get_salary_period_display()}"
        elif obj.salary_max:
            return f"{obj.salary_currency} Up to {obj.salary_max:,} / {obj.get_salary_period_display()}"
        elif obj.hourly_rate:
            return f"{obj.currency} ${obj.hourly_rate}/hr"
        elif obj.payment_amount:
            return f"{obj.currency} ${obj.payment_amount} ({obj.get_payment_method_display()})"
        elif obj.budget_min and obj.budget_max:
            return f"{obj.contract_currency} ${obj.budget_min:,} - ${obj.budget_max:,}"
        elif obj.stipend:
            return f"💰 {obj.stipend}"
        return "Not specified"
    salary_range_display.short_description = 'Compensation'

    def expiry_status_display(self, obj):
        status = obj.expiry_status()
        colors = {
            'active': ('🟢', '#10b981'),
            'expiring_soon': ('🟡', '#f59e0b'),
            'expired': ('🔴', '#ef4444')
        }
        icon, color = colors.get(status, ('⚪', '#6b7280'))

        if obj.expires_at:
            if status == 'expired':
                return format_html(
                    '<span style="color: {}; font-weight: 600;">{} Expired</span>',
                    color, icon
                )
            elif status == 'expiring_soon':
                return format_html(
                    '<span style="color: {}; font-weight: 600;">{} Expiring in {} days</span>',
                    color, icon, obj.days_until_expiry()
                )
            else:
                return format_html(
                    '<span style="color: {}; font-weight: 600;">{} Active ({} days left)</span>',
                    color, icon, obj.days_until_expiry()
                )
        return format_html('<span style="color: #6b7280;">No expiry set</span>')
    expiry_status_display.short_description = 'Expiry Status'

    actions = ['make_active', 'make_inactive', 'extend_expiry']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} job(s) marked as active.')
    make_active.short_description = "Mark selected as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} job(s) marked as inactive.')
    make_inactive.short_description = "Mark selected as inactive"

    def extend_expiry(self, request, queryset):
        count = 0
        for job in queryset:
            if job.expires_at:
                job.expires_at = job.expires_at + timezone.timedelta(days=30)
                job.save()
                count += 1
        self.message_user(request, f'{count} job(s) extended by 30 days.')
    extend_expiry.short_description = "Extend expiry by 30 days"


# ============================================================
# SAVED JOB ADMIN
# ============================================================

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_link', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'user__email', 'job__title', 'job__company')
    raw_id_fields = ('user', 'job')
    date_hierarchy = 'saved_at'
    list_per_page = 50

    def job_link(self, obj):
        return format_html(
            '<a href="/admin/jobs/job/{}/change/">{}</a>',
            obj.job.id, obj.job.title
        )
    job_link.short_description = 'Job'


# ============================================================
# JOB COMMENT ADMIN
# ============================================================

@admin.register(JobComment)
class JobCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'comment_preview', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'job__title', 'comment')
    raw_id_fields = ('user', 'job')
    actions = ['approve_comments', 'reject_comments']

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True, is_read=True)
        self.message_user(request, f'{queryset.count()} comments approved.')
    approve_comments.short_description = "Approve selected comments"

    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} comments rejected.')
    reject_comments.short_description = "Reject selected comments"


# ============================================================
# JOB LIKE ADMIN
# ============================================================

@admin.register(JobLike)
class JobLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'job__title')
    raw_id_fields = ('user', 'job')
    date_hierarchy = 'created_at'
    list_per_page = 50

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'


# ============================================================
# JOB VIEW ADMIN
# ============================================================

@admin.register(JobView)
class JobViewAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'user', 'viewed_at', 'ip_address')
    list_filter = ('viewed_at',)
    search_fields = ('job__title', 'user__username', 'ip_address')
    raw_id_fields = ('job', 'user')
    date_hierarchy = 'viewed_at'
    list_per_page = 50

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'


# ============================================================
# JOB CLICK ADMIN
# ============================================================

@admin.register(JobClick)
class JobClickAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'user', 'link_type', 'clicked_at')
    list_filter = ('link_type', 'clicked_at')
    search_fields = ('job__title', 'user__username', 'ip_address')
    raw_id_fields = ('job', 'user')
    date_hierarchy = 'clicked_at'
    list_per_page = 50

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'


# ============================================================
# JOB APPLICATION ADMIN (User Submitted)
# ============================================================

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company', 'user', 'status', 'published_status',
        'job_type_display', 'submitted_at'
    )
    list_filter = (
        'status', 'work_type', 'employment_type', 'experience_level',
        'payment_method', 'contract_type', 'submitted_at'
    )
    search_fields = ('title', 'company', 'user__username', 'user__email')
    readonly_fields = ('submitted_at', 'updated_at', 'reviewed_at')
    date_hierarchy = 'submitted_at'
    list_per_page = 25

    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'company', 'location', 'work_type', 'category', 'user')
        }),
        ('Content', {
            'fields': ('description', 'requirements')
        }),
        ('Full Time / Part Time Details', {
            'fields': ('employment_type', 'experience_level', 'salary_min', 'salary_max',
                       'salary_currency', 'salary_period', 'benefits', 'is_remote',
                       'shift_type', 'hours_per_week', 'hourly_rate', 'salary_range',
                       'currency', 'is_flexible_schedule', 'is_weekend_available', 'is_immediate')
        }),
        ('Daily Wage Details', {
            'fields': ('payment_method', 'payment_amount', 'start_date', 'end_date',
                       'working_hours', 'is_immediate_joining')
        }),
        ('Contract Details', {
            'fields': ('contract_type', 'budget_min', 'budget_max', 'contract_currency',
                       'contract_experience_level', 'duration_type', 'estimated_duration',
                       'contract_start_date', 'contract_end_date', 'is_contract_remote',
                       'is_contract_urgent')
        }),
        ('Internship Details', {
            'fields': ('stipend', 'duration', 'internship_type')
        }),
        ('Links & Contact', {
            'fields': ('apply_url', 'company_website', 'contact_email', 'contact_phone')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes', 'submitted_at', 'updated_at', 'reviewed_at', 'created_job')
        }),
    )

    def job_type_display(self, obj):
        if obj.employment_type == 'full_time':
            return '💼 Full Time'
        elif obj.employment_type == 'part_time':
            return '🕐 Part Time'
        elif obj.payment_method:
            return '⚡ Daily Wage'
        elif obj.contract_type:
            return '📄 Contract'
        elif obj.stipend:
            return '🎓 Internship'
        return '📌 Other'
    job_type_display.short_description = 'Job Type'

    def published_status(self, obj):
        if obj.created_job:
            return format_html('<span style="color: #10b981; font-weight: 600;">✅ Published</span>')
        elif obj.status == 'approved':
            return format_html('<span style="color: #f59e0b; font-weight: 600;">⏳ Needs Publishing</span>')
        return format_html('<span style="color: #94a3b8;">-</span>')
    published_status.short_description = 'Published?'

    def save_model(self, request, obj, form, change):
        """Auto-publish when status is changed to 'approved'"""
        if obj.status == 'approved' and not obj.created_job:
            try:
                base_slug = slugify(obj.title)
                slug = base_slug
                counter = 1
                while Job.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                # Determine job type and set appropriate fields
                job_data = {
                    'title': obj.title,
                    'slug': slug,
                    'company': obj.company,
                    'location': obj.location,
                    'description': obj.description,
                    'requirements': obj.requirements,
                    'work_type': obj.work_type,
                    'category': obj.category,
                    'apply_url': obj.apply_url,
                    'company_website': obj.company_website,
                    'contact_email': obj.contact_email,
                    'contact_phone': obj.contact_phone,
                    'is_active': True,
                    'posted_by': obj.user,
                    'is_user_submitted': True,
                    'expires_at': timezone.now() + timezone.timedelta(days=30),
                }

                # Full Time / Part Time fields
                if obj.employment_type:
                    job_data['employment_type'] = obj.employment_type
                    job_data['experience_level'] = obj.experience_level
                    job_data['salary_min'] = obj.salary_min
                    job_data['salary_max'] = obj.salary_max
                    job_data['salary_currency'] = obj.salary_currency
                    job_data['salary_period'] = obj.salary_period
                    job_data['benefits'] = obj.benefits
                    job_data['is_remote'] = obj.is_remote
                    job_data['shift_type'] = obj.shift_type
                    job_data['hours_per_week'] = obj.hours_per_week
                    job_data['hourly_rate'] = obj.hourly_rate
                    job_data['salary_range'] = obj.salary_range
                    job_data['currency'] = obj.currency
                    job_data['is_flexible_schedule'] = obj.is_flexible_schedule
                    job_data['is_weekend_available'] = obj.is_weekend_available
                    job_data['is_immediate'] = obj.is_immediate

                # Daily Wage fields
                if obj.payment_method:
                    job_data['payment_method'] = obj.payment_method
                    job_data['payment_amount'] = obj.payment_amount
                    job_data['start_date'] = obj.start_date
                    job_data['end_date'] = obj.end_date
                    job_data['working_hours'] = obj.working_hours
                    job_data['is_immediate_joining'] = obj.is_immediate_joining

                # Contract fields
                if obj.contract_type:
                    job_data['contract_type'] = obj.contract_type
                    job_data['budget_min'] = obj.budget_min
                    job_data['budget_max'] = obj.budget_max
                    job_data['contract_currency'] = obj.contract_currency
                    job_data['contract_experience_level'] = obj.contract_experience_level
                    job_data['duration_type'] = obj.duration_type
                    job_data['estimated_duration'] = obj.estimated_duration
                    job_data['contract_start_date'] = obj.contract_start_date
                    job_data['contract_end_date'] = obj.contract_end_date
                    job_data['is_contract_remote'] = obj.is_contract_remote
                    job_data['is_contract_urgent'] = obj.is_contract_urgent

                # Internship fields
                if obj.stipend:
                    job_data['stipend'] = obj.stipend
                    job_data['duration'] = obj.duration
                    job_data['internship_type'] = obj.internship_type

                job = Job.objects.create(**job_data)
                obj.created_job = job

                messages.success(request, f'✅ Job "{job.title}" auto-published successfully!')

                try:
                    job_type_name = obj.employment_type or 'Job'
                    send_mail(
                        subject=f'Your {job_type_name} "{obj.title}" is Now Live! 🎉',
                        message=f"""
Dear {obj.user.username},

Your {job_type_name.lower()} post "{obj.title}" at {obj.company} has been approved and is now live!

🔗 View your job: /jobs/{job.slug}/

📅 Your job will expire on: {job.expires_at.strftime('%B %d, %Y')}

Best regards,
The Job Reference Hub Team
""",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[obj.contact_email, obj.user.email],
                        fail_silently=True,
                    )
                except:
                    pass

            except Exception as e:
                messages.error(request, f'❌ Error auto-publishing job: {str(e)}')
                return

        super().save_model(request, obj, form, change)

    actions = ['reject_selected']

    def reject_selected(self, request, queryset):
        rejected = 0
        for app in queryset.filter(status='pending'):
            app.status = 'rejected'
            app.reviewed_at = timezone.now()
            app.save()
            rejected += 1
        self.message_user(request, f'❌ {rejected} job(s) rejected.')
    reject_selected.short_description = "Reject Selected Jobs"