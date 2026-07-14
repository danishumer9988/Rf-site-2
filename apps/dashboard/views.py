from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import SavedJob, Job, JobApplication  # Add JobApplication here
from apps.internships.models import SavedInternship, Internship
from apps.accounts.forms import UserUpdateForm, ProfileUpdateForm
from apps.accounts.models import Profile
# Remove this line: from apps.job_applications.models import JobApplication
from apps.contact.models import ContactMessage
from apps.newsletter.models import Subscriber
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import Job, JobView, JobLike, JobComment, JobClick, JobApplication

@login_required
def dashboard_home(request):
    saved_jobs_count = SavedJob.objects.filter(user=request.user).count()
    saved_internships_count = SavedInternship.objects.filter(user=request.user).count()

    recent_saved_jobs = SavedJob.objects.filter(user=request.user)[:5]
    recent_saved_internships = SavedInternship.objects.filter(user=request.user)[:5]

    context = {
        'saved_jobs_count': saved_jobs_count,
        'saved_internships_count': saved_internships_count,
        'recent_saved_jobs': recent_saved_jobs,
        'recent_saved_internships': recent_saved_internships,
    }

    return render(request, 'dashboard/dashboard_home.html', context)

@login_required
def dashboard_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'dashboard/profile.html', context)

@login_required
def dashboard_saved_jobs(request):
    saved_jobs = SavedJob.objects.filter(user=request.user)
    return render(request, 'dashboard/saved_jobs.html', {'saved_jobs': saved_jobs})

@login_required
def dashboard_saved_internships(request):
    saved_internships = SavedInternship.objects.filter(user=request.user)
    return render(request, 'dashboard/saved_internships.html', {
        'saved_internships': saved_internships
    })

@login_required
def dashboard_settings(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('dashboard_settings')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'dashboard/settings.html', {'form': form})


# ========== API ENDPOINTS ==========

def api_pending_applications(request):
    """Get pending job applications for admin dashboard"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        pending = JobApplication.objects.filter(status='pending').order_by('-submitted_at')[:10]
        applications = []

        for app in pending:
            applications.append({
                'id': app.id,
                'title': app.title,
                'company': app.company,
                'user': app.user.username,
                'submitted_at': app.submitted_at.strftime('%Y-%m-%d %H:%M'),
            })

        return JsonResponse({'applications': applications})

    except Exception as e:
        return JsonResponse({'error': str(e), 'applications': []}, status=500)

def api_admin_stats(request):
    """Admin dashboard statistics"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(is_active=True).count()
        inactive_jobs = Job.objects.filter(is_active=False).count()

        total_internships = Internship.objects.count()
        active_internships = Internship.objects.filter(is_active=True).count()
        inactive_internships = Internship.objects.filter(is_active=False).count()

        total_users = User.objects.count()
        staff_users = User.objects.filter(is_staff=True).count()
        new_users_today = User.objects.filter(date_joined__date=today).count()

        total_contacts = ContactMessage.objects.count()
        unread_contacts = ContactMessage.objects.filter(is_read=False).count()

        total_subscribers = Subscriber.objects.count()
        active_subscribers = Subscriber.objects.filter(is_active=True).count()

        pending_applications = JobApplication.objects.filter(status='pending').count()

        recent_activities = []

        for job in Job.objects.order_by('-posted_at')[:3]:
            recent_activities.append({
                'type': 'job',
                'action': f'New job posted: {job.title} at {job.company}',
                'time': job.posted_at.strftime('%Y-%m-%d %H:%M'),
            })

        for internship in Internship.objects.order_by('-posted_at')[:3]:
            recent_activities.append({
                'type': 'internship',
                'action': f'New internship posted: {internship.title} at {internship.company}',
                'time': internship.posted_at.strftime('%Y-%m-%d %H:%M'),
            })

        for app in JobApplication.objects.order_by('-submitted_at')[:3]:
            recent_activities.append({
                'type': 'application',
                'action': f'Job application submitted: {app.title} by {app.user.username}',
                'time': app.submitted_at.strftime('%Y-%m-%d %H:%M'),
            })

        for user in User.objects.order_by('-date_joined')[:3]:
            recent_activities.append({
                'type': 'user',
                'action': f'New user registered: {user.username}',
                'time': user.date_joined.strftime('%Y-%m-%d %H:%M'),
            })

        for contact in ContactMessage.objects.order_by('-created_at')[:3]:
            recent_activities.append({
                'type': 'contact',
                'action': f'New contact message from: {contact.name}',
                'time': contact.created_at.strftime('%Y-%m-%d %H:%M'),
            })

        recent_activities.sort(key=lambda x: x['time'], reverse=True)

        data = {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'inactive_jobs': inactive_jobs,
            'total_internships': total_internships,
            'active_internships': active_internships,
            'inactive_internships': inactive_internships,
            'total_users': total_users,
            'staff_users': staff_users,
            'new_users_today': new_users_today,
            'total_contacts': total_contacts,
            'unread_contacts': unread_contacts,
            'total_subscribers': total_subscribers,
            'active_subscribers': active_subscribers,
            'pending_applications': pending_applications,
            'recent_activities': recent_activities[:10],
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def user_analytics(request):
    """User analytics dashboard for job posters"""

    # Get user's jobs
    jobs = Job.objects.filter(posted_by=request.user)

    # Date filtering
    period = request.GET.get('period', '30')
    if period == 'all':
        days = 365 * 10
    else:
        days = int(period)

    start_date = timezone.now() - timedelta(days=days)

    # Filter jobs by date
    jobs_filtered = jobs.filter(posted_at__gte=start_date)

    # KPI Calculations
    total_views = jobs_filtered.aggregate(Sum('views'))['views__sum'] or 0
    total_clicks = jobs_filtered.aggregate(Sum('clicks'))['clicks__sum'] or 0
    total_likes = jobs_filtered.aggregate(Sum('likes'))['likes__sum'] or 0
    total_comments = JobComment.objects.filter(job__in=jobs_filtered, is_approved=True).count()
    total_applications = jobs_filtered.aggregate(Sum('applications_count'))['applications_count__sum'] or 0
    total_saves = jobs_filtered.aggregate(Sum('saved_by'))['saved_by__sum'] or 0

    # This week's metrics
    week_ago = timezone.now() - timedelta(days=7)
    jobs_week = jobs.filter(posted_at__gte=week_ago)
    views_this_week = jobs_week.aggregate(Sum('views'))['views__sum'] or 0
    clicks_this_week = jobs_week.aggregate(Sum('clicks'))['clicks__sum'] or 0
    likes_this_week = jobs_week.aggregate(Sum('likes'))['likes__sum'] or 0
    comments_this_week = JobComment.objects.filter(job__in=jobs_week, is_approved=True).count()
    applications_this_week = jobs_week.aggregate(Sum('applications_count'))['applications_count__sum'] or 0
    saves_this_week = jobs_week.aggregate(Sum('saved_by'))['saved_by__sum'] or 0

    # Growth calculations (compare with previous period)
    previous_start = start_date - timedelta(days=days)
    jobs_previous = jobs.filter(posted_at__gte=previous_start, posted_at__lt=start_date)

    def calc_growth(current, previous):
        if previous == 0:
            return 0 if current == 0 else 100
        return round(((current - previous) / previous) * 100, 1)

    views_previous = jobs_previous.aggregate(Sum('views'))['views__sum'] or 0
    clicks_previous = jobs_previous.aggregate(Sum('clicks'))['clicks__sum'] or 0
    likes_previous = jobs_previous.aggregate(Sum('likes'))['likes__sum'] or 0
    comments_previous = JobComment.objects.filter(job__in=jobs_previous, is_approved=True).count()
    applications_previous = jobs_previous.aggregate(Sum('applications_count'))['applications_count__sum'] or 0
    saves_previous = jobs_previous.aggregate(Sum('saved_by'))['saved_by__sum'] or 0

    # Chart data
    chart_dates = []
    views_data = []
    clicks_data = []

    for i in range(min(30, days)):
        date = timezone.now().date() - timedelta(days=i)
        day_jobs = jobs.filter(posted_at__date=date)
        chart_dates.append(date.strftime('%b %d'))
        views_data.append(day_jobs.aggregate(Sum('views'))['views__sum'] or 0)
        clicks_data.append(day_jobs.aggregate(Sum('clicks'))['clicks__sum'] or 0)

    # Top jobs
    top_jobs = jobs.order_by('-views')[:10]

    context = {
        # KPI Numbers
        'total_views': total_views,
        'total_clicks': total_clicks,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_applications': total_applications,
        'total_saves': total_saves,

        # This Week
        'views_this_week': views_this_week,
        'clicks_this_week': clicks_this_week,
        'likes_this_week': likes_this_week,
        'comments_this_week': comments_this_week,
        'applications_this_week': applications_this_week,
        'saves_this_week': saves_this_week,

        # Growth
        'views_growth': calc_growth(views_this_week, views_previous),
        'clicks_growth': calc_growth(clicks_this_week, clicks_previous),
        'likes_growth': calc_growth(likes_this_week, likes_previous),
        'comments_growth': calc_growth(comments_this_week, comments_previous),
        'applications_growth': calc_growth(applications_this_week, applications_previous),
        'saves_growth': calc_growth(saves_this_week, saves_previous),

        # Charts
        'views_data': {
            'labels': chart_dates[::-1],
            'data': views_data[::-1]
        },
        'clicks_data': {
            'labels': chart_dates[::-1],
            'data': clicks_data[::-1]
        },

        # Top Jobs
        'top_jobs': top_jobs,

        # Sidebar counts
        'saved_jobs_count': request.user.saved_jobs.count(),
        'saved_internships_count': request.user.saved_internships.count(),
    }

    return render(request, 'dashboard/analytics.html', context)