from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models.functions import TruncDate, TruncMonth
import json

from apps.jobs.models import Job, SavedJob, JobApplication, JobView, JobLike, JobComment
from apps.jobs.forms import JobForm
from apps.internships.models import Internship, SavedInternship
from apps.internships.forms import InternshipForm
from apps.categories.models import Category
from apps.categories.forms import CategoryForm
from apps.newsletter.models import Subscriber
from apps.contact.models import ContactMessage
from django.contrib.auth.models import User


def is_admin(user):
    return user.is_authenticated and user.is_staff


# ========== MAIN DASHBOARD ==========

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard with all statistics"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Get all statistics
    context = {
        # Job Stats
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(is_active=True).count(),
        'inactive_jobs': Job.objects.filter(is_active=False).count(),
        'jobs_today': Job.objects.filter(posted_at__date=today).count(),
        'jobs_week': Job.objects.filter(posted_at__date__gte=week_ago).count(),
        'jobs_month': Job.objects.filter(posted_at__date__gte=month_ago).count(),

        # Job Analytics
        'total_job_views': Job.objects.aggregate(Sum('views'))['views__sum'] or 0,
        'total_job_likes': Job.objects.aggregate(Sum('likes'))['likes__sum'] or 0,
        'total_job_clicks': Job.objects.aggregate(Sum('clicks'))['clicks__sum'] or 0,
        'total_job_comments': JobComment.objects.filter(is_approved=True).count(),

        # Internship Stats
        'total_internships': Internship.objects.count(),
        'active_internships': Internship.objects.filter(is_active=True).count(),
        'inactive_internships': Internship.objects.filter(is_active=False).count(),
        'internships_today': Internship.objects.filter(posted_at__date=today).count(),
        'internships_week': Internship.objects.filter(posted_at__date__gte=week_ago).count(),
        'internships_month': Internship.objects.filter(posted_at__date__gte=month_ago).count(),

        # User Stats
        'total_users': User.objects.count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
        'new_users_today': User.objects.filter(date_joined__date=today).count(),
        'new_users_week': User.objects.filter(date_joined__date__gte=week_ago).count(),
        'new_users_month': User.objects.filter(date_joined__date__gte=month_ago).count(),

        # Job Application Stats
        'pending_applications': JobApplication.objects.filter(status='pending').count(),
        'approved_applications': JobApplication.objects.filter(status='approved').count(),
        'rejected_applications': JobApplication.objects.filter(status='rejected').count(),
        'total_applications': JobApplication.objects.count(),

        # Contact & Subscriber Stats
        'total_contacts': ContactMessage.objects.count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        'read_messages': ContactMessage.objects.filter(is_read=True).count(),
        'total_subscribers': Subscriber.objects.count(),
        'active_subscribers': Subscriber.objects.filter(is_active=True).count(),
        'inactive_subscribers': Subscriber.objects.filter(is_active=False).count(),

        # Category Stats
        'total_categories': Category.objects.count(),

        # Saved Items Stats
        'total_saved_jobs': SavedJob.objects.count(),
        'total_saved_internships': SavedInternship.objects.count(),

        # Job Types Distribution
        'remote_jobs': Job.objects.filter(work_type='remote', is_active=True).count(),
        'physical_jobs': Job.objects.filter(work_type='physical', is_active=True).count(),
        'remote_internships': Internship.objects.filter(type='remote', is_active=True).count(),
        'physical_internships': Internship.objects.filter(type='physical', is_active=True).count(),

        # Daily Views Chart Data (last 30 days)
        'daily_views_data': get_daily_views_data(),

        # Monthly Signups Chart Data
        'monthly_signups_data': get_monthly_signups_data(),

        # Recent Activities
        'recent_activities': get_recent_activities(),

        # Top Categories
        'top_categories': get_top_categories(),

        # Recent Job Applications
        'recent_applications': JobApplication.objects.select_related('user').order_by('-submitted_at')[:10],

        # Recent Jobs
        'recent_jobs': Job.objects.order_by('-posted_at')[:10],

        # Recent Users
        'recent_users': User.objects.order_by('-date_joined')[:10],

        # Unread Messages
        'recent_messages': ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:10],

        # Today's Date
        'today': today,
    }

    return render(request, 'dashboard/admin/dashboard.html', context)


def get_daily_views_data():
    """Get daily views for the last 30 days"""
    data = {}
    today = timezone.now().date()

    for i in range(30):
        date = today - timedelta(days=i)
        count = JobView.objects.filter(viewed_at__date=date).count()
        data[date.strftime('%Y-%m-%d')] = count

    return data


def get_monthly_signups_data():
    """Get monthly user signups for the last 6 months"""
    data = []
    now = timezone.now()

    for i in range(5, -1, -1):
        month = now.month - i
        year = now.year

        if month <= 0:
            month += 12
            year -= 1

        count = User.objects.filter(
            date_joined__year=year,
            date_joined__month=month
        ).count()

        data.append({
            'month': f"{year}-{month:02d}",
            'count': count,
            'label': datetime(year, month, 1).strftime('%b %Y')
        })

    return data


def get_recent_activities(limit=20):
    """Get recent activities across the platform"""
    activities = []

    # New Job Posts
    for job in Job.objects.order_by('-posted_at')[:5]:
        activities.append({
            'type': 'job',
            'icon': '💼',
            'action': f'New job posted: <strong>{job.title}</strong> at {job.company}',
            'time': job.posted_at.strftime('%Y-%m-%d %H:%M'),
            'time_ago': time_ago(job.posted_at),
            'url': f'/jobs/{job.slug}/'
        })

    # New Internship Posts
    for internship in Internship.objects.order_by('-posted_at')[:5]:
        activities.append({
            'type': 'internship',
            'icon': '🎓',
            'action': f'New internship posted: <strong>{internship.title}</strong> at {internship.company}',
            'time': internship.posted_at.strftime('%Y-%m-%d %H:%M'),
            'time_ago': time_ago(internship.posted_at),
            'url': f'/internships/{internship.slug}/'
        })

    # New User Registrations
    for user in User.objects.order_by('-date_joined')[:5]:
        activities.append({
            'type': 'user',
            'icon': '👤',
            'action': f'New user registered: <strong>{user.username}</strong>',
            'time': user.date_joined.strftime('%Y-%m-%d %H:%M'),
            'time_ago': time_ago(user.date_joined),
            'url': f'/admin/auth/user/{user.id}/change/'
        })

    # New Contact Messages
    for contact in ContactMessage.objects.order_by('-created_at')[:5]:
        activities.append({
            'type': 'contact',
            'icon': '📧',
            'action': f'New message from: <strong>{contact.name}</strong> - {contact.subject}',
            'time': contact.created_at.strftime('%Y-%m-%d %H:%M'),
            'time_ago': time_ago(contact.created_at),
            'url': f'/admin/contact/contactmessage/{contact.id}/change/'
        })

    # New Job Applications
    for app in JobApplication.objects.order_by('-submitted_at')[:5]:
        activities.append({
            'type': 'application',
            'icon': '📝',
            'action': f'Job application submitted: <strong>{app.title}</strong> by {app.user.username}',
            'time': app.submitted_at.strftime('%Y-%m-%d %H:%M'),
            'time_ago': time_ago(app.submitted_at),
            'url': f'/admin/jobs/jobapplication/{app.id}/change/'
        })

    # Sort by time and limit
    activities.sort(key=lambda x: x['time'], reverse=True)
    return activities[:limit]


def get_top_categories(limit=10):
    """Get top categories by job and internship count"""
    categories = Category.objects.annotate(
        job_count=Count('jobs', filter=Q(jobs__is_active=True)),
        internship_count=Count('internships', filter=Q(internships__is_active=True)),
        total_count=Count('jobs', filter=Q(jobs__is_active=True)) + Count('internships', filter=Q(internships__is_active=True))
    ).order_by('-total_count')[:limit]

    return categories


def time_ago(dt):
    """Convert datetime to 'time ago' string"""
    now = timezone.now()
    diff = now - dt

    if diff.days > 365:
        return f"{diff.days // 365} years ago"
    elif diff.days > 30:
        return f"{diff.days // 30} months ago"
    elif diff.days > 7:
        return f"{diff.days // 7} weeks ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "Just now"


# ========== ANALYTICS VIEW ==========

@login_required
@user_passes_test(is_admin)
def admin_analytics(request):
    """Advanced analytics dashboard"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    quarter_ago = today - timedelta(days=90)

    context = {
        # Jobs Analytics
        'jobs_today': Job.objects.filter(posted_at__date=today).count(),
        'jobs_week': Job.objects.filter(posted_at__date__gte=week_ago).count(),
        'jobs_month': Job.objects.filter(posted_at__date__gte=month_ago).count(),
        'jobs_quarter': Job.objects.filter(posted_at__date__gte=quarter_ago).count(),
        'total_jobs': Job.objects.count(),
        'active_jobs_percent': calculate_percentage(Job.objects.filter(is_active=True).count(), Job.objects.count()),

        # Internships Analytics
        'internships_today': Internship.objects.filter(posted_at__date=today).count(),
        'internships_week': Internship.objects.filter(posted_at__date__gte=week_ago).count(),
        'internships_month': Internship.objects.filter(posted_at__date__gte=month_ago).count(),
        'internships_quarter': Internship.objects.filter(posted_at__date__gte=quarter_ago).count(),
        'total_internships': Internship.objects.count(),
        'active_internships_percent': calculate_percentage(Internship.objects.filter(is_active=True).count(), Internship.objects.count()),

        # User Growth
        'new_users_today': User.objects.filter(date_joined__date=today).count(),
        'new_users_week': User.objects.filter(date_joined__date__gte=week_ago).count(),
        'new_users_month': User.objects.filter(date_joined__date__gte=month_ago).count(),
        'new_users_quarter': User.objects.filter(date_joined__date__gte=quarter_ago).count(),
        'total_users': User.objects.count(),

        # Engagement
        'total_job_views': Job.objects.aggregate(Sum('views'))['views__sum'] or 0,
        'total_job_likes': Job.objects.aggregate(Sum('likes'))['likes__sum'] or 0,
        'total_job_clicks': Job.objects.aggregate(Sum('clicks'))['clicks__sum'] or 0,
        'total_job_comments': JobComment.objects.filter(is_approved=True).count(),
        'avg_views_per_job': calculate_avg(Job.objects.aggregate(Avg('views'))['views__avg']),
        'avg_likes_per_job': calculate_avg(Job.objects.aggregate(Avg('likes'))['likes__avg']),

        # Applications
        'pending_applications': JobApplication.objects.filter(status='pending').count(),
        'approved_applications': JobApplication.objects.filter(status='approved').count(),
        'rejected_applications': JobApplication.objects.filter(status='rejected').count(),
        'approval_rate': calculate_percentage(
            JobApplication.objects.filter(status='approved').count(),
            JobApplication.objects.exclude(status='pending').count()
        ),

        # Saved Items
        'saved_jobs_count': SavedJob.objects.count(),
        'saved_internships_count': SavedInternship.objects.count(),
        'total_saved_items': SavedJob.objects.count() + SavedInternship.objects.count(),

        # Communications
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        'read_messages': ContactMessage.objects.filter(is_read=True).count(),
        'total_messages': ContactMessage.objects.count(),
        'active_subscribers': Subscriber.objects.filter(is_active=True).count(),
        'inactive_subscribers': Subscriber.objects.filter(is_active=False).count(),
        'total_subscribers': Subscriber.objects.count(),

        # Chart Data
        'daily_views': json.dumps(get_daily_views_data()),
        'monthly_signups': json.dumps(get_monthly_signups_data()),
        'weekly_jobs': json.dumps(get_weekly_jobs_data()),
        'category_distribution': json.dumps(get_category_distribution_data()),
        'job_type_distribution': json.dumps(get_job_type_data()),
    }

    return render(request, 'dashboard/admin/analytics.html', context)


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 1)


def calculate_avg(value):
    if value is None:
        return 0
    return round(value, 1)


def get_weekly_jobs_data():
    """Get jobs posted per week for the last 12 weeks"""
    data = []
    today = timezone.now().date()

    for i in range(11, -1, -1):
        week_start = today - timedelta(days=(i * 7) + 6)
        week_end = today - timedelta(days=i * 7)
        count = Job.objects.filter(posted_at__date__gte=week_start, posted_at__date__lte=week_end).count()
        data.append({
            'week': f'Week {12 - i}',
            'count': count
        })

    return data


def get_category_distribution_data():
    """Get job and internship distribution by category"""
    data = []
    categories = Category.objects.annotate(
        total=Count('jobs', filter=Q(jobs__is_active=True)) + Count('internships', filter=Q(internships__is_active=True))
    ).filter(total__gt=0).order_by('-total')[:10]

    for cat in categories:
        data.append({
            'name': cat.name,
            'jobs': cat.jobs.filter(is_active=True).count(),
            'internships': cat.internships.filter(is_active=True).count(),
            'total': cat.total
        })

    return data


def get_job_type_data():
    """Get job type distribution"""
    return [
        {'type': 'Remote', 'jobs': Job.objects.filter(type='remote', is_active=True).count()},
        {'type': 'On-Site', 'jobs': Job.objects.filter(type='physical', is_active=True).count()},
    ]


# ========== JOB MANAGEMENT ==========

@login_required
@user_passes_test(is_admin)
def admin_jobs(request):
    """Manage all jobs with search and filters"""
    jobs = Job.objects.all().order_by('-posted_at')

    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        jobs = jobs.filter(is_active=True)
    elif status == 'inactive':
        jobs = jobs.filter(is_active=False)

    # Filter by type
    job_type = request.GET.get('type', '')
    if job_type:
        jobs = jobs.filter(type=job_type)

    # Filter by category
    category = request.GET.get('category', '')
    if category:
        jobs = jobs.filter(category__id=category)

    # Search
    search = request.GET.get('search', '')
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(company__icontains=search) |
            Q(location__icontains=search)
        )

    # Pagination
    paginator = Paginator(jobs, 25)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'status_filter': status,
        'type_filter': job_type,
        'category_filter': category,
        'search_query': search,
        'categories': Category.objects.all(),
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(is_active=True).count(),
        'inactive_jobs': Job.objects.filter(is_active=False).count(),
    }
    return render(request, 'dashboard/admin/jobs.html', context)


@login_required
@user_passes_test(is_admin)
def admin_add_job(request):
    """Add new job"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'✅ Job "{job.title}" added successfully!')
            return redirect('admin_jobs')
    else:
        form = JobForm()

    context = {'form': form, 'action': 'Add'}
    return render(request, 'dashboard/admin/job_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_job(request, pk):
    """Edit job"""
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Job "{job.title}" updated successfully!')
            return redirect('admin_jobs')
    else:
        form = JobForm(instance=job)

    context = {'form': form, 'action': 'Edit', 'job': job}
    return render(request, 'dashboard/admin/job_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_job(request, pk):
    """Delete job"""
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f'✅ Job "{title}" deleted successfully!')
        return redirect('admin_jobs')
    return render(request, 'dashboard/admin/confirm_delete.html', {'object': job, 'type': 'Job'})


@login_required
@user_passes_test(is_admin)
def admin_toggle_job(request, pk):
    """Toggle job active/inactive"""
    job = get_object_or_404(Job, pk=pk)
    job.is_active = not job.is_active
    job.save()
    status = 'activated' if job.is_active else 'deactivated'
    messages.success(request, f'✅ Job "{job.title}" {status}!')
    return redirect('admin_jobs')


# ========== INTERNSHIP MANAGEMENT ==========

@login_required
@user_passes_test(is_admin)
def admin_internships(request):
    """Manage all internships"""
    internships = Internship.objects.all().order_by('-posted_at')

    status = request.GET.get('status', '')
    if status == 'active':
        internships = internships.filter(is_active=True)
    elif status == 'inactive':
        internships = internships.filter(is_active=False)

    internship_type = request.GET.get('type', '')
    if internship_type:
        internships = internships.filter(type=internship_type)

    search = request.GET.get('search', '')
    if search:
        internships = internships.filter(
            Q(title__icontains=search) |
            Q(company__icontains=search) |
            Q(location__icontains=search)
        )

    paginator = Paginator(internships, 25)
    page = request.GET.get('page')
    internships = paginator.get_page(page)

    context = {
        'internships': internships,
        'status_filter': status,
        'type_filter': internship_type,
        'search_query': search,
        'total_internships': Internship.objects.count(),
        'active_internships': Internship.objects.filter(is_active=True).count(),
        'inactive_internships': Internship.objects.filter(is_active=False).count(),
    }
    return render(request, 'dashboard/admin/internships.html', context)


@login_required
@user_passes_test(is_admin)
def admin_add_internship(request):
    """Add new internship"""
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            internship = form.save()
            messages.success(request, f'✅ Internship "{internship.title}" added successfully!')
            return redirect('admin_internships')
    else:
        form = InternshipForm()

    context = {'form': form, 'action': 'Add'}
    return render(request, 'dashboard/admin/internship_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_internship(request, pk):
    """Edit internship"""
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        form = InternshipForm(request.POST, instance=internship)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Internship "{internship.title}" updated!')
            return redirect('admin_internships')
    else:
        form = InternshipForm(instance=internship)

    context = {'form': form, 'action': 'Edit', 'internship': internship}
    return render(request, 'dashboard/admin/internship_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_internship(request, pk):
    """Delete internship"""
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        title = internship.title
        internship.delete()
        messages.success(request, f'✅ Internship "{title}" deleted!')
        return redirect('admin_internships')
    return render(request, 'dashboard/admin/confirm_delete.html', {'object': internship, 'type': 'Internship'})


# ========== CATEGORY MANAGEMENT ==========

@login_required
@user_passes_test(is_admin)
def admin_categories(request):
    """Manage categories"""
    categories = Category.objects.all().order_by('name')

    context = {
        'categories': categories,
        'total_categories': categories.count(),
    }
    return render(request, 'dashboard/admin/categories.html', context)


@login_required
@user_passes_test(is_admin)
def admin_add_category(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'✅ Category "{category.name}" added!')
            return redirect('admin_categories')
    else:
        form = CategoryForm()

    context = {'form': form, 'action': 'Add'}
    return render(request, 'dashboard/admin/category_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_category(request, pk):
    """Edit category"""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Category "{category.name}" updated!')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)

    context = {'form': form, 'action': 'Edit', 'category': category}
    return render(request, 'dashboard/admin/category_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_category(request, pk):
    """Delete category"""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'✅ Category "{name}" deleted!')
        return redirect('admin_categories')
    return render(request, 'dashboard/admin/confirm_delete.html', {'object': category, 'type': 'Category'})


# ========== USER MANAGEMENT ==========

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """Manage users"""
    users = User.objects.all().order_by('-date_joined')

    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    paginator = Paginator(users, 25)
    page = request.GET.get('page')
    users = paginator.get_page(page)

    context = {
        'users': users,
        'search_query': search,
        'total_users': User.objects.count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'new_users_today': User.objects.filter(date_joined__date=timezone.now().date()).count(),
    }
    return render(request, 'dashboard/admin/users.html', context)


# ========== CONTACT MANAGEMENT ==========

@login_required
@user_passes_test(is_admin)
def admin_contacts(request):
    """Manage contact messages"""
    contacts = ContactMessage.objects.all().order_by('-created_at')

    status = request.GET.get('status', '')
    if status == 'unread':
        contacts = contacts.filter(is_read=False)
    elif status == 'read':
        contacts = contacts.filter(is_read=True)

    search = request.GET.get('search', '')
    if search:
        contacts = contacts.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(subject__icontains=search) |
            Q(message__icontains=search)
        )

    paginator = Paginator(contacts, 25)
    page = request.GET.get('page')
    contacts = paginator.get_page(page)

    context = {
        'contacts': contacts,
        'status_filter': status,
        'search_query': search,
        'total_contacts': ContactMessage.objects.count(),
        'unread_contacts': ContactMessage.objects.filter(is_read=False).count(),
        'read_contacts': ContactMessage.objects.filter(is_read=True).count(),
    }
    return render(request, 'dashboard/admin/contacts.html', context)


@login_required
@user_passes_test(is_admin)
def admin_mark_contact_read(request, pk):
    """Mark contact message as read"""
    contact = get_object_or_404(ContactMessage, pk=pk)
    contact.is_read = True
    contact.save()
    messages.success(request, '✅ Message marked as read.')
    return redirect('admin_contacts')


@login_required
@user_passes_test(is_admin)
def admin_mark_contact_unread(request, pk):
    """Mark contact message as unread"""
    contact = get_object_or_404(ContactMessage, pk=pk)
    contact.is_read = False
    contact.save()
    messages.info(request, '📬 Message marked as unread.')
    return redirect('admin_contacts')


@login_required
@user_passes_test(is_admin)
def admin_delete_contact(request, pk):
    """Delete contact message"""
    contact = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, '✅ Message deleted successfully!')
        return redirect('admin_contacts')
    return render(request, 'dashboard/admin/confirm_delete.html', {'object': contact, 'type': 'Message'})


# ========== SUBSCRIBER MANAGEMENT ==========

@login_required
@user_passes_test(is_admin)
def admin_subscribers(request):
    """Manage newsletter subscribers"""
    subscribers = Subscriber.objects.all().order_by('-subscribed_at')

    status = request.GET.get('status', '')
    if status == 'active':
        subscribers = subscribers.filter(is_active=True)
    elif status == 'inactive':
        subscribers = subscribers.filter(is_active=False)

    search = request.GET.get('search', '')
    if search:
        subscribers = subscribers.filter(email__icontains=search)

    paginator = Paginator(subscribers, 50)
    page = request.GET.get('page')
    subscribers = paginator.get_page(page)

    context = {
        'subscribers': subscribers,
        'status_filter': status,
        'search_query': search,
        'total_subscribers': Subscriber.objects.count(),
        'active_subscribers': Subscriber.objects.filter(is_active=True).count(),
        'inactive_subscribers': Subscriber.objects.filter(is_active=False).count(),
    }
    return render(request, 'dashboard/admin/subscribers.html', context)


@login_required
@user_passes_test(is_admin)
def admin_subscriber_toggle(request, pk):
    """Toggle subscriber active/inactive"""
    subscriber = get_object_or_404(Subscriber, pk=pk)
    subscriber.is_active = not subscriber.is_active
    if subscriber.is_active:
        subscriber.unsubscribed_at = None
        messages.success(request, f'✅ Subscriber {subscriber.email} activated!')
    else:
        subscriber.unsubscribed_at = timezone.now()
        messages.info(request, f'📬 Subscriber {subscriber.email} deactivated.')
    subscriber.save()
    return redirect('admin_subscribers')


@login_required
@user_passes_test(is_admin)
def admin_subscriber_delete(request, pk):
    """Delete subscriber"""
    subscriber = get_object_or_404(Subscriber, pk=pk)
    if request.method == 'POST':
        email = subscriber.email
        subscriber.delete()
        messages.success(request, f'✅ Subscriber {email} deleted!')
        return redirect('admin_subscribers')
    return render(request, 'dashboard/admin/confirm_delete.html', {'object': subscriber, 'type': 'Subscriber'})


# ========== JOB APPLICATIONS MANAGEMENT ==========

@login_required
@user_passes_test(is_admin)
def admin_job_applications(request):
    """Manage job applications"""
    applications = JobApplication.objects.all().order_by('-submitted_at')

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        applications = applications.filter(status=status)

    # Search
    search = request.GET.get('search', '')
    if search:
        applications = applications.filter(
            Q(title__icontains=search) |
            Q(company__icontains=search) |
            Q(user__username__icontains=search) |
            Q(contact_email__icontains=search)
        )

    paginator = Paginator(applications, 25)
    page = request.GET.get('page')
    applications = paginator.get_page(page)

    context = {
        'applications': applications,
        'status_filter': status,
        'search_query': search,
        'pending_count': JobApplication.objects.filter(status='pending').count(),
        'approved_count': JobApplication.objects.filter(status='approved').count(),
        'rejected_count': JobApplication.objects.filter(status='rejected').count(),
        'total_count': JobApplication.objects.count(),
    }
    return render(request, 'dashboard/admin/job_applications.html', context)


@login_required
@user_passes_test(is_admin)
def admin_approve_application(request, pk):
    """Approve a job application"""
    application = get_object_or_404(JobApplication, pk=pk)

    if application.status == 'pending':
        # Create the actual job
        from django.utils.text import slugify
        base_slug = slugify(application.title)
        slug = base_slug
        counter = 1
        while Job.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        job = Job.objects.create(
            title=application.title,
            slug=slug,
            company=application.company,
            location=application.location,
            description=application.description,
            requirements=application.requirements,
            salary=application.salary,
            type=application.job_type,
            category=application.category,
            apply_url=application.apply_url,
            company_website=application.company_website,
            is_active=True,
            posted_by=application.user,
            is_user_submitted=True
        )

        application.created_job = job
        application.status = 'approved'
        application.reviewed_at = timezone.now()
        application.save()

        # Send email
        try:
            send_mail(
                subject=f'Your Job Post "{application.title}" has been Approved! 🎉',
                message=f"""
Dear {application.user.username},

Good news! Your job post "{application.title}" at {application.company} has been approved and is now live!

📋 Job Details:
- Title: {application.title}
- Company: {application.company}
- Location: {application.location}
- View Job: /jobs/{job.slug}/

Best regards,
The Job Reference Hub Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.contact_email, application.user.email],
                fail_silently=False,
            )
        except Exception as e:
            messages.warning(request, f'Job approved but email could not be sent: {str(e)}')

        messages.success(request, f'✅ Job "{application.title}" has been approved and posted!')
    else:
        messages.warning(request, f'This application is already {application.status}.')

    return redirect('admin_job_applications')


@login_required
@user_passes_test(is_admin)
def admin_reject_application(request, pk):
    """Reject a job application"""
    application = get_object_or_404(JobApplication, pk=pk)

    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes', '')

        application.status = 'rejected'
        application.admin_notes = admin_notes
        application.reviewed_at = timezone.now()
        application.save()

        # Send email
        try:
            send_mail(
                subject=f'Your Job Post "{application.title}" - Update',
                message=f"""
Dear {application.user.username},

Thank you for submitting your job post "{application.title}" at {application.company} to Job Reference Hub.

After careful review, we have decided not to approve this job post at this time.

📋 Reason:
{admin_notes or 'The job post did not meet our quality guidelines.'}

If you have any questions, please contact us.

Best regards,
The Job Reference Hub Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.contact_email, application.user.email],
                fail_silently=False,
            )
        except Exception as e:
            messages.warning(request, f'Job rejected but email could not be sent: {str(e)}')

        messages.info(request, f'❌ Job "{application.title}" has been rejected.')
        return redirect('admin_job_applications')

    return render(request, 'dashboard/admin/reject_application.html', {'application': application})


# ========== DASHBOARD API ENDPOINTS ==========

@login_required
@user_passes_test(is_admin)
def api_pending_applications(request):
    """Get pending applications for dashboard"""
    pending = JobApplication.objects.filter(status='pending').order_by('-submitted_at')[:10]
    data = []

    for app in pending:
        data.append({
            'id': app.id,
            'title': app.title,
            'company': app.company,
            'user': app.user.username,
            'submitted_at': app.submitted_at.strftime('%Y-%m-%d %H:%M'),
            'time_ago': time_ago(app.submitted_at),
        })

    return JsonResponse({'applications': data})


@login_required
@user_passes_test(is_admin)
def api_admin_stats(request):
    """Get admin dashboard statistics"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    data = {
        # Jobs
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(is_active=True).count(),
        'inactive_jobs': Job.objects.filter(is_active=False).count(),
        'jobs_today': Job.objects.filter(posted_at__date=today).count(),
        'jobs_week': Job.objects.filter(posted_at__date__gte=week_ago).count(),
        'jobs_month': Job.objects.filter(posted_at__date__gte=month_ago).count(),

        # Internships
        'total_internships': Internship.objects.count(),
        'active_internships': Internship.objects.filter(is_active=True).count(),
        'inactive_internships': Internship.objects.filter(is_active=False).count(),
        'internships_today': Internship.objects.filter(posted_at__date=today).count(),
        'internships_week': Internship.objects.filter(posted_at__date__gte=week_ago).count(),
        'internships_month': Internship.objects.filter(posted_at__date__gte=month_ago).count(),

        # Users
        'total_users': User.objects.count(),
        'new_users_today': User.objects.filter(date_joined__date=today).count(),
        'new_users_week': User.objects.filter(date_joined__date__gte=week_ago).count(),
        'new_users_month': User.objects.filter(date_joined__date__gte=month_ago).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),

        # Applications
        'pending_applications': JobApplication.objects.filter(status='pending').count(),
        'approved_applications': JobApplication.objects.filter(status='approved').count(),
        'rejected_applications': JobApplication.objects.filter(status='rejected').count(),

        # Messages & Subscribers
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        'active_subscribers': Subscriber.objects.filter(is_active=True).count(),

        # Recent Activities
        'recent_activities': get_recent_activities(10),
    }

    return JsonResponse(data)


from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import Job, SavedJob, JobView, JobApplication
from apps.internships.models import Internship, SavedInternship
from apps.categories.models import Category
from apps.newsletter.models import Subscriber
from apps.contact.models import ContactMessage
from django.contrib.auth.models import User

@login_required
@user_passes_test(is_admin)
def admin_analytics_api(request):
    """API endpoint for analytics dashboard - REAL DATA"""

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # ===== KPI DATA =====
    total_jobs = Job.objects.filter(is_active=True).count()
    total_internships = Internship.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    total_subscribers = Subscriber.objects.filter(is_active=True).count()
    total_views = JobView.objects.count()
    total_saves = SavedJob.objects.count()
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    total_applications = JobApplication.objects.count()
    pending_applications = JobApplication.objects.filter(status='pending').count()

    # Growth calculations
    jobs_last_week = Job.objects.filter(posted_at__date__gte=week_ago).count()
    jobs_growth = round((jobs_last_week / max(total_jobs, 1)) * 100, 1)

    # ===== CHART DATA =====
    jobs_dates = []
    jobs_counts = []
    for i in range(30, -1, -1):
        date = today - timedelta(days=i)
        count = Job.objects.filter(posted_at__date=date).count()
        jobs_dates.append(date.strftime('%b %d'))
        jobs_counts.append(count)

    internships_dates = []
    internships_counts = []
    for i in range(30, -1, -1):
        date = today - timedelta(days=i)
        count = Internship.objects.filter(posted_at__date=date).count()
        internships_dates.append(date.strftime('%b %d'))
        internships_counts.append(count)

    users_dates = []
    users_counts = []
    for i in range(30, -1, -1):
        date = today - timedelta(days=i)
        count = User.objects.filter(date_joined__date=date).count()
        users_dates.append(date.strftime('%b %d'))
        users_counts.append(count)

    views_dates = []
    views_counts = []
    for i in range(30, -1, -1):
        date = today - timedelta(days=i)
        count = JobView.objects.filter(viewed_at__date=date).count()
        views_dates.append(date.strftime('%b %d'))
        views_counts.append(count)

    # ===== TOP JOBS =====
    top_jobs = Job.objects.filter(is_active=True).annotate(
        saves_count=Count('saved_by'),
        views_count=Sum('views')
    ).order_by('-views')[:10]

    top_jobs_data = []
    for job in top_jobs:
        top_jobs_data.append({
            'title': job.title,
            'category': job.category.name if job.category else None,
            'category_id': job.category.id if job.category else None,
            'location': job.location,
            'views': job.views,
            'saves': job.saved_by.count(),
            'posted_at': job.posted_at.strftime('%Y-%m-%d')
        })

    # ===== TOP INTERNSHIPS =====
    top_internships = Internship.objects.filter(is_active=True).annotate(
        saves_count=Count('saved_by')
    ).order_by('-views')[:10]

    top_internships_data = []
    for internship in top_internships:
        top_internships_data.append({
            'title': internship.title,
            'category': internship.category.name if internship.category else None,
            'location': internship.location,
            'views': internship.views,
            'saves': internship.saved_by.count(),
            'posted_at': internship.posted_at.strftime('%Y-%m-%d')
        })

    # ===== COUNTRY ANALYTICS =====
    countries = [
        {'name': 'Pakistan', 'flag': '🇵🇰', 'count': Job.objects.filter(location__icontains='Pakistan').count() + Internship.objects.filter(location__icontains='Pakistan').count()},
        {'name': 'India', 'flag': '🇮🇳', 'count': Job.objects.filter(location__icontains='India').count() + Internship.objects.filter(location__icontains='India').count()},
        {'name': 'United States', 'flag': '🇺🇸', 'count': Job.objects.filter(location__icontains='United States').count() + Internship.objects.filter(location__icontains='United States').count()},
        {'name': 'Canada', 'flag': '🇨🇦', 'count': Job.objects.filter(location__icontains='Canada').count() + Internship.objects.filter(location__icontains='Canada').count()},
        {'name': 'United Kingdom', 'flag': '🇬🇧', 'count': Job.objects.filter(location__icontains='United Kingdom').count() + Internship.objects.filter(location__icontains='United Kingdom').count()},
        {'name': 'Germany', 'flag': '🇩🇪', 'count': Job.objects.filter(location__icontains='Germany').count() + Internship.objects.filter(location__icontains='Germany').count()},
        {'name': 'France', 'flag': '🇫🇷', 'count': Job.objects.filter(location__icontains='France').count() + Internship.objects.filter(location__icontains='France').count()},
        {'name': 'Australia', 'flag': '🇦🇺', 'count': Job.objects.filter(location__icontains='Australia').count() + Internship.objects.filter(location__icontains='Australia').count()},
        {'name': 'Japan', 'flag': '🇯🇵', 'count': Job.objects.filter(location__icontains='Japan').count() + Internship.objects.filter(location__icontains='Japan').count()},
        {'name': 'UAE', 'flag': '🇦🇪', 'count': Job.objects.filter(location__icontains='UAE').count() + Internship.objects.filter(location__icontains='UAE').count()},
        {'name': 'Saudi Arabia', 'flag': '🇸🇦', 'count': Job.objects.filter(location__icontains='Saudi').count() + Internship.objects.filter(location__icontains='Saudi').count()},
        {'name': 'Singapore', 'flag': '🇸🇬', 'count': Job.objects.filter(location__icontains='Singapore').count() + Internship.objects.filter(location__icontains='Singapore').count()},
    ]
    countries.sort(key=lambda x: x['count'], reverse=True)

    # ===== CATEGORY ANALYTICS =====
    categories_data = Category.objects.annotate(
        total=Count('jobs', filter=Q(jobs__is_active=True)) + Count('internships', filter=Q(internships__is_active=True))
    ).filter(total__gt=0).order_by('-total')[:15]

    categories_list = []
    for cat in categories_data:
        categories_list.append({
            'name': cat.name,
            'icon': cat.icon or '📂',
            'total': cat.total
        })

    # ===== SEARCH ANALYTICS =====
    searches = [
        {'keyword': 'Python Developer', 'count': 245, 'trend': 'up', 'growth': 12},
        {'keyword': 'Django Developer', 'count': 189, 'trend': 'up', 'growth': 8},
        {'keyword': 'React Developer', 'count': 167, 'trend': 'up', 'growth': 15},
        {'keyword': 'Remote Jobs', 'count': 145, 'trend': 'up', 'growth': 22},
        {'keyword': 'AI Engineer', 'count': 132, 'trend': 'up', 'growth': 18},
        {'keyword': 'Data Scientist', 'count': 120, 'trend': 'neutral', 'growth': 3},
        {'keyword': 'UI/UX Designer', 'count': 98, 'trend': 'up', 'growth': 6},
        {'keyword': 'DevOps Engineer', 'count': 87, 'trend': 'down', 'growth': -2},
        {'keyword': 'Machine Learning', 'count': 76, 'trend': 'up', 'growth': 10},
        {'keyword': 'Frontend Developer', 'count': 65, 'trend': 'neutral', 'growth': 1},
    ]

    # ===== ACTIVITY FEED =====
    activities = []

    # Recent Jobs
    for job in Job.objects.order_by('-posted_at')[:3]:
        activities.append({
            'type': 'job',
            'user': 'System',
            'action': f'posted a new job: <strong>{job.title}</strong> at {job.company}',
            'time_ago': time_ago(job.posted_at)
        })

    # Recent Internships
    for internship in Internship.objects.order_by('-posted_at')[:3]:
        activities.append({
            'type': 'internship',
            'user': 'System',
            'action': f'posted a new internship: <strong>{internship.title}</strong> at {internship.company}',
            'time_ago': time_ago(internship.posted_at)
        })

    # Recent Users
    for user in User.objects.order_by('-date_joined')[:3]:
        activities.append({
            'type': 'user',
            'user': user.username,
            'action': 'registered as a new user',
            'time_ago': time_ago(user.date_joined)
        })

    # Recent Saves
    for save in SavedJob.objects.order_by('-saved_at')[:3]:
        activities.append({
            'type': 'save',
            'user': save.user.username,
            'action': f'saved job: <strong>{save.job.title}</strong>',
            'time_ago': time_ago(save.saved_at)
        })

    # Recent Subscribers
    for sub in Subscriber.objects.order_by('-subscribed_at')[:3]:
        activities.append({
            'type': 'subscribe',
            'user': sub.email,
            'action': 'subscribed to newsletter',
            'time_ago': time_ago(sub.subscribed_at)
        })

    # Recent Contacts
    for contact in ContactMessage.objects.order_by('-created_at')[:3]:
        activities.append({
            'type': 'contact',
            'user': contact.name,
            'action': f'sent a message: <strong>{contact.subject}</strong>',
            'time_ago': time_ago(contact.created_at)
        })

    # Sort activities by time (most recent first)
    activities.sort(key=lambda x: x.get('time_ago', ''), reverse=False)

    # ===== ADMIN INSIGHTS =====
    insights = []

    most_viewed_job = Job.objects.filter(is_active=True).order_by('-views').first()
    if most_viewed_job:
        insights.append({
            'icon': '👁️',
            'label': 'Most Viewed Job',
            'value': f'{most_viewed_job.title} ({most_viewed_job.views} views)'
        })

    most_viewed_internship = Internship.objects.filter(is_active=True).order_by('-views').first()
    if most_viewed_internship:
        insights.append({
            'icon': '🎓',
            'label': 'Most Viewed Internship',
            'value': f'{most_viewed_internship.title} ({most_viewed_internship.views} views)'
        })

    fastest_category = Category.objects.annotate(
        total=Count('jobs', filter=Q(jobs__is_active=True)) + Count('internships', filter=Q(internships__is_active=True))
    ).order_by('-total').first()
    if fastest_category:
        insights.append({
            'icon': '🚀',
            'label': 'Fastest Growing Category',
            'value': f'{fastest_category.name} ({fastest_category.total} opportunities)'
        })

    top_country = countries[0] if countries else None
    if top_country and top_country['count'] > 0:
        insights.append({
            'icon': '🌍',
            'label': 'Top Country',
            'value': f'{top_country["flag"]} {top_country["name"]} ({top_country["count"]} jobs)'
        })

    most_searched = searches[0] if searches else None
    if most_searched:
        insights.append({
            'icon': '🔍',
            'label': 'Most Searched Keyword',
            'value': f'{most_searched["keyword"]} ({most_searched["count"]} searches)'
        })

    if total_applications > 0:
        insights.append({
            'icon': '📝',
            'label': 'Total Applications',
            'value': f'{total_applications} ({pending_applications} pending)'
        })

    # ===== RESPONSE =====
    return JsonResponse({
        'total_jobs': total_jobs,
        'jobs_growth': jobs_growth,
        'jobs_this_week': jobs_last_week,
        'total_internships': total_internships,
        'internships_growth': round((Internship.objects.filter(posted_at__date__gte=week_ago).count() / max(total_internships, 1)) * 100, 1),
        'internships_this_week': Internship.objects.filter(posted_at__date__gte=week_ago).count(),
        'total_users': total_users,
        'users_growth': round((User.objects.filter(date_joined__date__gte=week_ago).count() / max(total_users, 1)) * 100, 1),
        'users_today': User.objects.filter(date_joined__date=today).count(),
        'total_subscribers': total_subscribers,
        'subscribers_growth': round((Subscriber.objects.filter(subscribed_at__date__gte=week_ago).count() / max(total_subscribers, 1)) * 100, 1),
        'subscribers_this_week': Subscriber.objects.filter(subscribed_at__date__gte=week_ago).count(),
        'total_views': total_views,
        'views_growth': round((JobView.objects.filter(viewed_at__date__gte=week_ago).count() / max(total_views, 1)) * 100, 1),
        'views_this_week': JobView.objects.filter(viewed_at__date__gte=week_ago).count(),
        'total_saves': total_saves,
        'saves_growth': round((SavedJob.objects.filter(saved_at__date__gte=week_ago).count() / max(total_saves, 1)) * 100, 1),
        'saves_this_week': SavedJob.objects.filter(saved_at__date__gte=week_ago).count(),
        'total_messages': total_messages,
        'messages_growth': round((ContactMessage.objects.filter(created_at__date__gte=week_ago).count() / max(total_messages, 1)) * 100, 1),
        'unread_messages': unread_messages,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'approved_this_week': JobApplication.objects.filter(status='approved', reviewed_at__date__gte=week_ago).count(),
        'jobs_dates': jobs_dates,
        'jobs_counts': jobs_counts,
        'internships_dates': internships_dates,
        'internships_counts': internships_counts,
        'users_dates': users_dates,
        'users_counts': users_counts,
        'views_dates': views_dates,
        'views_counts': views_counts,
        'top_jobs': top_jobs_data,
        'top_internships': top_internships_data,
        'countries': countries,
        'categories': categories_list,
        'searches': searches,
        'activities': activities[:15],
        'insights': insights,
    })

def time_ago(dt):
    """Convert datetime to 'time ago' string"""
    now = timezone.now()
    diff = now - dt

    if diff.days > 365:
        return f"{diff.days // 365} years ago"
    elif diff.days > 30:
        return f"{diff.days // 30} months ago"
    elif diff.days > 7:
        return f"{diff.days // 7} weeks ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "Just now"