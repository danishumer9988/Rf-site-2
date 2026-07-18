from django import forms
from .models import Subscriber, Feedback

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address',
                'class': 'newsletter-input'
            })
        }


# ========== NEW: FEEDBACK FORM ==========

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['email', 'message', 'rating']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Your email (optional)'}),
            'message': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your feedback here...'
            }),
            'rating': forms.Select(choices=[(None, 'Rate (optional)')] + [(i, f'{i} star') for i in range(1, 6)])
        }
        labels = {
            'email': 'Email (optional)',
            'message': 'Your feedback',
            'rating': 'Rating'
        }