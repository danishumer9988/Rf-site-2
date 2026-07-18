from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/<str:email>/', views.unsubscribe, name='unsubscribe'),
    # ===== NEW FEEDBACK ROUTES =====
    path('feedback/', views.feedback_chat, name='feedback_chat'),
    path('feedback/submit/', views.feedback_submit, name='feedback_submit'),
]