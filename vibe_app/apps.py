"""VIBE App Configuration"""
from django.apps import AppConfig


class VibeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vibe_app'
    verbose_name = 'VIBE Social'

    def ready(self):
        """Register signals when app is ready."""
        import vibe_app.signals
