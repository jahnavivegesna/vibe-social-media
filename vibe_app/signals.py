"""
VIBE - Django Signals
======================
Signals are like "event listeners" in Django.
When something happens (like creating a user), we automatically do something else.
"""

from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, Follow, Like, Comment, Notification
import re


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new User is created.
    'created' is True only when the User is first created (not on updates).
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Automatically save the UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """Send notification when someone likes a post."""
    if created and instance.is_active:
        # Don't notify yourself
        if instance.user != instance.post.author:
            # Avoid duplicate notifications
            Notification.objects.get_or_create(
                recipient=instance.post.author,
                sender=instance.user,
                notification_type='like',
                post=instance.post,
            )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """Send notification when someone comments on a post."""
    if created and not instance.is_deleted:
        if instance.author != instance.post.author:
            Notification.objects.create(
                recipient=instance.post.author,
                sender=instance.author,
                notification_type='comment',
                post=instance.post,
            )


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """Send notification when someone follows a user."""
    if created:
        Notification.objects.create(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='follow',
        )
