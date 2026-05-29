"""VIBE - Django Admin Registration"""
from django.contrib import admin
from .models import (
    UserProfile, Post, Comment, Like, Follow,
    Notification, Report, BlockedUser, Hashtag, FriendRequest
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_private', 'is_verified', 'created_at']
    search_fields = ['user__username', 'bio']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'post_type', 'created_at', 'is_deleted']
    list_filter = ['post_type', 'is_deleted']
    search_fields = ['content', 'author__username']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'is_deleted']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'report_type', 'status', 'created_at']
    list_filter = ['status', 'report_type']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']

admin.site.register(Like)
admin.site.register(Notification)
admin.site.register(BlockedUser)
admin.site.register(Hashtag)
