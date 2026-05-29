"""
VIBE Social Media - Database Models
=====================================
This file defines ALL database tables using Django ORM.
Each class = one database table.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


# ============================================================
# USER PROFILE - extends default Django User
# ============================================================
class UserProfile(models.Model):
    """
    Extended user profile with bio, avatar, privacy settings, etc.
    Every User automatically gets one UserProfile (created via signal).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, default='')
    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        default=None
    )
    website = models.URLField(blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    is_private = models.BooleanField(default=False)  # private/public profile
    is_verified = models.BooleanField(default=False)  # blue tick
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Cover/banner image for profile
    cover_pic = models.ImageField(upload_to='cover_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_profile_pic_url(self):
        """Returns profile pic URL or a default avatar URL"""
        if self.profile_pic:
            return self.profile_pic.url
        return '/static/images/default_avatar.png'

    def get_followers_count(self):
        return Follow.objects.filter(following=self.user).count()

    def get_following_count(self):
        return Follow.objects.filter(follower=self.user).count()

    def get_posts_count(self):
        return Post.objects.filter(author=self.user, is_deleted=False).count()


# ============================================================
# POSTS - text, image, or video posts
# ============================================================
class Post(models.Model):
    """
    A post can be text-only, have an image, or have a video.
    """
    POST_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2000)
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')

    # Media attachments
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)  # soft delete

    # Hashtags are extracted from content dynamically
    # But we also store them for faster search
    hashtags = models.ManyToManyField('Hashtag', blank=True, related_name='posts')

    class Meta:
        ordering = ['-created_at']  # newest first

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"

    def get_likes_count(self):
        return Like.objects.filter(post=self, is_active=True).count()

    def get_comments_count(self):
        return Comment.objects.filter(post=self, is_deleted=False).count()

    def is_liked_by(self, user):
        """Check if a specific user has liked this post"""
        if user.is_authenticated:
            return Like.objects.filter(post=self, user=user, is_active=True).exists()
        return False


# ============================================================
# COMMENTS - comments on posts
# ============================================================
class Comment(models.Model):
    """Comments on posts. Supports nested replies (parent comment)."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}"


# ============================================================
# LIKES - likes on posts
# ============================================================
class Like(models.Model):
    """Tracks which user liked which post."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # toggle like/unlike

    class Meta:
        unique_together = ('user', 'post')  # one like per user per post

    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"


# ============================================================
# REACTIONS - emoji reactions on posts
# ============================================================
class Reaction(models.Model):
    """Emoji reactions (like, love, haha, wow, sad, angry)."""
    REACTION_TYPES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('haha', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😡'),
        ('fire', '🔥'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # one reaction per user per post


# ============================================================
# FOLLOWS - follow/unfollow system
# ============================================================
class Follow(models.Model):
    """
    Tracks follower/following relationships.
    follower = the person who follows
    following = the person being followed
    """
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


# ============================================================
# FRIEND REQUESTS
# ============================================================
class FriendRequest(models.Model):
    """Friend requests between users (for private profiles)."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.status})"


# ============================================================
# NOTIFICATIONS
# ============================================================
class Notification(models.Model):
    """All notifications for a user."""
    NOTIFICATION_TYPES = [
        ('like', 'liked your post'),
        ('comment', 'commented on your post'),
        ('follow', 'started following you'),
        ('mention', 'mentioned you'),
        ('friend_request', 'sent you a friend request'),
        ('friend_accepted', 'accepted your friend request'),
        ('share', 'shared your post'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} {self.notification_type} → {self.recipient.username}"

    def get_message(self):
        return f"{self.sender.username} {dict(self.NOTIFICATION_TYPES)[self.notification_type]}"


# ============================================================
# REPORTS
# ============================================================
class Report(models.Model):
    """Report system for posts and users."""
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('violence', 'Violence'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reports_received', null=True, blank=True
    )
    reported_post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='reports', null=True, blank=True
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report by {self.reporter.username} - {self.report_type}"


# ============================================================
# BLOCKED USERS
# ============================================================
class BlockedUser(models.Model):
    """Track who has blocked whom."""
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"


# ============================================================
# HASHTAGS
# ============================================================
class Hashtag(models.Model):
    """Hashtags for categorizing posts."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name}"

    def get_post_count(self):
        return self.posts.filter(is_deleted=False).count()


# ============================================================
# MESSAGES (Direct Messages)
# ============================================================
class Message(models.Model):
    """Direct messages between users."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(max_length=1000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"
