from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.utils import timezone
from .models import Internship, SavedInternship, InternshipView
from apps.categories.models import Category


class InternshipListView(ListView):
    model = Internship
    template_name = 'internships/internship_list.html'
    context_object_name = 'internships'
    paginate_by = 15

    def get_queryset(self):
        queryset = Internship.objects.filter(is_active=True)

        # Get search parameters
        search = self.request.GET.get('search', '')
        category_id = self.request.GET.get('category', '')
        internship_type = self.request.GET.get('internship_type', '')  # full_time or part_time
        work_type = self.request.GET.get('type', '')  # remote or physical

        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(company__icontains=search) |
                Q(description__icontains=search) |
                Q(requirements__icontains=search)
            )

        if category_id:
            try:
                queryset = queryset.filter(category_id=int(category_id))
            except ValueError:
                pass

        if internship_type:
            queryset = queryset.filter(internship_type=internship_type)

        if work_type:
            queryset = queryset.filter(type=work_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        latest_internship = Internship.objects.filter(is_active=True).order_by('-posted_at').first()
        context['last_updated'] = latest_internship.posted_at if latest_internship else timezone.now()

        # Get counts for stats
        context['total_internships'] = Internship.objects.filter(is_active=True).count()
        context['remote_count'] = Internship.objects.filter(is_active=True, type='remote').count()
        context['physical_count'] = Internship.objects.filter(is_active=True, type='physical').count()
        context['full_time_count'] = Internship.objects.filter(is_active=True, internship_type='full_time').count()
        context['part_time_count'] = Internship.objects.filter(is_active=True, internship_type='part_time').count()

        # Get categories for dropdown
        categories = Category.objects.annotate(
            internship_count=models.Count('internships', filter=Q(internships__is_active=True))
        ).filter(internship_count__gt=0)
        context['categories'] = categories

        # Get today's date
        context['today'] = timezone.now().date()

        # Get saved internships for user
        if self.request.user.is_authenticated:
            saved_internships = SavedInternship.objects.filter(
                user=self.request.user
            ).values_list('internship_id', flat=True)
            context['saved_ids'] = list(saved_internships)
        else:
            context['saved_ids'] = []

        return context


class FullTimeInternshipListView(ListView):
    model = Internship
    template_name = 'internships/full_time/internship_list.html'
    context_object_name = 'internships'
    paginate_by = 15

    def get_queryset(self):
        return Internship.objects.filter(is_active=True, internship_type='full_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['total_internships'] = Internship.objects.filter(is_active=True).count()
        context['remote_count'] = Internship.objects.filter(is_active=True, type='remote').count()
        context['physical_count'] = Internship.objects.filter(is_active=True, type='physical').count()
        context['full_time_count'] = Internship.objects.filter(is_active=True, internship_type='full_time').count()
        context['part_time_count'] = Internship.objects.filter(is_active=True, internship_type='part_time').count()
        context['categories'] = Category.objects.annotate(
            internship_count=models.Count('internships', filter=Q(internships__is_active=True))
        ).filter(internship_count__gt=0)

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedInternship.objects.filter(
                user=self.request.user
            ).values_list('internship_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


class PartTimeInternshipListView(ListView):
    model = Internship
    template_name = 'internships/part_time/internship_list.html'
    context_object_name = 'internships'
    paginate_by = 15

    def get_queryset(self):
        return Internship.objects.filter(is_active=True, internship_type='part_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        context['total_internships'] = Internship.objects.filter(is_active=True).count()
        context['remote_count'] = Internship.objects.filter(is_active=True, type='remote').count()
        context['physical_count'] = Internship.objects.filter(is_active=True, type='physical').count()
        context['full_time_count'] = Internship.objects.filter(is_active=True, internship_type='full_time').count()
        context['part_time_count'] = Internship.objects.filter(is_active=True, internship_type='part_time').count()
        context['categories'] = Category.objects.annotate(
            internship_count=models.Count('internships', filter=Q(internships__is_active=True))
        ).filter(internship_count__gt=0)

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedInternship.objects.filter(
                user=self.request.user
            ).values_list('internship_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


class PhysicalInternshipListView(ListView):
    model = Internship
    template_name = 'internships/physical_internships.html'
    context_object_name = 'internships'
    paginate_by = 15

    def get_queryset(self):
        return Internship.objects.filter(is_active=True, type='physical')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        latest_internship = Internship.objects.filter(
            is_active=True, type='physical'
        ).order_by('-posted_at').first()
        context['last_updated'] = latest_internship.posted_at if latest_internship else timezone.now()
        context['today'] = timezone.now().date()

        categories = Category.objects.annotate(
            internship_count=models.Count('internships', filter=Q(internships__is_active=True, internships__type='physical'))
        ).filter(internship_count__gt=0)
        context['categories'] = categories.count()

        context['new_count'] = Internship.objects.filter(
            is_active=True, type='physical',
            posted_at__date=timezone.now().date()
        ).count()

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedInternship.objects.filter(
                user=self.request.user
            ).values_list('internship_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


class RemoteInternshipListView(ListView):
    model = Internship
    template_name = 'internships/remote_internships.html'
    context_object_name = 'internships'
    paginate_by = 15

    def get_queryset(self):
        return Internship.objects.filter(is_active=True, type='remote')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        latest_internship = Internship.objects.filter(
            is_active=True, type='remote'
        ).order_by('-posted_at').first()
        context['last_updated'] = latest_internship.posted_at if latest_internship else timezone.now()
        context['today'] = timezone.now().date()

        categories = Category.objects.annotate(
            internship_count=models.Count('internships', filter=Q(internships__is_active=True, internships__type='remote'))
        ).filter(internship_count__gt=0)
        context['categories'] = categories.count()

        context['new_count'] = Internship.objects.filter(
            is_active=True, type='remote',
            posted_at__date=timezone.now().date()
        ).count()

        if self.request.user.is_authenticated:
            context['saved_ids'] = list(SavedInternship.objects.filter(
                user=self.request.user
            ).values_list('internship_id', flat=True))
        else:
            context['saved_ids'] = []

        return context


class InternshipDetailView(DetailView):
    model = Internship
    template_name = 'internships/internship_detail.html'
    context_object_name = 'internship'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        internship = self.get_object()

        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        viewed = InternshipView.objects.filter(internship=internship, session_key=session_key).exists()

        if not viewed:
            internship.views += 1
            internship.save()
            InternshipView.objects.create(
                internship=internship,
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

        # Check if saved
        if self.request.user.is_authenticated:
            context['is_saved'] = SavedInternship.objects.filter(
                user=self.request.user, internship=self.object
            ).exists()
        else:
            context['is_saved'] = False

        # Get related internships
        context['related_internships'] = Internship.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:5]

        return context


@login_required
def save_internship(request, slug):
    internship = get_object_or_404(Internship, slug=slug)
    saved_internship, created = SavedInternship.objects.get_or_create(
        user=request.user, internship=internship
    )

    if created:
        messages.success(request, f'Internship "{internship.title}" saved!')
    else:
        saved_internship.delete()
        messages.info(request, f'Internship removed from saved.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'saved': created})

    return redirect(request.META.get('HTTP_REFERER', 'internship_list'))


def search_internships(request):
    """Search internships with filters"""
    internships = Internship.objects.filter(is_active=True)

    query = request.GET.get('query', '')
    location = request.GET.get('location', '')
    work_type = request.GET.get('type', '')
    internship_type = request.GET.get('internship_type', '')
    category_slug = request.GET.get('category', '')

    if query:
        internships = internships.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(description__icontains=query) |
            Q(requirements__icontains=query)
        )

    if location:
        internships = internships.filter(location__icontains=location)

    if work_type:
        internships = internships.filter(type=work_type)

    if internship_type:
        internships = internships.filter(internship_type=internship_type)

    if category_slug:
        internships = internships.filter(category__slug=category_slug)

    paginator = Paginator(internships, 15)
    page = request.GET.get('page')

    try:
        internships = paginator.page(page)
    except PageNotAnInteger:
        internships = paginator.page(1)
    except EmptyPage:
        internships = paginator.page(paginator.num_pages)

    context = {
        'internships': internships,
        'total_internships': Internship.objects.filter(is_active=True).count(),
        'remote_count': Internship.objects.filter(is_active=True, type='remote').count(),
        'physical_count': Internship.objects.filter(is_active=True, type='physical').count(),
        'full_time_count': Internship.objects.filter(is_active=True, internship_type='full_time').count(),
        'part_time_count': Internship.objects.filter(is_active=True, internship_type='part_time').count(),
        'categories': Category.objects.all(),
        'today': timezone.now().date(),
        'is_paginated': internships.has_other_pages(),
        'page_obj': internships,
        'paginator': paginator,
    }

    if request.user.is_authenticated:
        context['saved_ids'] = list(SavedInternship.objects.filter(
            user=request.user
        ).values_list('internship_id', flat=True))
    else:
        context['saved_ids'] = []

    return render(request, 'internships/internship_list.html', context)