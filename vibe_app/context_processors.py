"""
VIBE - Context Processors
==========================
Context processors add data to EVERY template automatically.
"""

from .models import Notification


def notifications_count(request):
    """Add unread notification count to all templates."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return {'unread_notifications': count}
    return {'unread_notifications': 0}
