from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import Job
from apps.internships.models import Internship
from apps.categories.models import Category
from django.contrib.auth.models import User
from apps.newsletter.models import Subscriber


def home(request):
    """Home page with real database statistics"""

    # Get date range for last week
    today = timezone.now().date()
    last_week = today - timedelta(days=7)

    # ===== STATS FOR THE 3 CARDS =====
    # 1. Last Week Jobs
    last_week_jobs = Job.objects.filter(
        is_active=True,
        posted_at__date__gte=last_week
    ).count()

    # 2. Last Week Internships
    last_week_internships = Internship.objects.filter(
        is_active=True,
        posted_at__date__gte=last_week
    ).count()

    # 3. Total Categories (Industries Covered)
    total_categories = Category.objects.count()

    # ===== OTHER STATS =====
    total_jobs = Job.objects.filter(is_active=True).count()
    total_internships = Internship.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    total_subscribers = Subscriber.objects.filter(is_active=True).count()

    # ===== LATEST LISTINGS FOR CAROUSEL (JOBS) =====
    full_time_jobs = Job.objects.filter(
        is_active=True,
        employment_type='full_time'
    ).order_by('-posted_at')[:10]

    part_time_jobs = Job.objects.filter(
        is_active=True,
        employment_type='part_time'
    ).order_by('-posted_at')[:10]

    contract_jobs = Job.objects.filter(
        is_active=True,
        employment_type='contract'
    ).order_by('-posted_at')[:10]

    daily_jobs = Job.objects.filter(
        is_active=True,
        employment_type='daily'
    ).order_by('-posted_at')[:10]

    # ===== LATEST LISTINGS FOR CAROUSEL (INTERNSHIPS) =====
    full_time_internships = Internship.objects.filter(
        is_active=True,
        internship_type='full_time'
    ).order_by('-posted_at')[:10]

    part_time_internships = Internship.objects.filter(
        is_active=True,
        internship_type='part_time'
    ).order_by('-posted_at')[:10]

    # ===== LATEST LISTINGS (for other sections) =====
    latest_jobs = Job.objects.filter(is_active=True).order_by('-posted_at')[:32]
    latest_internships = Internship.objects.filter(is_active=True).order_by('-posted_at')[:32]

    # ===== CATEGORIES WITH COUNTS =====
    categories = Category.objects.all()
    for category in categories:
        category.job_count = category.jobs.filter(is_active=True).count()
        category.internship_count = category.internships.filter(is_active=True).count()

    # ===== USER'S SAVED ITEMS =====
    user_saved_jobs = []
    user_saved_internships = []
    if request.user.is_authenticated:
        from apps.jobs.models import SavedJob
        from apps.internships.models import SavedInternship
        user_saved_jobs = SavedJob.objects.filter(
            user=request.user
        ).values_list('job_id', flat=True)
        user_saved_internships = SavedInternship.objects.filter(
            user=request.user
        ).values_list('internship_id', flat=True)

    context = {
        # Stats for the 3 cards
        'last_week_jobs': last_week_jobs,
        'last_week_internships': last_week_internships,
        'total_categories': total_categories,

        # Other stats
        'total_jobs': total_jobs,
        'total_internships': total_internships,
        'total_users': total_users,
        'total_subscribers': total_subscribers,

        # Latest job listings by type (for carousel)
        'full_time_jobs': full_time_jobs,
        'part_time_jobs': part_time_jobs,
        'contract_jobs': contract_jobs,
        'daily_jobs': daily_jobs,

        # Latest internship listings by type (for carousel)
        'full_time_internships': full_time_internships,
        'part_time_internships': part_time_internships,

        # Latest listings (for other sections)
        'latest_jobs': latest_jobs,
        'latest_internships': latest_internships,

        # Categories
        'categories': categories,

        # Date
        'today': today,

        # User saved items
        'user_saved_jobs': user_saved_jobs,
        'user_saved_internships': user_saved_internships,
    }

    return render(request, 'home.html', context)