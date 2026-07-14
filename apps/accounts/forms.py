from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Profile
from django.contrib.auth.forms import SetPasswordForm
import re

# ========== CUSTOM REGISTRATION FORM ==========
class CustomRegistrationForm(forms.Form):
    """Custom registration form without CSRF token requirement"""

    # User information
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'John',
            'class': 'form-control',
            'id': 'firstName'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Doe',
            'class': 'form-control',
            'id': 'lastName'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'johndoe123',
            'class': 'form-control',
            'id': 'username'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'john@example.com (optional)',
            'class': 'form-control',
            'id': 'email'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '+1 234 567 8900',
            'class': 'form-control',
            'id': 'phoneNumber'
        })
    )
    user_type = forms.ChoiceField(
        choices=Profile.USER_TYPES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'userType'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'form-control',
            'id': 'password'
        })
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'form-control',
            'id': 'confirmPassword'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters long.')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('Username can only contain letters, numbers and underscores.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError('Please enter a valid email address.')
            if User.objects.filter(email=email).exists():
                raise ValidationError('This email is already registered.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone or len(phone) < 10:
            raise ValidationError('Please enter a valid phone number.')
        return phone

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')

        return cleaned_data

# ========== VERIFICATION FORM ==========
class VerificationForm(forms.Form):
    """Verification code form"""
    verification_code = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit code',
            'class': 'form-control',
            'id': 'verificationCode',
            'maxlength': '6'
        })
    )

# ========== USER REGISTRATION FORM (Django default) ==========
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email

# ========== USER LOGIN FORM ==========
class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

# ========== USER UPDATE FORM ==========
class UserUpdateForm(forms.ModelForm):
    """Form for updating user information"""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
                raise ValidationError('This email is already registered.')
        return email

# ========== PROFILE UPDATE FORM ==========
class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""

    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'phone', 'location', 'website', 'linkedin', 'github']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 234 567 8900'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'github': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourusername'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 10:
            raise ValidationError('Please enter a valid phone number.')
        return phone