from django.urls import path
from . import views

urlpatterns = [
    # Registration & Verification
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),

    # Login & Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('logout-confirm/', views.logout_confirm, name='logout_confirm'),

    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),

    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
]