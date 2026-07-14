from django import forms
from .models import Internship


class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = [
            'title', 'company', 'location', 'description', 'requirements',
            'stipend', 'duration', 'type', 'internship_type', 'category',
            'apply_url', 'company_website', 'is_active', 'expires_at'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Internship title'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'stipend': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., $1000/month'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3 months'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'internship_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'apply_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class InternshipSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search internships...', 'class': 'search-input'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'City, state', 'class': 'search-input'}))
    type = forms.ChoiceField(
        choices=[('', 'All Types'), ('physical', 'On-Site'), ('remote', 'Remote')],
        required=False
    )
    internship_type = forms.ChoiceField(
        choices=[('', 'All'), ('full_time', 'Full-Time'), ('part_time', 'Part-Time')],
        required=False
    )
    category = forms.ChoiceField(required=False)