# 🎯 VIBE — Social Media Platform
### Built with Django + MySQL + Vanilla JS

> A full-featured, modern social media app with glassmorphism UI, dark mode, AJAX interactions, and a complete admin dashboard.

---

## 📁 Complete Folder Structure

```
vibe/
├── manage.py                          # Django CLI tool
├── requirements.txt                   # Python dependencies
│
├── vibe_project/                      # Django project config
│   ├── __init__.py
│   ├── settings.py                    # All settings (DB, apps, auth)
│   ├── urls.py                        # Root URL routing
│   └── wsgi.py                        # Production WSGI server
│
├── vibe_app/                          # Main app
│   ├── __init__.py
│   ├── apps.py                        # App config + signal registration
│   ├── models.py                      # ALL database models (tables)
│   ├── views.py                       # ALL page/API logic
│   ├── urls.py                        # App URL routing
│   ├── forms.py                       # Django forms (validation)
│   ├── signals.py                     # Auto-triggers (create profile, notify)
│   ├── admin.py                       # Django admin registration
│   ├── context_processors.py          # Global template data
│   └── migrations/                    # Database migration files
│
├── templates/                         # All HTML templates
│   ├── base/
│   │   └── base.html                  # Master layout (nav, sidebar, footer)
│   ├── home/
│   │   └── feed.html                  # Home feed page
│   ├── auth/
│   │   ├── login.html                 # Login page
│   │   └── signup.html                # Registration page
│   ├── posts/
│   │   ├── post_card.html             # Reusable post component
│   │   └── post_detail.html           # Single post + comments
│   ├── users/
│   │   ├── profile.html               # User profile page
│   │   ├── edit_profile.html          # Edit profile form
│   │   └── followers_list.html        # Followers/following list
│   ├── explore/
│   │   ├── explore.html               # Search + explore page
│   │   └── hashtag_feed.html          # Hashtag posts page
│   ├── notifications/
│   │   └── notifications.html         # Notifications page
│   ├── settings/
│   │   └── settings.html              # User settings page
│   └── admin_panel/
│       ├── dashboard.html             # Custom admin dashboard
│       └── users.html                 # User management
│
├── static/
│   ├── css/
│   │   └── main.css                   # Complete responsive CSS (glassmorphism, dark mode)
│   ├── js/
│   │   └── main.js                    # All JS (AJAX, infinite scroll, etc.)
│   └── images/
│       └── default_avatar.png         # Default profile picture
│
└── media/                             # User uploads (auto-created)
    ├── profile_pics/
    ├── cover_pics/
    ├── post_images/
    └── post_videos/
```

---

## 🗄️ Database Schema

| Table | Key Fields | Purpose |
|-------|-----------|---------|
| `auth_user` | id, username, email, password | Django's built-in users |
| `userprofile` | user, bio, profile_pic, is_private | Extended profile data |
| `post` | author, content, image, video, post_type | All posts |
| `comment` | post, author, content, parent | Comments + replies |
| `like` | user, post, is_active | Like/unlike toggle |
| `reaction` | user, post, reaction_type | Emoji reactions |
| `follow` | follower, following | Follow relationships |
| `friendrequest` | sender, receiver, status | Friend request system |
| `notification` | recipient, sender, type, post | All notifications |
| `report` | reporter, reported_user/post, type | Reporting system |
| `blockeduser` | blocker, blocked | Block system |
| `hashtag` | name | Hashtag indexing |
| `message` | sender, receiver, content | Direct messages |

---

## ⚙️ Setup Guide (Step by Step)

### ✅ Prerequisites
- Python 3.10+ installed
- MySQL 8.0+ installed and running
- pip (Python package manager)

---

### 📌 Phase 1: MySQL Setup

Open MySQL command line or MySQL Workbench:

```sql
-- Create the database
CREATE DATABASE vibe_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a dedicated user (recommended)
CREATE USER 'vibe_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON vibe_db.* TO 'vibe_user'@'localhost';
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
```

---

### 📌 Phase 2: Python Environment

```bash
# 1. Navigate to the project folder
cd vibe

# 2. Create a virtual environment (isolates your dependencies)
python -m venv vibe_env

# 3. Activate it
# Windows:
vibe_env\Scripts\activate
# Mac/Linux:
source vibe_env/bin/activate

# 4. Install all dependencies
pip install -r requirements.txt
```

---

### 📌 Phase 3: Configure Database in settings.py

Edit `vibe_project/settings.py` — find the DATABASES section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vibe_db',          # ← your database name
        'USER': 'vibe_user',        # ← your MySQL username
        'PASSWORD': 'your_strong_password',  # ← your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

> **💡 Quick Testing?** Comment out MySQL settings and uncomment the SQLite fallback — no MySQL needed for testing!

---

### 📌 Phase 4: Run Django Setup Commands

```bash
# Create all database tables (reads models.py and makes SQL)
python manage.py makemigrations
python manage.py migrate

# Create a superuser (admin account)
python manage.py createsuperuser
# Enter: username, email, password

# Collect static files (CSS/JS) for production
python manage.py collectstatic --noinput
```

---

### 📌 Phase 5: Run the Development Server

```bash
python manage.py runserver
```

Open your browser: **http://127.0.0.1:8000**

---

## 🔑 Default URLs

| URL | Page |
|-----|------|
| `/` | Home Feed |
| `/auth/login/` | Login |
| `/auth/signup/` | Register |
| `/explore/` | Explore + Search |
| `/notifications/` | Notifications |
| `/profile/<username>/` | User Profile |
| `/settings/` | Settings |
| `/vibe-admin/` | Custom Admin Dashboard |
| `/django-admin/` | Django Built-in Admin |
| `/hashtag/<tag>/` | Hashtag Feed |

---

## 🌐 Google Login Setup (Optional)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project → Enable **Google+ API**
3. Go to **Credentials** → Create **OAuth 2.0 Client ID**
4. Set Authorized redirect URI: `http://localhost:8000/accounts/google/login/callback/`
5. Copy Client ID and Secret into `settings.py`:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'YOUR_CLIENT_ID_HERE',
            'secret': 'YOUR_SECRET_HERE',
        }
    }
}
```

6. In Django admin (`/django-admin/`):
   - Go to **Sites** → Set domain to `localhost:8000`
   - Go to **Social Applications** → Add Google with your credentials

---

## 🎨 Features Summary

### 🔐 Authentication
- ✅ Signup/Login with username or email
- ✅ Google OAuth login
- ✅ Password hashing (Django's built-in PBKDF2)
- ✅ Session management (30-day cookies)
- ✅ Logout

### 👤 User Profiles
- ✅ Username, bio, profile picture, cover photo
- ✅ Website + location
- ✅ Followers/following count with live updates
- ✅ Public/private profile toggle
- ✅ Edit profile page
- ✅ Verified badge support

### 📝 Posts
- ✅ Text posts
- ✅ Image posts (with preview)
- ✅ Video posts
- ✅ Hashtag auto-detection and linking
- ✅ @mention parsing
- ✅ Edit/delete posts (soft delete)
- ✅ Timestamps

### ❤️ Interactions (All AJAX/Real-time)
- ✅ Like/unlike with animation
- ✅ Comment system + nested replies
- ✅ Follow/unfollow
- ✅ Share posts (Web Share API + clipboard fallback)
- ✅ Infinite scroll feed

### 🔔 Notifications
- ✅ Like, comment, follow notifications
- ✅ Unread badge in navbar
- ✅ Live polling every 30 seconds
- ✅ Mark all as read on visit

### 🔍 Explore
- ✅ Search users, posts, hashtags
- ✅ Trending hashtags sidebar
- ✅ Suggested users
- ✅ Post grid + list views

### 🛡️ Safety
- ✅ Report posts/users
- ✅ Block/unblock users
- ✅ Privacy settings

### 🎛️ Admin Dashboard
- ✅ User/post/like/comment counts
- ✅ New users this week
- ✅ Pending reports management
- ✅ Top users by followers
- ✅ Recent posts table
- ✅ Activate/deactivate users

### 🎨 UI/UX
- ✅ Dark/light mode toggle (localStorage)
- ✅ Glassmorphism cards
- ✅ Animated gradients
- ✅ Toast notifications
- ✅ Skeleton loading
- ✅ Image lightbox
- ✅ Fully responsive (mobile + desktop)
- ✅ Mobile bottom navigation bar
- ✅ Smooth animations + hover effects

---

## 🚀 Production Deployment Checklist

```python
# In settings.py, change these for production:
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')  # Use environment variable!
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Use environment variables for DB credentials
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
```

```bash
# Production commands
pip install gunicorn
gunicorn vibe_project.wsgi:application --bind 0.0.0.0:8000
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `django.db.utils.OperationalError` | Check MySQL is running and credentials in settings.py are correct |
| `ModuleNotFoundError: mysqlclient` | Run `pip install mysqlclient` (may need MySQL dev headers) |
| Static files not loading | Run `python manage.py collectstatic` |
| Google login not working | Check Site domain in Django admin matches your URL |
| Images not uploading | Ensure `media/` folder exists and has write permissions |
| Port 8000 in use | Run `python manage.py runserver 8080` to use port 8080 |

---

## 📚 Tech Stack

- **Backend**: Django 4.2 (Python)
- **Database**: MySQL 8.0 (via mysqlclient)
- **ORM**: Django ORM (no raw SQL needed)
- **Auth**: Django Auth + django-allauth (Google OAuth)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (no frameworks!)
- **CSS**: Custom design system with CSS variables, glassmorphism, dark mode
- **JS Features**: Fetch API (AJAX), IntersectionObserver (infinite scroll), localStorage
- **Static Files**: WhiteNoise (development + production)
- **Media**: Django's built-in file handling + Pillow (image processing)

---

*Built with ❤️ as a college portfolio project — VIBE Social Media*
