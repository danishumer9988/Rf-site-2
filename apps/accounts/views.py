from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView, View
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import timedelta
from django.http import JsonResponse
from .forms import (
    CustomRegistrationForm,
    VerificationForm,
    UserRegistrationForm,
    UserLoginForm,
    UserUpdateForm,
    ProfileUpdateForm
)
from .models import Profile
import logging

logger = logging.getLogger(__name__)

# ========== PASSWORD RESET VIEWS ==========

def password_reset_request(request):
    """Request password reset email"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            # Generate token and UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build reset link
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            # Send email
            try:
                # Try to render HTML template
                try:
                    html_message = render_to_string('emails/password_reset_email.html', {
                        'user': user,
                        'reset_link': reset_link,
                        'site_name': 'Job Reference Hub',
                        'site_url': request.build_absolute_uri('/'),
                        'request': request,
                    })
                    plain_message = strip_tags(html_message)
                except Exception as template_error:
                    # Fallback to plain text if template not found
                    print(f"Template error: {template_error}")
                    plain_message = f"""
Hello {user.first_name or user.username},

We received a request to reset your password for your Job Reference Hub account.

To reset your password, click the link below:
{reset_link}

This link will expire in 24 hours for security reasons.

If you didn't request this, please ignore this email.

Best regards,
The Job Reference Hub Team
"""
                    html_message = None

                # Send email
                if html_message:
                    send_mail(
                        subject='Password Reset Request - Job Reference Hub',
                        message=plain_message,
                        html_message=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                else:
                    send_mail(
                        subject='Password Reset Request - Job Reference Hub',
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )

                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('password_reset_done')

            except Exception as e:
                print(f"Email sending error: {str(e)}")
                messages.error(request, f'Failed to send reset email: {str(e)}')
                return render(request, 'accounts/password_reset.html')

        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            messages.info(request, 'If an account exists with this email, you will receive a password reset link.')
            return redirect('password_reset_done')

    return render(request, 'accounts/password_reset.html')

def password_reset_done(request):
    """Page shown after password reset email is sent"""
    return render(request, 'accounts/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    """Confirm password reset with token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully. Please login with your new password.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)

        return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'validlink': True})
    else:
        return render(request, 'accounts/password_reset_confirm.html', {'validlink': False})

def password_reset_complete(request):
    """Password reset complete page"""
    return render(request, 'accounts/password_reset_complete.html')

# ========== REGISTRATION VIEWS ==========

class RegisterView(View):
    """Custom registration view without CSRF token requirement"""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = CustomRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = CustomRegistrationForm(request.POST)

        if form.is_valid():
            # Get cleaned data
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            user_type = form.cleaned_data['user_type']
            password = form.cleaned_data['password']

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email or '',
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Update profile
            profile = user.profile
            profile.phone_number = phone_number
            profile.user_type = user_type
            profile.first_name = first_name
            profile.last_name = last_name
            profile.email_verified = False

            # Generate verification code
            verification_code = profile.generate_verification_code()
            profile.verification_code = verification_code
            profile.verification_code_created_at = timezone.now()
            profile.save()

            # Send verification email
            if email:
                try:
                    html_message = render_to_string('emails/verification_email.html', {
                        'first_name': first_name,
                        'verification_code': verification_code,
                        'site_name': 'Job Reference Hub',
                    })
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject='Verify Your Email - Job Reference Hub',
                        message=plain_message,
                        html_message=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                    messages.success(request, 'Registration successful! We sent a verification code to your email.')
                except Exception as e:
                    logger.error(f"Email sending failed: {str(e)}")
                    messages.warning(request, 'Registration successful but we could not send the verification email. Please contact support.')
            else:
                messages.info(request, 'Registration successful! Please check your phone for verification.')

            # Store user ID in session for verification
            request.session['pending_verification_user_id'] = user.id

            return redirect('verify_email')

        # Form errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field.replace('_', ' ').title()}: {error}")

        return render(request, 'accounts/register.html', {'form': form})

class VerifyEmailView(View):
    """Email verification view"""

    def get(self, request):
        user_id = request.session.get('pending_verification_user_id')

        if not user_id:
            messages.warning(request, 'No pending verification found. Please register first.')
            return redirect('register')

        try:
            user = User.objects.get(id=user_id)
            profile = user.profile

            # Check if already verified
            if profile.email_verified:
                messages.info(request, 'Your email is already verified. Please login.')
                return redirect('login')

            # Check if code is expired (15 minutes)
            if profile.verification_code_created_at:
                expiry_time = profile.verification_code_created_at + timedelta(minutes=15)
                if timezone.now() > expiry_time:
                    # Generate new code
                    new_code = profile.generate_verification_code()
                    profile.verification_code = new_code
                    profile.verification_code_created_at = timezone.now()
                    profile.save()

                    # Send new code
                    if user.email:
                        try:
                            html_message = render_to_string('emails/verification_email.html', {
                                'first_name': user.first_name,
                                'verification_code': new_code,
                                'site_name': 'Job Reference Hub',
                            })
                            plain_message = strip_tags(html_message)

                            send_mail(
                                subject='New Verification Code - Job Reference Hub',
                                message=plain_message,
                                html_message=html_message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[user.email],
                                fail_silently=False,
                            )
                            messages.info(request, 'Your previous code expired. A new code has been sent to your email.')
                        except Exception:
                            messages.warning(request, 'Your code expired. Please request a new one.')

        except User.DoesNotExist:
            messages.error(request, 'User not found. Please register again.')
            return redirect('register')

        form = VerificationForm()
        return render(request, 'accounts/verify_email.html', {'form': form, 'user': user})

    def post(self, request):
        user_id = request.session.get('pending_verification_user_id')

        if not user_id:
            messages.warning(request, 'No pending verification found.')
            return redirect('register')

        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('register')

        form = VerificationForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['verification_code']

            # Check if code matches
            if profile.verification_code == code:
                # Check if code is not expired
                if profile.verification_code_created_at:
                    expiry_time = profile.verification_code_created_at + timedelta(minutes=15)
                    if timezone.now() <= expiry_time:
                        # Verify user
                        profile.email_verified = True
                        profile.verification_code = None
                        profile.verification_code_created_at = None
                        profile.save()

                        # Log user in
                        login(request, user)

                        # Clear session
                        del request.session['pending_verification_user_id']

                        messages.success(request, f'Welcome {user.first_name}! Your email has been verified.')
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Verification code has expired. Please request a new one.')
                else:
                    messages.error(request, 'Invalid verification request. Please try again.')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')

        return render(request, 'accounts/verify_email.html', {'form': form, 'user': user})

class ResendVerificationView(View):
    """Resend verification code"""

    def post(self, request):
        user_id = request.session.get('pending_verification_user_id')

        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'No pending verification found.'})

        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'})

        if profile.email_verified:
            return JsonResponse({'status': 'error', 'message': 'Your email is already verified.'})

        # Generate new code
        new_code = profile.generate_verification_code()
        profile.verification_code = new_code
        profile.verification_code_created_at = timezone.now()
        profile.save()

        # Send new code
        if user.email:
            try:
                html_message = render_to_string('emails/verification_email.html', {
                    'first_name': user.first_name,
                    'verification_code': new_code,
                    'site_name': 'Job Reference Hub',
                })
                plain_message = strip_tags(html_message)

                send_mail(
                    subject='New Verification Code - Job Reference Hub',
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                return JsonResponse({'status': 'success', 'message': 'New code sent successfully!'})
            except Exception:
                return JsonResponse({'status': 'error', 'message': 'Failed to send email. Please try again.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No email address provided.'})

class ProfileView(DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        if user_form.is_valid():
            user_form.save()
            form.save()
            messages.success(self.request, 'Profile updated successfully!')
            return redirect('profile')
        return self.render_to_response(self.get_context_data(form=form))

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')

            # ✅ AFTER LOGIN, GO TO THE PAGE USER WANTED
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)  # Goes to /jobs/post/
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    next_url = request.GET.get('next', '')
    return render(request, 'accounts/login.html', {'next': next_url})

def logout_view(request):
    """Logout view with confirmation page - handles both GET and POST"""
    if not request.user.is_authenticated:
        messages.info(request, 'You are already logged out.')
        return redirect('home')

    if request.method == 'POST':
        username = request.user.username
        logout(request)
        messages.success(request, f'Goodbye {username}! You have been logged out successfully.')
        return redirect('home')

    return render(request, 'accounts/logout.html')

def logout_confirm(request):
    """Logout confirmation page"""
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'accounts/logout.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})