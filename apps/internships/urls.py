from django.urls import path
from . import views

urlpatterns = [
    # Main listing
    path('', views.InternshipListView.as_view(), name='internship_list'),

    # By employment type
    path('full-time/', views.FullTimeInternshipListView.as_view(), name='full_time_internships'),
    path('part-time/', views.PartTimeInternshipListView.as_view(), name='part_time_internships'),

    # By work location
    path('remote/', views.RemoteInternshipListView.as_view(), name='remote_internships'),
    path('onsite/', views.PhysicalInternshipListView.as_view(), name='onsite_internships'),
    path('physical/', views.PhysicalInternshipListView.as_view(), name='physical_internships'),

    # Search
    path('search/', views.search_internships, name='search_internships'),

    # Save
    path('<slug:slug>/save/', views.save_internship, name='save_internship'),

    # Detail (must be last)
    path('<slug:slug>/', views.InternshipDetailView.as_view(), name='internship_detail'),
]