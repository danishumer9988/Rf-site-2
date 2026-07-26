from django.urls import path
from . import views


urlpatterns = [
    # Main listing
    path('', views.JobListView.as_view(), name='job_list'),

    # By employment type
    path('full-time/', views.FullTimeJobListView.as_view(), name='full_time_jobs'),
    path('part-time/', views.PartTimeJobListView.as_view(), name='part_time_jobs'),
    path('contract/', views.ContractJobListView.as_view(), name='contract_jobs'),
    path('daily/', views.DailyJobListView.as_view(), name='daily_jobs'),

    # By work location
    path('remote/', views.RemoteJobListView.as_view(), name='remote_jobs'),
    path('physical/', views.PhysicalJobListView.as_view(), name='physical_jobs'),
    path('onsite/', views.OnSiteJobListView.as_view(), name='onsite_jobs'),

    # Search
    path('search/', views.search_jobs, name='search_jobs'),

    # Post job
    path('post/', views.post_job, name='post_job'),
    path('post/submitted/', views.job_submitted_success, name='job_submitted_success'),

    # User dashboard
    path('my-posts/', views.my_posted_jobs, name='my_posted_jobs'),
    path('my-posts/<slug:slug>/analytics/', views.my_job_analytics, name='my_job_analytics'),
    path('my-posts/<slug:slug>/edit/', views.edit_posted_job, name='edit_posted_job'),
    path('post/my-posts/', views.my_job_posts, name='my_job_posts'),

    # Job interactions
    path('<slug:slug>/', views.JobDetailView.as_view(), name='job_detail'),
    path('<slug:slug>/save/', views.save_job, name='save_job'),
    path('<slug:slug>/like/', views.like_job, name='like_job'),
    path('<slug:slug>/comment/', views.comment_job, name='comment_job'),
    path('<slug:slug>/track-click/', views.track_click, name='track_click'),

    # Comments
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]