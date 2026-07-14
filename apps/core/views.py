from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import Job, SavedJob
from apps.internships.models import Internship, SavedInternship
from apps.categories.models import Category
from apps.newsletter.models import Subscriber
from apps.contact.models import ContactMessage
from django.contrib.auth.models import User

def api_statistics(request):
    """Real-time statistics for homepage"""
    total_jobs = Job.objects.filter(is_active=True).count()
    remote_jobs = Job.objects.filter(is_active=True, type='remote').count()
    physical_jobs = Job.objects.filter(is_active=True, type='physical').count()
    total_internships = Internship.objects.filter(is_active=True).count()
    remote_internships = Internship.objects.filter(is_active=True, type='remote').count()
    physical_internships = Internship.objects.filter(is_active=True, type='physical').count()
    total_categories = Category.objects.count()
    total_subscribers = Subscriber.objects.filter(is_active=True).count()
    total_users = User.objects.count()

    # Today's stats
    today = timezone.now().date()
    jobs_today = Job.objects.filter(posted_at__date=today).count()
    internships_today = Internship.objects.filter(posted_at__date=today).count()

    # This week's stats
    week_ago = today - timedelta(days=7)
    jobs_this_week = Job.objects.filter(posted_at__date__gte=week_ago).count()
    internships_this_week = Internship.objects.filter(posted_at__date__gte=week_ago).count()

    # This month's stats
    month_ago = today - timedelta(days=30)
    jobs_this_month = Job.objects.filter(posted_at__date__gte=month_ago).count()
    internships_this_month = Internship.objects.filter(posted_at__date__gte=month_ago).count()

    # Popular categories
    popular_categories = list(Category.objects.annotate(
        job_count=Count('jobs', filter=Q(jobs__is_active=True)),
        internship_count=Count('internships', filter=Q(internships__is_active=True))
    ).order_by('-job_count')[:6].values('name', 'slug', 'icon', 'job_count', 'internship_count'))

    # Recent activity
    recent_jobs = list(Job.objects.filter(is_active=True).order_by('-posted_at')[:5].values(
        'title', 'company', 'slug', 'type', 'posted_at'
    ))

    recent_internships = list(Internship.objects.filter(is_active=True).order_by('-posted_at')[:5].values(
        'title', 'company', 'slug', 'type', 'posted_at'
    ))

    data = {
        'total_jobs': total_jobs,
        'remote_jobs': remote_jobs,
        'physical_jobs': physical_jobs,
        'total_internships': total_internships,
        'remote_internships': remote_internships,
        'physical_internships': physical_internships,
        'total_categories': total_categories,
        'total_subscribers': total_subscribers,
        'total_users': total_users,
        'jobs_today': jobs_today,
        'internships_today': internships_today,
        'jobs_this_week': jobs_this_week,
        'internships_this_week': internships_this_week,
        'jobs_this_month': jobs_this_month,
        'internships_this_month': internships_this_month,
        'popular_categories': popular_categories,
        'recent_jobs': recent_jobs,
        'recent_internships': recent_internships,
    }

    return JsonResponse(data)

def api_admin_dashboard(request):
    """Admin dashboard statistics"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    inactive_jobs = Job.objects.filter(is_active=False).count()

    total_internships = Internship.objects.count()
    active_internships = Internship.objects.filter(is_active=True).count()
    inactive_internships = Internship.objects.filter(is_active=False).count()

    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    new_users_today = User.objects.filter(date_joined__date=timezone.now().date()).count()

    total_contacts = ContactMessage.objects.count()
    unread_contacts = ContactMessage.objects.filter(is_read=False).count()

    total_subscribers = Subscriber.objects.count()
    active_subscribers = Subscriber.objects.filter(is_active=True).count()

    # Jobs by type
    jobs_by_type = list(Job.objects.values('type').annotate(count=Count('id')))
    internships_by_type = list(Internship.objects.values('type').annotate(count=Count('id')))

    # Monthly signups (last 6 months)
    monthly_signups = []
    for i in range(5, -1, -1):
        month = timezone.now().month - i
        year = timezone.now().year
        if month <= 0:
            month += 12
            year -= 1

        count = User.objects.filter(
            date_joined__year=year,
            date_joined__month=month
        ).count()

        monthly_signups.append({
            'month': f"{year}-{month:02d}",
            'count': count
        })

    # Recent activities
    recent_activities = []

    # Recent job posts
    for job in Job.objects.order_by('-posted_at')[:5]:
        recent_activities.append({
            'type': 'job',
            'action': f"New job posted: {job.title}",
            'time': job.posted_at.strftime('%Y-%m-%d %H:%M'),
            'user': 'System'
        })

    # Recent user registrations
    for user in User.objects.order_by('-date_joined')[:5]:
        recent_activities.append({
            'type': 'user',
            'action': f"New user registered: {user.username}",
            'time': user.date_joined.strftime('%Y-%m-%d %H:%M'),
            'user': user.username
        })

    # Recent contact messages
    for contact in ContactMessage.objects.order_by('-created_at')[:5]:
        recent_activities.append({
            'type': 'contact',
            'action': f"New message from: {contact.name}",
            'time': contact.created_at.strftime('%Y-%m-%d %H:%M'),
            'user': contact.name
        })

    # Sort by time
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
        'jobs_by_type': jobs_by_type,
        'internships_by_type': internships_by_type,
        'monthly_signups': monthly_signups,
        'recent_activities': recent_activities[:10],
    }

    return JsonResponse(data)

