from django.db import models
from django.contrib.auth.models import User

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


# ========== NEW: FEEDBACK / CHATBOT MODEL ==========

class Feedback(models.Model):
    SENDER_CHOICES = (
        ('user', 'User'),
        ('bot', 'Bot'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)  # for anonymous users
    email = models.EmailField(blank=True)
    message = models.TextField()
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES, default='user')
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Rating from 1 to 5"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"