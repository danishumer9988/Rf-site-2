from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import Job, SavedJob
from apps.internships.models import Internship, SavedInternship
from apps.categories.models import Category
from django.db.models import Count, Q

def home_view(request):
    """Homepage with real statistics"""
    today = timezone.now().date()

    # Get the most recent post time from jobs or internships
    latest_job = Job.objects.filter(is_active=True).order_by('-posted_at').first()
    latest_internship = Internship.objects.filter(is_active=True).order_by('-posted_at').first()

    # Determine the most recent update time
    if latest_job and latest_internship:
        last_updated = max(latest_job.posted_at, latest_internship.posted_at)
    elif latest_job:
        last_updated = latest_job.posted_at
    elif latest_internship:
        last_updated = latest_internship.posted_at
    else:
        # If no jobs or internships, use current time
        last_updated = timezone.now()

    # ✅ SHOW 20 ITEMS (4 per row = 5 rows)
    latest_jobs = Job.objects.filter(is_active=True).order_by('-posted_at')[:20]
    latest_internships = Internship.objects.filter(is_active=True).order_by('-posted_at')[:20]

    categories = Category.objects.annotate(
        job_count=Count('jobs', filter=Q(jobs__is_active=True)),
        internship_count=Count('internships', filter=Q(internships__is_active=True))
    ).order_by('-job_count')

    user_saved_jobs = []
    user_saved_internships = []
    if request.user.is_authenticated:
        user_saved_jobs = list(SavedJob.objects.filter(
            user=request.user
        ).values_list('job_id', flat=True))
        user_saved_internships = list(SavedInternship.objects.filter(
            user=request.user
        ).values_list('internship_id', flat=True))

    context = {
        'latest_jobs': latest_jobs,  # ✅ 20 jobs
        'latest_internships': latest_internships,  # ✅ 20 internships
        'categories': categories,
        'user_saved_jobs': user_saved_jobs,
        'user_saved_internships': user_saved_internships,
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'total_internships': Internship.objects.filter(is_active=True).count(),
        'total_remote_jobs': Job.objects.filter(is_active=True, type='remote').count(),
        'today': today,
        'last_updated': last_updated,
    }

    return render(request, 'home.html', context)