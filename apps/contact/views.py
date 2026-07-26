from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import ContactForm
from .models import ContactMessage

class ContactCreateView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'contact/contact.html'
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your message has been sent successfully! We will get back to you soon.')
        return response