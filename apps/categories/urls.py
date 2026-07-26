from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
]