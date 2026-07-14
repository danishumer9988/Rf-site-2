# apps/jobs/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from apps.categories.models import Category


# ============================================================
# CHOICES
# ============================================================

WORK_TYPE_CHOICES = [
    ('physical', 'On-Site'),
    ('remote', 'Remote'),
]

EMPLOYMENT_TYPE_CHOICES = [
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('contract', 'Contract'),
    ('freelance', 'Freelance'),
    ('temporary', 'Temporary'),
]

EXPERIENCE_LEVEL_CHOICES = [
    ('entry', 'Entry Level (0-2 years)'),
    ('mid', 'Mid Level (2-5 years)'),
    ('senior', 'Senior Level (5-8 years)'),
    ('lead', 'Lead/Manager (8+ years)'),
    ('executive', 'Executive (10+ years)'),
]

PAYMENT_METHOD_CHOICES = [
    ('hourly', 'Hourly'),
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
]

CONTRACT_TYPE_CHOICES = [
    ('fixed', 'Fixed Price'),
    ('hourly', 'Hourly Rate'),
    ('milestone', 'Milestone Based'),
]

DURATION_TYPE_CHOICES = [
    ('short', 'Short Term (1-3 months)'),
    ('medium', 'Medium Term (3-6 months)'),
    ('long', 'Long Term (6+ months)'),
    ('ongoing', 'Ongoing'),
]

SHIFT_TYPE_CHOICES = [
    ('morning', 'Morning Shift'),
    ('afternoon', 'Afternoon Shift'),
    ('evening', 'Evening Shift'),
    ('night', 'Night Shift'),
    ('flexible', 'Flexible'),
    ('weekend', 'Weekend Only'),
]


# ============================================================
# JOB (UNIFIED MODEL)
# ============================================================

class Job(models.Model):
    # ===== Common Fields =====
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True)

    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, default='physical')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='jobs')

    apply_url = models.URLField(max_length=500, blank=True)
    company_website = models.URLField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    # ===== Status =====
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # ===== Analytics =====
    views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)

    # ===== Who posted =====
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_jobs')
    is_user_submitted = models.BooleanField(default=False)

    # ===== FULL TIME JOB FIELDS =====
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, blank=True, null=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True, null=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD', blank=True)
    salary_period = models.CharField(max_length=20, choices=[('yearly', 'Per Year'), ('monthly', 'Per Month')], default='yearly', blank=True)
    benefits = models.TextField(blank=True, help_text="List benefits like health insurance, 401k, etc.")
    is_remote = models.BooleanField(default=False)

    # ===== PART TIME JOB FIELDS =====
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES, blank=True, null=True)
    hours_per_week = models.PositiveIntegerField(null=True, blank=True, help_text="Hours per week")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_range = models.CharField(max_length=100, blank=True, help_text="e.g., $15-20/hour")
    currency = models.CharField(max_length=3, default='USD', blank=True)
    is_flexible_schedule = models.BooleanField(default=False)
    is_weekend_available = models.BooleanField(default=False)
    is_immediate = models.BooleanField(default=False)

    # ===== DAILY WAGE JOB FIELDS =====
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    working_hours = models.CharField(max_length=100, blank=True, help_text="e.g., 9 AM - 5 PM")
    is_immediate_joining = models.BooleanField(default=False)

    # ===== CONTRACT JOB FIELDS =====
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES, blank=True, null=True)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    contract_currency = models.CharField(max_length=3, default='USD', blank=True)
    contract_experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True, null=True)
    duration_type = models.CharField(max_length=20, choices=DURATION_TYPE_CHOICES, blank=True, null=True)
    estimated_duration = models.CharField(max_length=100, blank=True, help_text="e.g., 3 months, 6 months")
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    is_contract_remote = models.BooleanField(default=False)
    is_contract_urgent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-posted_at']
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        indexes = [
            models.Index(fields=['is_active', 'posted_at']),
            models.Index(fields=['work_type']),
            models.Index(fields=['category']),
            models.Index(fields=['company']),
            models.Index(fields=['employment_type']),
            models.Index(fields=['expires_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.company}"

    # ========== EXPIRY METHODS ==========
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def days_until_expiry(self):
        if not self.expires_at:
            return None
        diff = self.expires_at - timezone.now()
        return diff.days

    def expiry_status(self):
        if not self.expires_at:
            return 'active'
        now = timezone.now()
        if now > self.expires_at:
            return 'expired'
        elif now > self.expires_at - timezone.timedelta(days=3):
            return 'expiring_soon'
        else:
            return 'active'

    # ========== ANALYTICS METHODS ==========
    def increment_views(self):
        self.views += 1
        self.save()

    def increment_like(self):
        self.likes += 1
        self.save()

    def decrement_like(self):
        if self.likes > 0:
            self.likes -= 1
            self.save()


# ============================================================
# JOB VIEW
# ============================================================

class JobView(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.job.title} - {self.viewed_at}"


# ============================================================
# JOB LIKE
# ============================================================

class JobLike(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='likes_log')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['job', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} liked {self.job.title}"


# ============================================================
# JOB COMMENT
# ============================================================

class JobComment(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} on {self.job.title}"


# ============================================================
# JOB CLICK
# ============================================================

class JobClick(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='click_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    link_type = models.CharField(max_length=20, choices=[
        ('apply', 'Apply Link'),
        ('website', 'Company Website')
    ])
    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.title} - {self.link_type} click"


# ============================================================
# SAVED JOB
# ============================================================

class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'job']
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


# ============================================================
# JOB APPLICATION (User Submitted)
# ============================================================

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')

    # ===== Common Fields =====
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, default='physical')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    apply_url = models.URLField(max_length=500, blank=True)
    company_website = models.URLField(max_length=200, blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Notes from admin")
    created_job = models.OneToOneField(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_application'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # ===== FULL TIME FIELDS =====
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, blank=True, null=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True, null=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD', blank=True)
    salary_period = models.CharField(max_length=20, choices=[('yearly', 'Per Year'), ('monthly', 'Per Month')], default='yearly', blank=True)
    benefits = models.TextField(blank=True)
    is_remote = models.BooleanField(default=False)

    # ===== PART TIME FIELDS =====
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES, blank=True, null=True)
    hours_per_week = models.PositiveIntegerField(null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3, default='USD', blank=True)
    is_flexible_schedule = models.BooleanField(default=False)
    is_weekend_available = models.BooleanField(default=False)
    is_immediate = models.BooleanField(default=False)

    # ===== DAILY WAGE FIELDS =====
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    working_hours = models.CharField(max_length=100, blank=True)
    is_immediate_joining = models.BooleanField(default=False)

    # ===== CONTRACT FIELDS =====
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES, blank=True, null=True)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    contract_currency = models.CharField(max_length=3, default='USD', blank=True)
    contract_experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True, null=True)
    duration_type = models.CharField(max_length=20, choices=DURATION_TYPE_CHOICES, blank=True, null=True)
    estimated_duration = models.CharField(max_length=100, blank=True)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    is_contract_remote = models.BooleanField(default=False)
    is_contract_urgent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'

    def save(self, *args, **kwargs):
        if not self.slug:
            import time
            self.slug = slugify(f"{self.title}-{int(time.time())}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.company} ({self.user.username})"