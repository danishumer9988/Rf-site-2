from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from django.utils import timezone
from .models import Category
from apps.jobs.models import Job, SavedJob
from apps.internships.models import Internship, SavedInternship

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'categories/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object

        # Get all active jobs and internships for this category
        jobs = category.jobs.filter(is_active=True)
        internships = category.internships.filter(is_active=True)

        # Get total counts
        total_jobs = jobs.count()
        total_internships = internships.count()

        # ✅ ADD LAST UPDATED - Check both jobs and internships in this category
        latest_job = jobs.order_by('-posted_at').first()
        latest_internship = internships.order_by('-posted_at').first()

        if latest_job and latest_internship:
            context['last_updated'] = max(latest_job.posted_at, latest_internship.posted_at)
        elif latest_job:
            context['last_updated'] = latest_job.posted_at
        elif latest_internship:
            context['last_updated'] = latest_internship.posted_at
        else:
            context['last_updated'] = timezone.now()

        # Calculate remote/onsite counts
        remote_count = jobs.filter(type='remote').count() + internships.filter(type='remote').count()
        onsite_count = jobs.filter(type='physical').count() + internships.filter(type='physical').count()

        # Get unique companies
        companies = set()
        for job in jobs:
            companies.add(job.company)
        for internship in internships:
            companies.add(internship.company)
        total_companies = len(companies)

        # Combine into all_opportunities list for the template
        all_opportunities = []

        # Add jobs
        for job in jobs:
            all_opportunities.append({
                'id': job.id,
                'slug': job.slug,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'salary': job.salary,
                'posted_at': job.posted_at,
                'type': 'job',
                'work_type': job.type,
                'is_internship': False,
                'is_featured': getattr(job, 'is_featured', False),
                'is_new': job.posted_at.date() == timezone.now().date(),
                'duration': None,
                'stipend': None,
            })

        # Add internships
        for internship in internships:
            all_opportunities.append({
                'id': internship.id,
                'slug': internship.slug,
                'title': internship.title,
                'company': internship.company,
                'location': internship.location,
                'salary': None,
                'posted_at': internship.posted_at,
                'type': 'internship',
                'work_type': internship.type,
                'is_internship': True,
                'is_featured': getattr(internship, 'is_featured', False),
                'is_new': internship.posted_at.date() == timezone.now().date(),
                'duration': internship.duration if hasattr(internship, 'duration') else None,
                'stipend': internship.stipend if hasattr(internship, 'stipend') else None,
            })

        # Sort by date (newest first)
        all_opportunities.sort(key=lambda x: x['posted_at'], reverse=True)

        # Check saved items for authenticated user
        if self.request.user.is_authenticated:
            saved_job_ids = list(SavedJob.objects.filter(
                user=self.request.user
            ).values_list('job_id', flat=True))

            saved_internship_ids = list(SavedInternship.objects.filter(
                user=self.request.user
            ).values_list('internship_id', flat=True))

            # Mark saved items
            for item in all_opportunities:
                if item['type'] == 'job':
                    item['is_saved'] = item['id'] in saved_job_ids
                else:
                    item['is_saved'] = item['id'] in saved_internship_ids
        else:
            for item in all_opportunities:
                item['is_saved'] = False

        # Add all data to context
        context.update({
            'all_opportunities': all_opportunities,
            'jobs': jobs,
            'internships': internships,
            'total_jobs': total_jobs,
            'total_internships': total_internships,
            'total_companies': total_companies,
            'remote_count': remote_count,
            'onsite_count': onsite_count,
        })

        return context