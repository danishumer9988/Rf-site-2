from django.urls import path
from . import views  # or from pages import views

urlpatterns = [
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_of_service, name='terms'),
    path('faq/', views.faq, name='faq'),
]