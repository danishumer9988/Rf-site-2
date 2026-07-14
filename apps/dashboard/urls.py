from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # User dashboard
    path('', views.dashboard_home, name='dashboard'),
    path('profile/', views.dashboard_profile, name='dashboard_profile'),
    path('saved-jobs/', views.dashboard_saved_jobs, name='dashboard_saved_jobs'),
    path('saved-internships/', views.dashboard_saved_internships, name='dashboard_saved_internships'),
    path('settings/', views.dashboard_settings, name='dashboard_settings'),

    # API endpoints
    path('api/pending-applications/', admin_views.api_pending_applications, name='api_pending_applications'),
    path('api/admin-stats/', admin_views.api_admin_stats, name='api_admin_stats'),

    # Admin dashboard
    path('admin-dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/analytics/', admin_views.admin_analytics, name='admin_analytics'),

    # Admin - Jobs
    path('admin-dashboard/jobs/', admin_views.admin_jobs, name='admin_jobs'),
    path('admin-dashboard/jobs/add/', admin_views.admin_add_job, name='admin_add_job'),
    path('admin-dashboard/jobs/edit/<int:pk>/', admin_views.admin_edit_job, name='admin_edit_job'),
    path('admin-dashboard/jobs/delete/<int:pk>/', admin_views.admin_delete_job, name='admin_delete_job'),
    path('admin-dashboard/jobs/toggle/<int:pk>/', admin_views.admin_toggle_job, name='admin_toggle_job'),

    # Admin - Internships
    path('admin-dashboard/internships/', admin_views.admin_internships, name='admin_internships'),
    path('admin-dashboard/internships/add/', admin_views.admin_add_internship, name='admin_add_internship'),
    path('admin-dashboard/internships/edit/<int:pk>/', admin_views.admin_edit_internship, name='admin_edit_internship'),
    path('admin-dashboard/internships/delete/<int:pk>/', admin_views.admin_delete_internship, name='admin_delete_internship'),

    # Admin - Categories
    path('admin-dashboard/categories/', admin_views.admin_categories, name='admin_categories'),
    path('admin-dashboard/categories/add/', admin_views.admin_add_category, name='admin_add_category'),
    path('admin-dashboard/categories/edit/<int:pk>/', admin_views.admin_edit_category, name='admin_edit_category'),
    path('admin-dashboard/categories/delete/<int:pk>/', admin_views.admin_delete_category, name='admin_delete_category'),

    # Admin - Users
    path('admin-dashboard/users/', admin_views.admin_users, name='admin_users'),

    # Admin - Contacts
    path('admin-dashboard/contacts/', admin_views.admin_contacts, name='admin_contacts'),
    path('admin-dashboard/contacts/read/<int:pk>/', admin_views.admin_mark_contact_read, name='admin_mark_contact_read'),
    path('admin-dashboard/contacts/unread/<int:pk>/', admin_views.admin_mark_contact_unread, name='admin_mark_contact_unread'),
    path('admin-dashboard/contacts/delete/<int:pk>/', admin_views.admin_delete_contact, name='admin_delete_contact'),

    # Admin - Subscribers
    path('admin-dashboard/subscribers/', admin_views.admin_subscribers, name='admin_subscribers'),
    path('admin-dashboard/subscribers/toggle/<int:pk>/', admin_views.admin_subscriber_toggle, name='admin_subscriber_toggle'),
    path('admin-dashboard/subscribers/delete/<int:pk>/', admin_views.admin_subscriber_delete, name='admin_subscriber_delete'),

    # Admin - Job Applications
    path('admin-dashboard/job-applications/', admin_views.admin_job_applications, name='admin_job_applications'),
    path('admin-dashboard/job-applications/approve/<int:pk>/', admin_views.admin_approve_application, name='admin_approve_application'),
    path('admin-dashboard/job-applications/reject/<int:pk>/', admin_views.admin_reject_application, name='admin_reject_application'),

    path('admin-dashboard/analytics/', admin_views.admin_analytics, name='admin_analytics'),
    path('api/admin-analytics/', admin_views.admin_analytics_api, name='admin_analytics_api'),

    path('analytics/', views.user_analytics, name='user_analytics'),
]