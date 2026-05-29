"""
VIBE - URL Patterns
====================
Maps URLs to views. Think of this as the app's routing table.
"""

from django.urls import path
from . import views

urlpatterns = [
    # ============================================================
    # HOME
    # ============================================================
    path('', views.home_feed, name='home'),

    # ============================================================
    # AUTHENTICATION
    # ============================================================
    path('auth/signup/', views.signup_view, name='signup'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),

    # ============================================================
    # POSTS
    # ============================================================
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/report/', views.report_post, name='report_post'),

    # ============================================================
    # COMMENTS
    # ============================================================
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # ============================================================
    # USERS / PROFILES
    # ============================================================
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('profile/<str:username>/block/', views.block_user, name='block_user'),
    path('profile/<str:username>/unblock/', views.unblock_user, name='unblock_user'),

    # ============================================================
    # EXPLORE & SEARCH
    # ============================================================
    path('explore/', views.explore, name='explore'),
    path('hashtag/<str:tag_name>/', views.hashtag_feed, name='hashtag_feed'),

    # ============================================================
    # NOTIFICATIONS
    # ============================================================
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),

    # ============================================================
    # SETTINGS
    # ============================================================
    path('settings/', views.settings_view, name='settings'),
    path('settings/change-password/', views.change_password, name='change_password'),

    # ============================================================
    # ADMIN DASHBOARD (separate from Django's built-in admin)
    # ============================================================
    path('vibe-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('vibe-admin/users/', views.admin_users, name='admin_users'),
    path('vibe-admin/report/<int:report_id>/resolve/', views.admin_resolve_report, name='admin_resolve_report'),
    path('vibe-admin/user/<int:user_id>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),

    # ============================================================
    # API ENDPOINTS (AJAX)
    # ============================================================
    path('api/posts/', views.api_get_posts, name='api_get_posts'),
    path('api/notifications/count/', views.get_notifications_ajax, name='api_notifications_count'),
]
