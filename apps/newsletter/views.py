from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .forms import SubscriberForm
from .models import Subscriber
from django.utils import timezone

class SubscribeView(CreateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'newsletter/subscribe_success.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        subscriber, created = Subscriber.objects.get_or_create(email=email)

        if created:
            messages.success(self.request, 'Successfully subscribed to job alerts!')
        else:
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.save()
                messages.success(self.request, 'You have been re-subscribed!')
            else:
                messages.info(self.request, 'You are already subscribed!')

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

        return redirect(self.success_url)

def unsubscribe(request, email):
    subscriber = get_object_or_404(Subscriber, email=email)
    if subscriber.is_active:
        subscriber.is_active = False
        subscriber.unsubscribed_at = timezone.now()
        subscriber.save()
        messages.success(request, 'Successfully unsubscribed from job alerts.')
    else:
        messages.info(request, 'You were already unsubscribed.')

    return render(request, 'newsletter/unsubscribe.html')