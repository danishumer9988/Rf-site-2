from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication

@login_required
@staff_member_required
def debug_jobs(request):
    """Debug view to check job status - Admin only"""
    data = {
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(is_active=True).count(),
        'inactive_jobs': Job.objects.filter(is_active=False).count(),
        'user_submitted_jobs': Job.objects.filter(is_user_submitted=True).count(),
        'user_submitted_active': Job.objects.filter(is_user_submitted=True, is_active=True).count(),
        'approved_applications': JobApplication.objects.filter(status='approved').count(),
        'applications_with_jobs': JobApplication.objects.filter(
            status='approved', created_job__isnull=False
        ).count(),
        'applications_without_jobs': JobApplication.objects.filter(
            status='approved', created_job__isnull=True
        ).count(),
        'pending_applications': JobApplication.objects.filter(status='pending').count(),
        'rejected_applications': JobApplication.objects.filter(status='rejected').count(),
        'jobs': []
    }

    # Get sample jobs
    for job in Job.objects.filter(is_active=True)[:20]:
        data['jobs'].append({
            'id': job.id,
            'title': job.title,
            'slug': job.slug,
            'is_active': job.is_active,
            'is_user_submitted': job.is_user_submitted,
            'posted_by': job.posted_by.username if job.posted_by else 'Admin',
            'posted_at': job.posted_at.strftime('%Y-%m-%d %H:%M'),
            'url': f'/jobs/{job.slug}/',
            'views': job.views,
            'likes': job.likes,
        })

    # Get applications without jobs
    data['orphan_applications'] = []
    for app in JobApplication.objects.filter(status='approved', created_job__isnull=True)[:10]:
        data['orphan_applications'].append({
            'id': app.id,
            'title': app.title,
            'company': app.company,
            'user': app.user.username,
            'submitted_at': app.submitted_at.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse(data, safe=False)