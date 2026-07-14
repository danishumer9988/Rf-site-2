from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
import json
from .models import Job, SavedJob, JobView, JobLike, JobComment, JobClick, JobApplication
from .forms import JobForm, JobCommentForm, JobSearchForm, JobApplicationForm
from apps.categories.models import Category


# ========== JOB LISTING VIEWS ==========

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 15

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)

        # Get search parameters
        query = self.request.GET.get('query', '')
        location = self.request.GET.get('location', '')
        employment_type = self.request.GET.get('employment_type', '')
        work_type = self.request.GET.get('work_type', '')  # Changed from work_location
        category_id = self.request.GET.get('category', '')

        # Apply filters
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(company__icontains=query) |
                Q(requirements__icontains=query)
            )

        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by employment_type (Full-Time, Part-Time, Contract, Daily)
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)

        # Filter by work_type (Remote, On-Site, Hybrid)
        if work_type:
            queryset = queryset.filter(work_type=work_type)

        if category_id:
            try:
                queryset = queryset.filter(category_id=int(category_id))
            except ValueError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get counts for stats
        total_jobs = Job.objects.filter(is_active=True).count()
        full_time_count = Job.objects.filter(is_active=True, employment_type='full_time').count()
        part_time_count = Job.objects.filter(is_active=True, employment_type='part_time').count()
        contract_count = Job.objects.filter(is_active=True, employment_type='contract').count()
        daily_count = Job.objects.filter(is_active=True, employment_type='daily').count()
        remote_count = Job.objects.filter(is_active=True, work_type='remote').count()
        physical_count = Job.objects.filter(is_active=True, work_type='physical').count()

        # Get the most recent job post time
        latest_job = Job.objects.filter(is_active=True).order_by('-posted_at').first()
        context['last_updated'] = latest_job.posted_at if latest_job else timezone.now()

        context['total_jobs'] = total_jobs
        context['full_time_count'] = full_time_count
        context['part_time_count'] = part_time_count
        context['contract_count'] = contract_count
        context['daily_count'] = daily_count
        context['remote_count'] = remote_count
        context['physical_count'] = physical_count

        # Get categories for dropdown
        context['categories'] = Category.objects.all()

        # Get today's date
        context['today'] = timezone.now().date()

        # Get saved jobs for user
        if self.request.user.is_authenticated:
            saved_jobs = SavedJob.objects.filter(user=self.request.user).values_list('job_id', flat=True)
            context['saved_ids'] = list(saved_jobs)
        else:
            context['saved_ids'] = []

        return context


class PhysicalJobListView(ListView):
    model = Job
    template_name = 'jobs/physical_jobs.html'
    context_object_name = 'jobs'
    paginate_by = 15

    def get_queryset(self):
        return Job.objects.filter(is_active=True, work_type='physical')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        latest_job = Job.objects.filter(is_active=True, work_type='physical').order_by('-posted_at').first()
        context['last_updated'] = latest_job.posted_at if latest_job else timezone.now()
        context['today'] = timezone.now().date()
        context['total_jobs'] = Job.objects.filter(is_active=True).count()
        context['remote_count'] = Job.objects.filter(is_active=True, work_type='remote').count()
        context['physical_count'] = Job.objects.filter(is_active=True, work_type='physical').count()
        context['full_time_count'] = Job.objects.filter(is_active=True, employment_type='full_time').count()
        context['part_time_count'] = Job.objects.filter(is_active=True, employment_type='part_time').count()
        context['contract_count'] = Job.objects.filter(is_active=True, employment_type='contract').count()
        context['daily_count'] = Job.objects.filter(is_active=True, employment_type='daily').count()
        context['categories'] = Category.objects.all()
        context['new_count'] = Job.objects.filter(
            is_active=True, work_type='physical',
            posted_at__date=timezone.now().date()
        ).count()

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedJob.objects.filter(
                user=self.request.user
            ).values_list('job_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


class RemoteJobListView(ListView):
    model = Job
    template_name = 'jobs/remote_jobs.html'
    context_object_name = 'jobs'
    paginate_by = 15

    def get_queryset(self):
        return Job.objects.filter(is_active=True, work_type='remote')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        latest_job = Job.objects.filter(is_active=True, work_type='remote').order_by('-posted_at').first()
        context['last_updated'] = latest_job.posted_at if latest_job else timezone.now()
        context['today'] = timezone.now().date()
        context['total_jobs'] = Job.objects.filter(is_active=True).count()
        context['remote_count'] = Job.objects.filter(is_active=True, work_type='remote').count()
        context['physical_count'] = Job.objects.filter(is_active=True, work_type='physical').count()
        context['full_time_count'] = Job.objects.filter(is_active=True, employment_type='full_time').count()
        context['part_time_count'] = Job.objects.filter(is_active=True, employment_type='part_time').count()
        context['contract_count'] = Job.objects.filter(is_active=True, employment_type='contract').count()
        context['daily_count'] = Job.objects.filter(is_active=True, employment_type='daily').count()
        context['categories'] = Category.objects.all()
        context['new_count'] = Job.objects.filter(
            is_active=True, work_type='remote',
            posted_at__date=timezone.now().date()
        ).count()

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedJob.objects.filter(
                user=self.request.user
            ).values_list('job_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


class OnSiteJobListView(PhysicalJobListView):
    """Alias for PhysicalJobListView"""
    pass


class FullTimeJobListView(ListView):
    model = Job
    template_name = 'jobs/full_time/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 15

    def get_queryset(self):
        return Job.objects.filter(is_active=True, employment_type='full_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['total_jobs'] = Job.objects.filter(is_active=True).count()
        context['remote_count'] = Job.objects.filter(is_active=True, work_type='remote').count()
        context['physical_count'] = Job.objects.filter(is_active=True, work_type='physical').count()
        context['full_time_count'] = Job.objects.filter(is_active=True, employment_type='full_time').count()
        context['part_time_count'] = Job.objects.filter(is_active=True, employment_type='part_time').count()
        context['contract_count'] = Job.objects.filter(is_active=True, employment_type='contract').count()
        context['daily_count'] = Job.objects.filter(is_active=True, employment_type='daily').count()
        context['categories'] = Category.objects.all()

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedJob.objects.filter(
                user=self.request.user
            ).values_list('job_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


class PartTimeJobListView(ListView):
    model = Job
    template_name = 'jobs/part_time/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 15

    def get_queryset(self):
        return Job.objects.filter(is_active=True, employment_type='part_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['total_jobs'] = Job.objects.filter(is_active=True).count()
        context['remote_count'] = Job.objects.filter(is_active=True, work_type='remote').count()
        context['physical_count'] = Job.objects.filter(is_active=True, work_type='physical').count()
        context['full_time_count'] = Job.objects.filter(is_active=True, employment_type='full_time').count()
        context['part_time_count'] = Job.objects.filter(is_active=True, employment_type='part_time').count()
        context['contract_count'] = Job.objects.filter(is_active=True, employment_type='contract').count()
        context['daily_count'] = Job.objects.filter(is_active=True, employment_type='daily').count()
        context['categories'] = Category.objects.all()

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedJob.objects.filter(
                user=self.request.user
            ).values_list('job_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


class ContractJobListView(ListView):
    model = Job
    template_name = 'jobs/contract/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 15

    def get_queryset(self):
        return Job.objects.filter(is_active=True, employment_type='contract')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['total_jobs'] = Job.objects.filter(is_active=True).count()
        context['remote_count'] = Job.objects.filter(is_active=True, work_type='remote').count()
        context['physical_count'] = Job.objects.filter(is_active=True, work_type='physical').count()
        context['full_time_count'] = Job.objects.filter(is_active=True, employment_type='full_time').count()
        context['part_time_count'] = Job.objects.filter(is_active=True, employment_type='part_time').count()
        context['contract_count'] = Job.objects.filter(is_active=True, employment_type='contract').count()
        context['daily_count'] = Job.objects.filter(is_active=True, employment_type='daily').count()
        context['categories'] = Category.objects.all()
        context['urgent_count'] = Job.objects.filter(is_active=True, employment_type='contract', is_urgent=True).count()
        context['expert_count'] = Job.objects.filter(is_active=True, employment_type='contract', experience_level='expert').count()

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedJob.objects.filter(
                user=self.request.user
            ).values_list('job_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


class DailyJobListView(ListView):
    model = Job
    template_name = 'jobs/daily/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 15

    def get_queryset(self):
        return Job.objects.filter(is_active=True, employment_type='daily')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['total_jobs'] = Job.objects.filter(is_active=True).count()
        context['remote_count'] = Job.objects.filter(is_active=True, work_type='remote').count()
        context['physical_count'] = Job.objects.filter(is_active=True, work_type='physical').count()
        context['full_time_count'] = Job.objects.filter(is_active=True, employment_type='full_time').count()
        context['part_time_count'] = Job.objects.filter(is_active=True, employment_type='part_time').count()
        context['contract_count'] = Job.objects.filter(is_active=True, employment_type='contract').count()
        context['daily_count'] = Job.objects.filter(is_active=True, employment_type='daily').count()
        context['categories'] = Category.objects.all()
        context['immediate_count'] = Job.objects.filter(is_active=True, employment_type='daily', is_immediate=True).count()

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedJob.objects.filter(
                user=self.request.user
            ).values_list('job_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


# ========== JOB DETAIL VIEW ==========

class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        job = self.get_object()

        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        viewed = JobView.objects.filter(job=job, session_key=session_key).exists()

        if not viewed:
            job.views += 1
            job.save()
            JobView.objects.create(
                job=job,
                user=request.user if request.user.is_authenticated else None,
                ip_address=self.get_client_ip(request),
                session_key=session_key,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referer=request.META.get('HTTP_REFERER', '')
            )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()

        context['related_jobs'] = Job.objects.filter(
            category=job.category
        ).exclude(id=job.id)[:5]

        if self.request.user.is_authenticated:
            context['is_liked'] = JobLike.objects.filter(
                user=self.request.user, job=job
            ).exists()
            context['is_saved'] = SavedJob.objects.filter(
                user=self.request.user, job=job
            ).exists()

        context['comments'] = job.comments.filter(is_approved=True)
        context['comment_form'] = JobCommentForm()
        context['analytics'] = {
            'views': job.views,
            'likes': job.likes,
            'clicks': job.clicks,
            'comments_count': job.comments.filter(is_approved=True).count(),
            'applications': job.applications_count,
        }
        context['is_owner'] = self.request.user.is_authenticated and job.posted_by == self.request.user

        return context


# ========== JOB INTERACTIONS ==========

@login_required
def like_job(request, slug):
    job = get_object_or_404(Job, slug=slug)
    like, created = JobLike.objects.get_or_create(user=request.user, job=job)

    if created:
        job.likes += 1
        job.save()
        liked = True
        message = '❤️ Job liked!'
    else:
        like.delete()
        job.likes -= 1
        job.save()
        liked = False
        message = '💔 Job unliked'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'likes_count': job.likes,
            'message': message
        })

    return redirect('job_detail', slug=job.slug)


@login_required
def comment_job(request, slug):
    job = get_object_or_404(Job, slug=slug)

    if request.method == 'POST':
        form = JobCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.job = job
            comment.user = request.user
            comment.save()

            if job.posted_by and job.posted_by != request.user:
                try:
                    send_mail(
                        subject=f'New Comment on Your Job: {job.title}',
                        message=f"""
Hello {job.posted_by.username},

{request.user.username} has commented on your job post "{job.title}".

💬 Comment:
"{comment.comment}"

View the comment here: https://jobreferencehub.com/jobs/{job.slug}/

Best regards,
The Job Reference Hub Team
""",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[job.posted_by.email],
                        fail_silently=True,
                    )
                except:
                    pass

            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Please enter a valid comment.')

    return redirect('job_detail', slug=job.slug)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(JobComment, id=comment_id)
    if request.user == comment.user or request.user.is_staff:
        job_slug = comment.job.slug
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
    else:
        messages.error(request, 'You are not authorized to delete this comment.')
    return redirect('job_detail', slug=job_slug)


@login_required
def save_job(request, slug):
    job = get_object_or_404(Job, slug=slug)
    saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)

    if created:
        messages.success(request, f'Job "{job.title}" saved successfully!')
    else:
        saved_job.delete()
        messages.info(request, f'Job "{job.title}" removed from saved.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'saved': created})

    return redirect(request.META.get('HTTP_REFERER', 'job_list'))


@login_required
def track_click(request, slug):
    job = get_object_or_404(Job, slug=slug)
    link_type = request.GET.get('type', 'apply')

    job.clicks += 1
    job.save()

    JobClick.objects.create(
        job=job,
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
        link_type=link_type
    )

    if link_type == 'apply' and job.apply_url:
        return redirect(job.apply_url)
    elif link_type == 'website' and job.company_website:
        return redirect(job.company_website)

    return redirect('job_detail', slug=job.slug)


# ========== USER POSTED JOBS ==========

@login_required
def my_posted_jobs(request):
    jobs = Job.objects.filter(posted_by=request.user).order_by('-posted_at')

    approved_apps = JobApplication.objects.filter(
        user=request.user,
        status='approved',
        created_job__isnull=True
    )

    if approved_apps.exists():
        messages.warning(
            request,
            f'⚠️ {approved_apps.count()} of your approved jobs are not published. Please contact support.'
        )

    total_views = sum(job.views for job in jobs)
    total_likes = sum(job.likes for job in jobs)
    total_clicks = sum(job.clicks for job in jobs)
    total_comments = sum(job.comments.filter(is_approved=True).count() for job in jobs)

    context = {
        'jobs': jobs,
        'total_jobs': jobs.count(),
        'total_views': total_views,
        'total_likes': total_likes,
        'total_clicks': total_clicks,
        'total_comments': total_comments,
        'pending_applications': JobApplication.objects.filter(user=request.user, status='pending').count(),
        'approved_without_job': approved_apps.count(),
    }
    return render(request, 'jobs/my_posted_jobs.html', context)


@login_required
def my_job_analytics(request, slug):
    job = get_object_or_404(Job, slug=slug, posted_by=request.user)

    last_30_days = timezone.now() - timedelta(days=30)
    views_last_30_days = job.view_logs.filter(viewed_at__gte=last_30_days)

    daily_views = {}
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        count = views_last_30_days.filter(viewed_at__date=date).count()
        daily_views[date.strftime('%Y-%m-%d')] = count

    context = {
        'job': job,
        'daily_views': json.dumps(daily_views),
        'total_views': job.views,
        'unique_views': job.view_logs.values('session_key').distinct().count(),
        'total_likes': job.likes,
        'total_comments': job.comments.filter(is_approved=True).count(),
        'total_clicks': job.clicks,
        'applications': job.applications_count,
        'recent_views': job.view_logs.order_by('-viewed_at')[:10],
        'recent_likes': job.likes_log.order_by('-created_at')[:10],
        'recent_comments': job.comments.filter(is_approved=True).order_by('-created_at')[:10],
        'recent_clicks': job.click_logs.order_by('-clicked_at')[:10],
    }
    return render(request, 'jobs/job_analytics.html', context)


@login_required
def edit_posted_job(request, slug):
    job = get_object_or_404(Job, slug=slug, posted_by=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('my_posted_jobs')
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})


# ========== JOB APPLICATION (POST JOB) ==========

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user

            if not application.contact_email:
                application.contact_email = request.user.email

            application.save()

            try:
                send_mail(
                    subject=f'Job Post Submitted: {application.title}',
                    message=f"""
Dear {request.user.username},

Thank you for submitting your job post "{application.title}" at {application.company}!

📋 What happens next?
1. Our team will review your job post within 24-48 hours
2. You will receive an email notification once it's approved
3. Once approved, your job will be visible to thousands of job seekers

📋 Job Details:
- Title: {application.title}
- Company: {application.company}
- Location: {application.location}
- Status: Pending Approval

You can track the status of your submission on your dashboard.

Thank you for choosing Job Reference Hub!

Best regards,
The Job Reference Hub Team
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[application.contact_email, request.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.warning(request, 'Your job was submitted but we could not send a confirmation email. Please contact support.')

            messages.success(request, 'Your job post has been submitted for approval! You will receive a confirmation email once it is reviewed.')
            return redirect('job_submitted_success')
    else:
        form = JobApplicationForm(initial={
            'contact_email': request.user.email,
        })

    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def job_submitted_success(request):
    return render(request, 'jobs/submitted_success.html')


@login_required
def my_job_posts(request):
    applications = JobApplication.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'jobs/my_jobs.html', {'applications': applications})


def search_jobs(request):
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(is_active=True)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        location = form.cleaned_data.get('location')
        employment_type = form.cleaned_data.get('employment_type')
        work_type = form.cleaned_data.get('work_type')
        category_id = form.cleaned_data.get('category')

        if query:
            jobs = jobs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(company__icontains=query)
            )
        if location:
            jobs = jobs.filter(location__icontains=location)
        if employment_type:
            jobs = jobs.filter(employment_type=employment_type)
        if work_type:
            jobs = jobs.filter(work_type=work_type)
        if category_id:
            try:
                jobs = jobs.filter(category_id=int(category_id))
            except ValueError:
                pass

    # Paginate results
    paginator = Paginator(jobs, 15)
    page = request.GET.get('page')

    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    # Add counts to context
    context = {
        'jobs': jobs,
        'search_form': form,
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'remote_count': Job.objects.filter(is_active=True, work_type='remote').count(),
        'physical_count': Job.objects.filter(is_active=True, work_type='physical').count(),
        'full_time_count': Job.objects.filter(is_active=True, employment_type='full_time').count(),
        'part_time_count': Job.objects.filter(is_active=True, employment_type='part_time').count(),
        'contract_count': Job.objects.filter(is_active=True, employment_type='contract').count(),
        'daily_count': Job.objects.filter(is_active=True, employment_type='daily').count(),
        'categories': Category.objects.all(),
        'today': timezone.now().date(),
        'is_paginated': jobs.has_other_pages(),
        'page_obj': jobs,
        'paginator': paginator,
    }

    if request.user.is_authenticated:
        context['saved_ids'] = list(SavedJob.objects.filter(
            user=request.user
        ).values_list('job_id', flat=True))
    else:
        context['saved_ids'] = []

    return render(request, 'jobs/job_list.html', context)