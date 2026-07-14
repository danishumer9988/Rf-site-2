from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from apps.categories.models import Category


class Internship(models.Model):
    INTERNSHIP_TYPES = [
        ('physical', 'Physical'),
        ('remote', 'Remote'),
    ]

    INTERNSHIP_EMPLOYMENT_TYPES = [
        ('full_time', 'Full-Time'),
        ('part_time', 'Part-Time'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    stipend = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=20, choices=INTERNSHIP_TYPES)
    internship_type = models.CharField(
        max_length=20,
        choices=INTERNSHIP_EMPLOYMENT_TYPES,
        default='full_time',
        help_text="Full-Time or Part-Time internship"
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='internships')
    apply_url = models.URLField(max_length=500, blank=True)
    company_website = models.URLField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Analytics fields
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)

    # Who posted the internship
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_internships')
    is_user_submitted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['is_active', 'posted_at']),
            models.Index(fields=['type']),
            models.Index(fields=['internship_type']),
            models.Index(fields=['category']),
            models.Index(fields=['company']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.company}")
            slug = base_slug
            counter = 1
            while Internship.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.company} ({self.get_internship_type_display()})"


class SavedInternship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_internships')
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'internship']
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} saved {self.internship.title}"


class InternshipView(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    referer = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.internship.title} - {self.viewed_at}"