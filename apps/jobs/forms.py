# apps/jobs/forms.py
from django import forms
from .models import Job, JobComment, JobApplication
from apps.categories.models import Category


# ============================================================
# JOB FORM (Admin / Edit)
# ============================================================

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            # Common fields
            'title', 'company', 'location', 'description', 'requirements',
            'work_type', 'category',
            'apply_url', 'company_website', 'contact_email', 'contact_phone',
            'is_active', 'is_featured', 'is_urgent', 'expires_at',

            # Full Time / Part Time fields
            'employment_type', 'experience_level',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period',
            'benefits', 'is_remote',
            'shift_type', 'hours_per_week', 'hourly_rate', 'salary_range',
            'currency', 'is_flexible_schedule', 'is_weekend_available', 'is_immediate',

            # Daily Wage fields
            'payment_method', 'payment_amount',
            'start_date', 'end_date', 'working_hours', 'is_immediate_joining',

            # Contract fields
            'contract_type', 'budget_min', 'budget_max', 'contract_currency',
            'contract_experience_level', 'duration_type', 'estimated_duration',
            'contract_start_date', 'contract_end_date', 'is_contract_remote',
            'is_contract_urgent',
        ]
        widgets = {
            # Common
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job title'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job location'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'work_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'apply_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@company.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_urgent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),

            # Full Time / Part Time
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '30000'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '50000'}),
            'salary_currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'salary_period': forms.Select(attrs={'class': 'form-control'}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Health insurance, 401k, etc.'}),
            'is_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shift_type': forms.Select(attrs={'class': 'form-control'}),
            'hours_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 40, 'placeholder': '20'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '15.00'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., $15-20/hour'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'is_flexible_schedule': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_weekend_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_immediate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Daily Wage
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Amount'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'working_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 9 AM - 5 PM'}),
            'is_immediate_joining': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Contract
            'contract_type': forms.Select(attrs={'class': 'form-control'}),
            'budget_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Min budget'}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Max budget'}),
            'contract_currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'contract_experience_level': forms.Select(attrs={'class': 'form-control'}),
            'duration_type': forms.Select(attrs={'class': 'form-control'}),
            'estimated_duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3 months'}),
            'contract_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_contract_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_contract_urgent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ============================================================
# JOB COMMENT FORM
# ============================================================

class JobCommentForm(forms.ModelForm):
    class Meta:
        model = JobComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment...'
            })
        }


# ============================================================
# JOB SEARCH FORM
# ============================================================

class JobSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Job title, skills, or keywords',
            'class': 'search-input'
        })
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'City, state, or remote',
            'class': 'search-input'
        })
    )

    # Work Type
    work_type = forms.ChoiceField(
        choices=[('', 'All Types'), ('physical', 'On-Site'), ('remote', 'Remote')],
        required=False,
        widget=forms.Select(attrs={'class': 'search-select'})
    )

    # Employment Type
    employment_type = forms.ChoiceField(
        choices=[
            ('', 'All Employment Types'),
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract', 'Contract'),
            ('freelance', 'Freelance'),
            ('temporary', 'Temporary')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'search-select'})
    )

    # Experience Level
    experience_level = forms.ChoiceField(
        choices=[
            ('', 'All Levels'),
            ('entry', 'Entry Level'),
            ('mid', 'Mid Level'),
            ('senior', 'Senior Level'),
            ('lead', 'Lead/Manager'),
            ('executive', 'Executive')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'search-select'})
    )

    # Daily Wage Filters
    payment_method = forms.ChoiceField(
        choices=[
            ('', 'All Payment Types'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'search-select'})
    )

    # Contract Filters
    contract_type = forms.ChoiceField(
        choices=[
            ('', 'All Contract Types'),
            ('fixed', 'Fixed Price'),
            ('hourly', 'Hourly Rate'),
            ('milestone', 'Milestone Based')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'search-select'})
    )

    # Salary / Budget Range
    salary_min = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'search-input', 'placeholder': 'Min'}))
    salary_max = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'search-input', 'placeholder': 'Max'}))


# ============================================================
# JOB APPLICATION FORM (User Submitted)
# ============================================================

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            # Common fields
            'title', 'company', 'location', 'work_type', 'category',
            'description', 'requirements',
            'apply_url', 'company_website',
            'contact_email', 'contact_phone',

            # Full Time / Part Time fields
            'employment_type', 'experience_level',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period',
            'benefits', 'is_remote',
            'shift_type', 'hours_per_week', 'hourly_rate', 'salary_range',
            'currency', 'is_flexible_schedule', 'is_weekend_available', 'is_immediate',

            # Daily Wage fields
            'payment_method', 'payment_amount',
            'start_date', 'end_date', 'working_hours', 'is_immediate_joining',

            # Contract fields
            'contract_type', 'budget_min', 'budget_max', 'contract_currency',
            'contract_experience_level', 'duration_type', 'estimated_duration',
            'contract_start_date', 'contract_end_date', 'is_contract_remote',
            'is_contract_urgent',
        ]
        widgets = {
            # Common
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Python Developer'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, State, or Remote'
            }),
            'work_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe the job role, responsibilities, and what makes this opportunity great...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'List the qualifications, skills, and experience required...'
            }),
            'apply_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/apply'
            }),
            'company_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://company.com'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@company.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),

            # Full Time / Part Time
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '30000'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '50000'
            }),
            'salary_currency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'USD'
            }),
            'salary_period': forms.Select(attrs={'class': 'form-control'}),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List benefits like health insurance, 401k, remote work, etc.'
            }),
            'is_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shift_type': forms.Select(attrs={'class': 'form-control'}),
            'hours_per_week': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 40,
                'placeholder': '20'
            }),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '15.00'
            }),
            'salary_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., $15-20/hour'
            }),
            'currency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'USD'
            }),
            'is_flexible_schedule': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_weekend_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_immediate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Daily Wage
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Amount'
            }),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'working_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 9 AM - 5 PM'
            }),
            'is_immediate_joining': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Contract
            'contract_type': forms.Select(attrs={'class': 'form-control'}),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Min budget'
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Max budget'
            }),
            'contract_currency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'USD'
            }),
            'contract_experience_level': forms.Select(attrs={'class': 'form-control'}),
            'duration_type': forms.Select(attrs={'class': 'form-control'}),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 3 months'
            }),
            'contract_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_contract_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_contract_urgent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = 'Select a category'