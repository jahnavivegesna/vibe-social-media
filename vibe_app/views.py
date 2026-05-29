"""
VIBE Social Media - Views
==========================
Views are functions/classes that handle web requests and return responses.
Each view = one page or one API endpoint.
"""

import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone

from .models import (
    UserProfile, Post, Comment, Like, Follow,
    Notification, Report, BlockedUser, Hashtag,
    FriendRequest, Reaction
)
from .forms import (
    SignupForm, LoginForm, EditProfileForm,
    PostForm, CommentForm, ReportForm
)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def extract_hashtags(text):
    """Extract hashtags from text like #python #django → ['python', 'django']"""
    return re.findall(r'#(\w+)', text.lower())


def get_user_feed_posts(user):
    """Get posts for a user's feed (from people they follow + their own)."""
    following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
    blocked_users = BlockedUser.objects.filter(blocker=user).values_list('blocked', flat=True)

    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=user)
    ).exclude(
        author__in=blocked_users
    ).filter(
        is_deleted=False
    ).select_related('author', 'author__profile').prefetch_related('likes', 'comments')

    return posts


# ============================================================
# HOME FEED
# ============================================================
@login_required
def home_feed(request):
    """
    Main home page with infinite scroll feed.
    Shows posts from users you follow.
    """
    page_num = request.GET.get('page', 1)
    posts_qs = get_user_feed_posts(request.user)
    paginator = Paginator(posts_qs, 10)  # 10 posts per page
    posts = paginator.get_page(page_num)

    # Trending hashtags
    trending = Hashtag.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:10]

    # Suggested users (not already following)
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    suggested_users = User.objects.exclude(
        id__in=list(following_ids) + [request.user.id]
    ).select_related('profile').order_by('?')[:5]

    # Post creation form
    post_form = PostForm()

    context = {
        'posts': posts,
        'trending_hashtags': trending,
        'suggested_users': suggested_users,
        'post_form': post_form,
        'page_title': 'Home',
    }
    return render(request, 'home/feed.html', context)


# ============================================================
# AUTHENTICATION VIEWS
# ============================================================
def signup_view(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to VIBE, {user.username}! 🎉')
            return redirect('home')
        else:
            # Show specific errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignupForm()

    return render(request, 'auth/signup.html', {'form': form, 'page_title': 'Sign Up'})


    
def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Allow login with email too
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                pass

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Welcome back, {user.username}! ✨')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    form = LoginForm()
    return render(request, 'auth/login.html', {'form': form, 'page_title': 'Login'})


@login_required
def logout_view(request):
    """Logout user."""
    logout(request)
    messages.success(request, 'You have been logged out. See you soon!')
    return redirect('login')


# ============================================================
# POST VIEWS
# ============================================================
@login_required
@require_POST
def create_post(request):
    """Create a new post (handles AJAX and regular form submission)."""
    form = PostForm(request.POST, request.FILES)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        # Extract and save hashtags
        hashtag_names = extract_hashtags(post.content)
        for tag_name in hashtag_names:
            hashtag, created = Hashtag.objects.get_or_create(name=tag_name)
            post.hashtags.add(hashtag)

        if is_ajax:
            return JsonResponse({
                'success': True,
                'post_id': post.id,
                'message': 'Post created successfully!'
            })
        messages.success(request, 'Your post is live! 🚀')
        return redirect('home')

    if is_ajax:
        return JsonResponse({'success': False, 'errors': form.errors})

    messages.error(request, 'Error creating post. Please try again.')
    return redirect('home')


@login_required
def post_detail(request, post_id):
    """View a single post with all comments."""
    post = get_object_or_404(Post, id=post_id, is_deleted=False)

    # Block check
    if BlockedUser.objects.filter(blocker=request.user, blocked=post.author).exists():
        messages.error(request, 'You have blocked this user.')
        return redirect('home')

    comments = Comment.objects.filter(
        post=post, parent=None, is_deleted=False
    ).select_related('author', 'author__profile')

    comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': post.is_liked_by(request.user),
        'page_title': f'Post by {post.author.username}',
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def delete_post(request, post_id):
    """Delete a post (soft delete)."""
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.is_deleted = True
    post.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Post deleted.')
    return redirect('home')


# ============================================================
# LIKE / UNLIKE (AJAX)
# ============================================================
@login_required
@require_POST
def toggle_like(request, post_id):
    """Toggle like on a post. Returns JSON for AJAX updates."""
    post = get_object_or_404(Post, id=post_id, is_deleted=False)

    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        # Already liked → toggle
        like.is_active = not like.is_active
        like.save()
        liked = like.is_active
    else:
        liked = True

    likes_count = Like.objects.filter(post=post, is_active=True).count()

    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': likes_count
    })


# ============================================================
# COMMENTS (AJAX)
# ============================================================
@login_required
@require_POST
def add_comment(request, post_id):
    """Add a comment to a post."""
    post = get_object_or_404(Post, id=post_id, is_deleted=False)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'success': False, 'error': 'Comment cannot be empty'})

    if len(content) > 500:
        return JsonResponse({'success': False, 'error': 'Comment too long (max 500 chars)'})

    parent_id = request.POST.get('parent_id')
    parent = None
    if parent_id:
        parent = get_object_or_404(Comment, id=parent_id)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
        parent=parent
    )

    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username,
            'author_pic': comment.author.profile.get_profile_pic_url(),
            'created_at': comment.created_at.strftime('%b %d, %Y'),
            'is_reply': parent is not None,
        },
        'comments_count': Comment.objects.filter(post=post, is_deleted=False).count()
    })


@login_required
def delete_comment(request, comment_id):
    """Delete a comment."""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.is_deleted = True
    comment.save()
    return JsonResponse({'success': True})


# ============================================================
# FOLLOW / UNFOLLOW (AJAX)
# ============================================================
@login_required
@require_POST
def toggle_follow(request, username):
    """Follow or unfollow a user."""
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return JsonResponse({'success': False, 'error': "You can't follow yourself"})

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user
    )

    if not created:
        # Already following → unfollow
        follow.delete()
        is_following = False
    else:
        is_following = True

    followers_count = Follow.objects.filter(following=target_user).count()

    return JsonResponse({
        'success': True,
        'is_following': is_following,
        'followers_count': followers_count
    })


# ============================================================
# USER PROFILE
# ============================================================
def user_profile(request, username):
    """View a user's profile page."""
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=profile_user)

    # Check if blocked
    if request.user.is_authenticated:
        if BlockedUser.objects.filter(blocker=request.user, blocked=profile_user).exists():
            messages.error(request, 'You have blocked this user.')
            return redirect('home')

    # Check if current user follows this user
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, following=profile_user
        ).exists()

    # Get posts (respect privacy)
    if profile.is_private and not is_following and request.user != profile_user:
        posts = Post.objects.none()
        is_private_and_not_following = True
    else:
        posts = Post.objects.filter(
            author=profile_user, is_deleted=False
        ).select_related('author', 'author__profile')
        is_private_and_not_following = False

    paginator = Paginator(posts, 12)
    page_num = request.GET.get('page', 1)
    posts_page = paginator.get_page(page_num)

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts_page,
        'is_following': is_following,
        'is_own_profile': request.user == profile_user,
        'is_private_and_not_following': is_private_and_not_following,
        'followers_count': profile.get_followers_count(),
        'following_count': profile.get_following_count(),
        'posts_count': profile.get_posts_count(),
        'page_title': f'{profile_user.username}\'s Profile',
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """Edit current user's profile."""
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save first_name and last_name to User model
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully! ✨')
            return redirect('user_profile', username=request.user.username)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = EditProfileForm(
            instance=profile,
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        )

    return render(request, 'users/edit_profile.html', {
        'form': form,
        'profile': profile,
        'page_title': 'Edit Profile'
    })


@login_required
def followers_list(request, username):
    """Show list of followers for a user."""
    profile_user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(
        following=profile_user
    ).select_related('follower', 'follower__profile')

    return render(request, 'users/followers_list.html', {
        'profile_user': profile_user,
        'follows': followers,
        'list_type': 'Followers',
        'page_title': f'{username}\'s Followers',
    })


@login_required
def following_list(request, username):
    """Show list of users someone follows."""
    profile_user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        follower=profile_user
    ).select_related('following', 'following__profile')

    return render(request, 'users/followers_list.html', {
        'profile_user': profile_user,
        'follows': following,
        'list_type': 'Following',
        'page_title': f'{username}\'s Following',
    })


# ============================================================
# EXPLORE / SEARCH
# ============================================================
def explore(request):
    """Explore page with search, trending posts, suggested users."""
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')

    posts = Post.objects.none()
    users = User.objects.none()
    hashtags = Hashtag.objects.none()

    if query:
        if search_type in ['all', 'posts']:
            posts = Post.objects.filter(
                Q(content__icontains=query),
                is_deleted=False
            ).select_related('author', 'author__profile')[:20]

        if search_type in ['all', 'users']:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).select_related('profile')[:20]

        if search_type in ['all', 'hashtags']:
            if query.startswith('#'):
                query_clean = query[1:]
            else:
                query_clean = query
            hashtags = Hashtag.objects.filter(name__icontains=query_clean)[:10]
    else:
        # Show trending content when no search
        posts = Post.objects.filter(
            is_deleted=False
        ).annotate(
            like_count=Count('likes')
        ).order_by('-like_count', '-created_at')[:20]

    trending_hashtags = Hashtag.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:15]

    context = {
        'query': query,
        'search_type': search_type,
        'posts': posts,
        'users': users,
        'hashtags': hashtags,
        'trending_hashtags': trending_hashtags,
        'page_title': 'Explore',
    }
    return render(request, 'explore/explore.html', context)


# ============================================================
# NOTIFICATIONS
# ============================================================
@login_required
def notifications(request):
    """View all notifications."""
    notifs = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'sender__profile', 'post')[:50]

    # Mark all as read when viewed
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)

    return render(request, 'notifications/notifications.html', {
        'notifications': notifs,
        'page_title': 'Notifications'
    })


@login_required
def mark_notification_read(request, notif_id):
    """Mark a single notification as read."""
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'success': True})


@login_required
def get_notifications_ajax(request):
    """Get unread notifications count for live updates."""
    count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()
    return JsonResponse({'count': count})


# ============================================================
# REPORT
# ============================================================
@login_required
def report_post(request, post_id):
    """Report a post."""
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_post = post
            report.reported_user = post.author
            report.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Report submitted.'})
            messages.success(request, 'Post reported. We will review it.')
            return redirect('home')

    return JsonResponse({'success': False, 'error': 'Invalid request'})


# ============================================================
# BLOCK USERS
# ============================================================
@login_required
@require_POST
def block_user(request, username):
    """Block a user."""
    user_to_block = get_object_or_404(User, username=username)

    BlockedUser.objects.get_or_create(
        blocker=request.user,
        blocked=user_to_block
    )

    # Also unfollow them
    Follow.objects.filter(follower=request.user, following=user_to_block).delete()
    Follow.objects.filter(follower=user_to_block, following=request.user).delete()

    messages.success(request, f'You have blocked {username}.')
    return redirect('home')


@login_required
@require_POST
def unblock_user(request, username):
    """Unblock a user."""
    user_to_unblock = get_object_or_404(User, username=username)
    BlockedUser.objects.filter(blocker=request.user, blocked=user_to_unblock).delete()
    messages.success(request, f'You have unblocked {username}.')
    return redirect('user_profile', username=username)


# ============================================================
# SETTINGS
# ============================================================
@login_required
def settings_view(request):
    """User settings page."""
    blocked_users = BlockedUser.objects.filter(
        blocker=request.user
    ).select_related('blocked', 'blocked__profile')

    return render(request, 'settings/settings.html', {
        'blocked_users': blocked_users,
        'page_title': 'Settings'
    })


@login_required
def change_password(request):
    """Change user password."""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            login(request, request.user)  # Re-login after password change
            messages.success(request, 'Password changed successfully!')
            return redirect('settings')

    return redirect('settings')


# ============================================================
# HASHTAG FEED
# ============================================================
def hashtag_feed(request, tag_name):
    """Show all posts with a specific hashtag."""
    hashtag = get_object_or_404(Hashtag, name=tag_name.lower())
    posts = Post.objects.filter(
        hashtags=hashtag, is_deleted=False
    ).select_related('author', 'author__profile').order_by('-created_at')

    paginator = Paginator(posts, 12)
    posts_page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'explore/hashtag_feed.html', {
        'hashtag': hashtag,
        'posts': posts_page,
        'page_title': f'#{tag_name}',
    })


# ============================================================
# ADMIN DASHBOARD
# ============================================================
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with analytics."""
    from django.db.models import Count
    from datetime import timedelta

    today = timezone.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    stats = {
        'total_users': User.objects.count(),
        'new_users_week': User.objects.filter(date_joined__gte=week_ago).count(),
        'total_posts': Post.objects.filter(is_deleted=False).count(),
        'new_posts_week': Post.objects.filter(created_at__gte=week_ago, is_deleted=False).count(),
        'total_likes': Like.objects.filter(is_active=True).count(),
        'total_comments': Comment.objects.filter(is_deleted=False).count(),
        'pending_reports': Report.objects.filter(status='pending').count(),
        'total_follows': Follow.objects.count(),
    }

    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_posts = Post.objects.filter(is_deleted=False).order_by('-created_at')[:10]
    pending_reports = Report.objects.filter(status='pending').select_related(
        'reporter', 'reported_user', 'reported_post'
    )[:20]

    # Top users by followers
    top_users = User.objects.annotate(
        follower_count=Count('followers_set')
    ).order_by('-follower_count')[:10]

    return render(request, 'admin_panel/dashboard.html', {
        'stats': stats,
        'recent_users': recent_users,
        'recent_posts': recent_posts,
        'pending_reports': pending_reports,
        'top_users': top_users,
        'page_title': 'Admin Dashboard',
    })


@staff_member_required
def admin_resolve_report(request, report_id):
    """Resolve or dismiss a report."""
    report = get_object_or_404(Report, id=report_id)
    action = request.POST.get('action')

    if action == 'resolve':
        report.status = 'resolved'
        report.reviewed_at = timezone.now()
        report.save()
        messages.success(request, 'Report resolved.')
    elif action == 'dismiss':
        report.status = 'dismissed'
        report.reviewed_at = timezone.now()
        report.save()
        messages.info(request, 'Report dismissed.')
    elif action == 'delete_post' and report.reported_post:
        report.reported_post.is_deleted = True
        report.reported_post.save()
        report.status = 'resolved'
        report.reviewed_at = timezone.now()
        report.save()
        messages.success(request, 'Post deleted and report resolved.')

    return redirect('admin_dashboard')


@staff_member_required
def admin_users(request):
    """List all users for management."""
    users = User.objects.select_related('profile').order_by('-date_joined')
    paginator = Paginator(users, 20)
    users_page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'admin_panel/users.html', {
        'users': users_page,
        'page_title': 'User Management',
    })


@staff_member_required
def admin_toggle_user(request, user_id):
    """Activate or deactivate a user account."""
    user = get_object_or_404(User, id=user_id)
    if user != request.user:  # Can't deactivate yourself
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} {status}.')
    return redirect('admin_users')


# ============================================================
# API ENDPOINTS (for AJAX/live updates)
# ============================================================
@login_required
def api_get_posts(request):
    """API endpoint to load more posts for infinite scroll."""
    page = request.GET.get('page', 1)
    posts_qs = get_user_feed_posts(request.user)
    paginator = Paginator(posts_qs, 10)
    posts = paginator.get_page(page)

    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post.id,
            'content': post.content,
            'author': post.author.username,
            'author_pic': post.author.profile.get_profile_pic_url(),
            'created_at': post.created_at.strftime('%b %d, %Y'),
            'likes_count': post.get_likes_count(),
            'comments_count': post.get_comments_count(),
            'is_liked': post.is_liked_by(request.user),
            'post_type': post.post_type,
            'image': post.image.url if post.image else None,
            'video': post.video.url if post.video else None,
        })

    return JsonResponse({
        'posts': posts_data,
        'has_next': posts.has_next(),
        'next_page': posts.next_page_number() if posts.has_next() else None,
    })
