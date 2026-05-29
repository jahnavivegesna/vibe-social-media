"""
VIBE - Django Forms
====================
Forms handle user input validation and rendering.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile, Post, Comment, Report


# ============================================================
# AUTHENTICATION FORMS
# ============================================================
class SignupForm(UserCreationForm):
    """User registration form with extra fields."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'your@email.com',
            'class': 'vibe-input'
        })
    )
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a username',
            'class': 'vibe-input'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'First name',
            'class': 'vibe-input'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'class': 'vibe-input'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create password',
            'class': 'vibe-input'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm password',
            'class': 'vibe-input'
        })

    def clean_email(self):
        """Check if email is already in use."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        """Check if username is already taken."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        # Only allow letters, numbers, underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Custom login form with styling."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or email',
            'class': 'vibe-input'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'vibe-input'
        })
    )


# ============================================================
# PROFILE FORMS
# ============================================================
class EditProfileForm(forms.ModelForm):
    """Edit user profile information."""
    first_name = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'vibe-input', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'vibe-input', 'placeholder': 'Last name'})
    )

    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_pic', 'cover_pic', 'website', 'location', 'is_private']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'vibe-input',
                'placeholder': 'Tell people about yourself...',
                'rows': 3
            }),
            'website': forms.URLInput(attrs={
                'class': 'vibe-input',
                'placeholder': 'https://yourwebsite.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'vibe-input',
                'placeholder': 'Where are you from?'
            }),
            'profile_pic': forms.FileInput(attrs={'class': 'file-input', 'accept': 'image/*'}),
            'cover_pic': forms.FileInput(attrs={'class': 'file-input', 'accept': 'image/*'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'vibe-checkbox'}),
        }


# ============================================================
# POST FORMS
# ============================================================
class PostForm(forms.ModelForm):
    """Create or edit a post."""
    class Meta:
        model = Post
        fields = ['content', 'image', 'video', 'post_type']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'vibe-input post-textarea',
                'placeholder': "What's on your mind? Use #hashtags!",
                'rows': 4,
                'maxlength': 2000,
            }),
            'image': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*',
                'id': 'image-upload'
            }),
            'video': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'video/*',
                'id': 'video-upload'
            }),
            'post_type': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        content = cleaned_data.get('content')

        if not content and not image and not video:
            raise forms.ValidationError("Please add some content to your post.")

        if image and video:
            raise forms.ValidationError("You can only upload an image OR a video, not both.")

        # Set post_type automatically
        if image:
            cleaned_data['post_type'] = 'image'
        elif video:
            cleaned_data['post_type'] = 'video'
        else:
            cleaned_data['post_type'] = 'text'

        return cleaned_data


class CommentForm(forms.ModelForm):
    """Add a comment to a post."""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'vibe-input comment-input',
                'placeholder': 'Write a comment...',
                'maxlength': 500,
            })
        }


# ============================================================
# REPORT FORM
# ============================================================
class ReportForm(forms.ModelForm):
    """Report a post or user."""
    class Meta:
        model = Report
        fields = ['report_type', 'description']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'vibe-select'}),
            'description': forms.Textarea(attrs={
                'class': 'vibe-input',
                'placeholder': 'Describe the issue...',
                'rows': 3
            })
        }
