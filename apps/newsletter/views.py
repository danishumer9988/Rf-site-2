from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import SubscriberForm, FeedbackForm
from .models import Subscriber, Feedback


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


# ========== NEW: FEEDBACK SUBMISSION (no bot saved) ==========

def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def feedback_chat(request):
    """Render the chat page with existing messages (user messages only)."""
    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None

    # Get only user messages (sender='user')
    if user:
        messages_qs = Feedback.objects.filter(user=user, sender='user')
    else:
        messages_qs = Feedback.objects.filter(session_key=session_key, user__isnull=True, sender='user')

    context = {
        'messages': messages_qs.order_by('created_at'),
        'form': FeedbackForm(),
    }
    return render(request, 'newsletter/feedback_chat.html', context)


def feedback_submit(request):
    """Handle AJAX submission – saves only the user message, bot reply not stored."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    form = FeedbackForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Invalid form data'}, status=400)

    # Save user message
    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None

    feedback = form.save(commit=False)
    feedback.user = user
    feedback.session_key = session_key
    feedback.sender = 'user'
    feedback.is_read = False
    feedback.save()

    # Prepare bot reply (not saved to database)
    bot_reply_text = "Thank you for your feedback! We'll get back to you if needed."

    # Return both messages as JSON (bot reply is ephemeral)
    return JsonResponse({
        'status': 'success',
        'user_message': {
            'id': feedback.id,
            'message': feedback.message,
            'created_at': feedback.created_at.strftime('%H:%M'),
            'sender': 'user'
        },
        'bot_message': {
            'id': 0,  # not stored
            'message': bot_reply_text,
            'created_at': timezone.now().strftime('%H:%M'),
            'sender': 'bot'
        }
    })