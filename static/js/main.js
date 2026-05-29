/**
 * VIBE SOCIAL MEDIA - Main JavaScript
 * =====================================
 * Handles all client-side interactions:
 * - Like/unlike posts (AJAX)
 * - Comment submission (AJAX)
 * - Follow/unfollow (AJAX)
 * - Dark/light mode toggle
 * - Toast notifications
 * - Infinite scroll
 * - Post media preview
 * - Dropdown menus
 * - Live notification updates
 */

/* ============================================================
   CSRF TOKEN (needed for all POST requests to Django)
   ============================================================ */
function getCsrfToken() {
  // Get CSRF token from the cookie Django sets
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') return decodeURIComponent(value);
  }
  // Fallback: get from hidden input in page
  const input = document.querySelector('[name=csrfmiddlewaretoken]');
  return input ? input.value : '';
}

// Helper for AJAX POST requests
async function vibePost(url, data = {}, isFormData = false) {
  const headers = { 'X-Requested-With': 'XMLHttpRequest' };
  let body;

  if (isFormData) {
    data.append('csrfmiddlewaretoken', getCsrfToken());
    body = data;
  } else {
    headers['Content-Type'] = 'application/json';
    headers['X-CSRFToken'] = getCsrfToken();
    body = JSON.stringify(data);
  }

  const res = await fetch(url, { method: 'POST', headers, body });
  return res.json();
}

// Helper for AJAX GET requests
async function vibeGet(url) {
  const res = await fetch(url, {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  });
  return res.json();
}


/* ============================================================
   DARK / LIGHT MODE TOGGLE
   ============================================================ */
const ThemeManager = {
  init() {
    // Load saved theme
    const saved = localStorage.getItem('vibe-theme') || 'light';
    this.apply(saved);

    // Bind toggle button
    document.querySelectorAll('.theme-toggle').forEach(btn => {
      btn.addEventListener('click', () => this.toggle());
    });
  },

  apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('vibe-theme', theme);
    // Update toggle button icon
    document.querySelectorAll('.theme-toggle').forEach(btn => {
      btn.textContent = theme === 'dark' ? '☀️' : '🌙';
      btn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    });
  },

  toggle() {
    const current = document.documentElement.getAttribute('data-theme');
    this.apply(current === 'dark' ? 'light' : 'dark');
    Toast.show(current === 'dark' ? '☀️ Light mode on!' : '🌙 Dark mode on!', 'info');
  }
};


/* ============================================================
   TOAST NOTIFICATIONS
   ============================================================ */
const Toast = {
  container: null,

  init() {
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      this.container.id = 'toast-container';
      document.body.appendChild(this.container);
    }

    // Show Django messages as toasts
    document.querySelectorAll('.django-message').forEach(el => {
      this.show(el.textContent, el.dataset.type || 'info');
    });
  },

  show(message, type = 'info', duration = 4000) {
    const icons = {
      success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <span class="toast-msg">${message}</span>
      <button class="toast-close" onclick="Toast.dismiss(this.parentElement)">✕</button>
    `;

    this.container.appendChild(toast);

    // Auto-dismiss after duration
    setTimeout(() => this.dismiss(toast), duration);

    return toast;
  },

  dismiss(toast) {
    if (!toast || !toast.parentElement) return;
    toast.classList.add('hiding');
    setTimeout(() => toast.remove(), 300);
  }
};


/* ============================================================
   LIKE / UNLIKE SYSTEM
   ============================================================ */
const LikeSystem = {
  init() {
    // Event delegation - listen on document for like buttons
    document.addEventListener('click', (e) => {
      const likeBtn = e.target.closest('.like-btn');
      if (likeBtn) {
        e.preventDefault();
        this.toggleLike(likeBtn);
      }
    });
  },

  async toggleLike(btn) {
    const postId = btn.dataset.postId;
    if (!postId || btn.dataset.loading) return;

    btn.dataset.loading = 'true';
    const wasLiked = btn.classList.contains('liked');

    // Optimistic update (instant UI feedback)
    this.updateBtn(btn, !wasLiked);

    try {
      const data = await vibePost(`/posts/${postId}/like/`);
      if (data.success) {
        this.updateBtn(btn, data.liked, data.likes_count);
        if (data.liked) {
          btn.style.transform = 'scale(1.2)';
          setTimeout(() => btn.style.transform = '', 300);
        }
      } else {
        // Revert on error
        this.updateBtn(btn, wasLiked);
        Toast.show('Failed to like post', 'error');
      }
    } catch (err) {
      this.updateBtn(btn, wasLiked);
      Toast.show('Network error', 'error');
    }

    delete btn.dataset.loading;
  },

  updateBtn(btn, liked, count) {
    const countEl = btn.querySelector('.like-count');
    const iconEl = btn.querySelector('.like-icon-svg');

    if (liked) {
      btn.classList.add('liked');
      if (iconEl) iconEl.textContent = '❤️';
    } else {
      btn.classList.remove('liked');
      if (iconEl) iconEl.textContent = '🤍';
    }

    if (count !== undefined && countEl) {
      countEl.textContent = count;
    }
  }
};


/* ============================================================
   COMMENT SYSTEM
   ============================================================ */
const CommentSystem = {
  init() {
    // Submit comment on Enter key or button click
    document.addEventListener('submit', (e) => {
      if (e.target.classList.contains('comment-form-ajax')) {
        e.preventDefault();
        this.submit(e.target);
      }
    });

    // Toggle comment section visibility
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.comment-btn');
      if (btn) {
        const postId = btn.dataset.postId;
        this.toggleSection(postId);
      }
    });
  },

  async submit(form) {
    const postId = form.dataset.postId;
    const input = form.querySelector('.comment-input');
    const content = input.value.trim();

    if (!content) {
      Toast.show('Please write a comment first', 'warning');
      return;
    }

    input.disabled = true;

    try {
      const formData = new FormData();
      formData.append('content', content);
      formData.append('csrfmiddlewaretoken', getCsrfToken());

      const parentId = form.dataset.parentId;
      if (parentId) formData.append('parent_id', parentId);

      const res = await fetch(`/posts/${postId}/comment/`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      });
      const data = await res.json();

      if (data.success) {
        input.value = '';
        this.renderComment(data.comment, postId);

        // Update comment count
        const countEl = document.querySelector(`[data-post-id="${postId}"] .comment-count`);
        if (countEl) countEl.textContent = data.comments_count;
      } else {
        Toast.show(data.error || 'Failed to post comment', 'error');
      }
    } catch (err) {
      Toast.show('Network error', 'error');
    }

    input.disabled = false;
    input.focus();
  },

  renderComment(comment, postId) {
    const section = document.querySelector(`.comments-list[data-post-id="${postId}"]`);
    if (!section) return;

    const html = `
      <div class="comment-item" data-comment-id="${comment.id}">
        <img src="${comment.author_pic}" alt="${comment.author}" onerror="this.src='/static/images/default_avatar.png'">
        <div class="comment-bubble">
          <span class="comment-author-name">${comment.author}</span>
          <p class="comment-text">${this.escapeHtml(comment.content)}</p>
          <div class="comment-meta">
            <span class="comment-time">Just now</span>
          </div>
        </div>
      </div>
    `;

    section.insertAdjacentHTML('beforeend', html);
    section.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  },

  toggleSection(postId) {
    const section = document.querySelector(`.comments-section[data-post-id="${postId}"]`);
    if (section) {
      section.classList.toggle('hidden');
    }
  },

  escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }
};


/* ============================================================
   FOLLOW SYSTEM
   ============================================================ */
const FollowSystem = {
  init() {
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('.follow-btn');
      if (btn && !btn.dataset.loading) {
        await this.toggleFollow(btn);
      }
    });
  },

  async toggleFollow(btn) {
    const username = btn.dataset.username;
    if (!username) return;

    btn.dataset.loading = 'true';
    btn.disabled = true;

    try {
      const data = await vibePost(`/profile/${username}/follow/`);

      if (data.success) {
        if (data.is_following) {
          btn.textContent = 'Following';
          btn.classList.add('following');
          Toast.show(`Now following @${username}! 🎉`, 'success');
        } else {
          btn.textContent = 'Follow';
          btn.classList.remove('following');
        }

        // Update follower count if on profile page
        const followerCountEl = document.querySelector('.follower-count');
        if (followerCountEl) {
          followerCountEl.textContent = data.followers_count;
        }
      } else {
        Toast.show(data.error || 'Failed to follow user', 'error');
      }
    } catch (err) {
      Toast.show('Network error', 'error');
    }

    btn.disabled = false;
    delete btn.dataset.loading;
  }
};


/* ============================================================
   POST CREATOR - Media Upload Preview
   ============================================================ */
const PostCreator = {
  init() {
    const imageInput = document.getElementById('image-upload');
    const videoInput = document.getElementById('video-upload');
    const textarea = document.querySelector('.post-textarea');
    const charCounter = document.querySelector('.char-counter');

    if (imageInput) {
      imageInput.addEventListener('change', (e) => this.previewMedia(e.target, 'image'));
    }

    if (videoInput) {
      videoInput.addEventListener('change', (e) => this.previewMedia(e.target, 'video'));
    }

    if (textarea && charCounter) {
      textarea.addEventListener('input', () => {
        const len = textarea.value.length;
        const max = 2000;
        charCounter.textContent = `${len}/${max}`;

        if (len > max * 0.9) charCounter.className = 'char-counter danger';
        else if (len > max * 0.75) charCounter.className = 'char-counter warning';
        else charCounter.className = 'char-counter';

        // Auto-resize textarea
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';

        // Parse hashtags in real time
        this.highlightHashtags(textarea);
      });
    }

    // Remove media button
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('remove-media')) {
        this.removeMedia(e.target);
      }
    });

    // Emoji picker trigger
    document.querySelectorAll('.emoji-btn').forEach(btn => {
      btn.addEventListener('click', () => this.toggleEmojiPicker());
    });
  },

  previewMedia(input, type) {
    const file = input.files[0];
    if (!file) return;

    // File size check (50MB)
    if (file.size > 50 * 1024 * 1024) {
      Toast.show('File too large! Max 50MB', 'error');
      input.value = '';
      return;
    }

    const preview = document.querySelector('.media-preview');
    if (!preview) return;

    const url = URL.createObjectURL(file);
    let content = '';

    if (type === 'image') {
      content = `<img src="${url}" alt="Preview">`;
      document.querySelector('#id_post_type') && (document.querySelector('#id_post_type').value = 'image');
    } else if (type === 'video') {
      content = `<video src="${url}" controls muted></video>`;
      document.querySelector('#id_post_type') && (document.querySelector('#id_post_type').value = 'video');
    }

    preview.innerHTML = content + `<button class="remove-media" data-type="${type}">✕</button>`;
    preview.classList.add('active');

    Toast.show(`${type === 'image' ? '📸 Image' : '🎥 Video'} ready to post!`, 'info');
  },

  removeMedia(btn) {
    const type = btn.dataset.type;
    const input = document.getElementById(`${type}-upload`);
    if (input) input.value = '';

    const preview = document.querySelector('.media-preview');
    if (preview) {
      preview.innerHTML = '';
      preview.classList.remove('active');
    }
  },

  highlightHashtags(textarea) {
    // Note: Real hashtag highlighting requires a contenteditable div
    // This is a simplified version - just parse the value
    const value = textarea.value;
    const hashtags = value.match(/#\w+/g) || [];
    // Could display them as chips below
  }
};


/* ============================================================
   INFINITE SCROLL
   ============================================================ */
const InfiniteScroll = {
  page: 2, // Start from page 2 (page 1 already loaded)
  loading: false,
  hasMore: true,

  init() {
    const feed = document.querySelector('.posts-feed');
    if (!feed) return;

    // Observe the last post
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !this.loading && this.hasMore) {
        this.loadMore();
      }
    }, { threshold: 0.5 });

    // Sentinel element at bottom of feed
    const sentinel = document.getElementById('scroll-sentinel');
    if (sentinel) observer.observe(sentinel);
  },

  async loadMore() {
    this.loading = true;
    const sentinel = document.getElementById('scroll-sentinel');
    if (sentinel) sentinel.innerHTML = '<div class="vibe-spinner"></div>';

    try {
      const data = await vibeGet(`/api/posts/?page=${this.page}`);

      if (data.posts && data.posts.length > 0) {
        this.renderPosts(data.posts);
        this.page++;
        this.hasMore = data.has_next;
      } else {
        this.hasMore = false;
      }

      if (sentinel) {
        sentinel.innerHTML = this.hasMore
          ? ''
          : '<p class="text-center text-muted" style="padding:1rem;font-size:.85rem">✨ You\'re all caught up!</p>';
      }
    } catch (err) {
      if (sentinel) sentinel.innerHTML = '<p class="text-center text-muted">Error loading posts</p>';
    }

    this.loading = false;
  },

  renderPosts(posts) {
    const feed = document.querySelector('.posts-feed');
    const sentinel = document.getElementById('scroll-sentinel');

    posts.forEach(post => {
      const html = this.buildPostHTML(post);
      const div = document.createElement('div');
      div.innerHTML = html;
      if (sentinel) {
        feed.insertBefore(div.firstElementChild, sentinel);
      } else {
        feed.appendChild(div.firstElementChild);
      }
    });
  },

  buildPostHTML(post) {
    const mediaHTML = post.image
      ? `<div class="post-media"><img src="${post.image}" alt="Post image" loading="lazy"></div>`
      : post.video
      ? `<div class="post-media"><video src="${post.video}" controls></video></div>`
      : '';

    const likedClass = post.is_liked ? 'liked' : '';

    return `
      <div class="post-card" data-post-id="${post.id}">
        <div class="post-header">
          <a href="/profile/${post.author}/" class="post-author">
            <img src="${post.author_pic}" alt="${post.author}" class="post-author-avatar"
                 onerror="this.src='/static/images/default_avatar.png'">
            <div>
              <span class="post-author-name">${post.author}</span>
              <span class="post-author-handle">@${post.author} · ${post.created_at}</span>
            </div>
          </a>
        </div>
        <div class="post-content">
          <p>${this.parseContent(post.content)}</p>
        </div>
        ${mediaHTML}
        <div class="post-footer">
          <div class="post-reactions">
            <button class="reaction-btn like-btn ${likedClass}" data-post-id="${post.id}">
              <span class="like-icon-svg">${post.is_liked ? '❤️' : '🤍'}</span>
              <span class="like-count">${post.likes_count}</span>
            </button>
            <button class="reaction-btn comment-btn" data-post-id="${post.id}">
              💬 <span class="comment-count">${post.comments_count}</span>
            </button>
            <button class="reaction-btn share-btn" data-post-id="${post.id}" onclick="sharePost(${post.id})">
              🔗
            </button>
          </div>
        </div>
      </div>
    `;
  },

  parseContent(text) {
    // Parse hashtags and mentions
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/#(\w+)/g, '<a href="/hashtag/$1/" class="hashtag-link">#$1</a>')
      .replace(/@(\w+)/g, '<a href="/profile/$1/" class="mention-link">@$1</a>');
  }
};


/* ============================================================
   LIVE NOTIFICATIONS POLLING
   ============================================================ */
const NotificationPoller = {
  interval: null,

  init() {
    if (!document.querySelector('.nav-notif-btn')) return;

    // Poll every 30 seconds for new notifications
    this.poll();
    this.interval = setInterval(() => this.poll(), 30000);
  },

  async poll() {
    try {
      const data = await vibeGet('/api/notifications/count/');
      if (data.count > 0) {
        this.updateBadge(data.count);
      }
    } catch (err) {
      // Silent fail - don't annoy user with errors
    }
  },

  updateBadge(count) {
    const badge = document.querySelector('.notif-badge');
    if (badge) {
      badge.textContent = count > 99 ? '99+' : count;
      badge.style.display = 'flex';
    } else {
      const btn = document.querySelector('.nav-notif-btn');
      if (btn) {
        const b = document.createElement('span');
        b.className = 'notif-badge';
        b.textContent = count;
        btn.style.position = 'relative';
        btn.appendChild(b);
      }
    }
  }
};


/* ============================================================
   DROPDOWN MENUS
   ============================================================ */
const Dropdowns = {
  init() {
    // Toggle dropdown on trigger click
    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('[data-dropdown]');
      if (trigger) {
        e.stopPropagation();
        const menuId = trigger.dataset.dropdown;
        const menu = document.getElementById(menuId);
        if (menu) {
          menu.classList.toggle('open');
          // Close others
          document.querySelectorAll('.dropdown-menu.open').forEach(m => {
            if (m !== menu) m.classList.remove('open');
          });
        }
        return;
      }

      // Click outside closes all
      document.querySelectorAll('.dropdown-menu.open').forEach(m => {
        m.classList.remove('open');
      });
    });
  }
};


/* ============================================================
   MODALS
   ============================================================ */
const Modal = {
  init() {
    // Open modal
    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('[data-modal]');
      if (trigger) {
        const modalId = trigger.dataset.modal;
        this.open(modalId);
      }

      // Close on overlay click
      if (e.target.classList.contains('modal-overlay')) {
        this.closeAll();
      }

      // Close button
      if (e.target.closest('.modal-close')) {
        this.closeAll();
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.closeAll();
    });
  },

  open(id) {
    const overlay = document.getElementById(id);
    if (overlay) overlay.classList.add('open');
  },

  close(id) {
    const overlay = document.getElementById(id);
    if (overlay) overlay.classList.remove('open');
  },

  closeAll() {
    document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
  }
};


/* ============================================================
   IMAGE LIGHTBOX
   ============================================================ */
const Lightbox = {
  init() {
    document.addEventListener('click', (e) => {
      const img = e.target.closest('.post-media img');
      if (img) this.open(img.src);
    });
  },

  open(src) {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position:fixed;inset:0;background:rgba(0,0,0,.9);
      z-index:9999;display:flex;align-items:center;justify-content:center;
      cursor:pointer;animation:fadeIn .2s ease;
    `;
    overlay.innerHTML = `
      <img src="${src}" style="max-width:90vw;max-height:90vh;object-fit:contain;
        border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,.5)">
      <button style="position:absolute;top:1.5rem;right:1.5rem;background:rgba(255,255,255,.15);
        border:none;color:white;font-size:1.5rem;width:44px;height:44px;border-radius:50%;
        cursor:pointer;display:flex;align-items:center;justify-content:center;
        backdrop-filter:blur(8px);">✕</button>
    `;
    overlay.addEventListener('click', () => overlay.remove());
    document.body.appendChild(overlay);
  }
};


/* ============================================================
   MOBILE SIDEBAR TOGGLE
   ============================================================ */
function initMobileSidebar() {
  const menuBtn = document.getElementById('mobile-menu-btn');
  const sidebar = document.querySelector('.vibe-sidebar-left');
  const overlay = document.getElementById('sidebar-overlay');

  if (!menuBtn || !sidebar) return;

  menuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('mobile-open');
    if (overlay) overlay.classList.toggle('active');
  });

  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('mobile-open');
      overlay.classList.remove('active');
    });
  }
}


/* ============================================================
   SHARE POST
   ============================================================ */
function sharePost(postId) {
  const url = `${window.location.origin}/posts/${postId}/`;

  if (navigator.share) {
    navigator.share({
      title: 'Check out this VIBE post!',
      url: url
    }).catch(() => {});
  } else {
    // Fallback: copy to clipboard
    navigator.clipboard.writeText(url).then(() => {
      Toast.show('🔗 Link copied to clipboard!', 'success');
    }).catch(() => {
      Toast.show('Could not copy link', 'error');
    });
  }
}


/* ============================================================
   REPORT MODAL
   ============================================================ */
function initReportButtons() {
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-report-post]');
    if (!btn) return;

    const postId = btn.dataset.reportPost;
    const type = document.querySelector('[name="report_type"]')?.value || 'spam';
    const desc = document.querySelector('[name="report_description"]')?.value || '';

    try {
      const formData = new FormData();
      formData.append('report_type', type);
      formData.append('description', desc);
      formData.append('csrfmiddlewaretoken', getCsrfToken());

      const res = await fetch(`/posts/${postId}/report/`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      });
      const data = await res.json();

      if (data.success) {
        Toast.show('✅ Report submitted. Thanks for keeping VIBE safe!', 'success');
        Modal.closeAll();
      }
    } catch (err) {
      Toast.show('Failed to submit report', 'error');
    }
  });
}


/* ============================================================
   PROFILE PICTURE PREVIEW
   ============================================================ */
function initProfilePicPreview() {
  const inputs = document.querySelectorAll('input[type="file"][accept="image/*"]');

  inputs.forEach(input => {
    input.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const previewId = input.dataset.preview;
      const preview = document.getElementById(previewId);

      if (preview) {
        preview.src = URL.createObjectURL(file);
        preview.style.animation = 'heartPop .4s ease';
      }
    });
  });
}


/* ============================================================
   SEARCH AUTOCOMPLETE (simple)
   ============================================================ */
function initSearchAutocomplete() {
  const searchInput = document.querySelector('.navbar-search input');
  if (!searchInput) return;

  let timeout;

  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const q = searchInput.value.trim();
      if (q) window.location.href = `/explore/?q=${encodeURIComponent(q)}`;
    }
  });
}


/* ============================================================
   SKELETON LOADING - show skeleton on page load
   ============================================================ */
function initSkeletons() {
  const feed = document.querySelector('.posts-feed');
  if (!feed || feed.children.length > 0) return;

  // Already handled by server-side rendering
}


/* ============================================================
   POST TABS (on profile page)
   ============================================================ */
function initProfileTabs() {
  const tabs = document.querySelectorAll('.profile-tab');
  const panes = document.querySelectorAll('.tab-pane');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;

      tabs.forEach(t => t.classList.remove('active'));
      panes.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      const pane = document.getElementById(`tab-${target}`);
      if (pane) pane.classList.add('active');
    });
  });
}


/* ============================================================
   AUTO-LINK HASHTAGS AND MENTIONS IN POST CONTENT
   ============================================================ */
function parsePostContent() {
  document.querySelectorAll('.post-content p, .post-content').forEach(el => {
    if (el.dataset.parsed) return;
    el.dataset.parsed = 'true';

    let html = el.innerHTML;
    // Hashtags → links
    html = html.replace(/#(\w+)/g, '<a href="/hashtag/$1/" class="hashtag-link">#$1</a>');
    // Mentions → links
    html = html.replace(/@(\w+)/g, '<a href="/profile/$1/" class="mention-link">@$1</a>');
    el.innerHTML = html;
  });
}


/* ============================================================
   ANIMATE STATS NUMBERS (count up effect)
   ============================================================ */
function animateNumbers() {
  document.querySelectorAll('.profile-stat-num, .admin-stat-num').forEach(el => {
    const target = parseInt(el.textContent.replace(/,/g, ''), 10);
    if (isNaN(target) || target === 0) return;

    let current = 0;
    const duration = 1200;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
      current = Math.min(current + increment, target);
      el.textContent = Math.floor(current).toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 16);
  });
}


/* ============================================================
   INITIALIZE EVERYTHING on DOM ready
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  // Core systems
  ThemeManager.init();
  Toast.init();
  LikeSystem.init();
  CommentSystem.init();
  FollowSystem.init();
  InfiniteScroll.init();
  NotificationPoller.init();
  Dropdowns.init();
  Modal.init();
  Lightbox.init();
  PostCreator.init();

  // Page-specific
  initMobileSidebar();
  initReportButtons();
  initProfilePicPreview();
  initSearchAutocomplete();
  initProfileTabs();
  parsePostContent();
  animateNumbers();

  // Log environment
  console.log('%cVIBE 🎉', 'font-size:24px;font-weight:bold;background:linear-gradient(135deg,#7C3AED,#EC4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent');
  console.log('%cSocial Media Platform — Built with Django + Vanilla JS', 'color:#7C3AED');
});


// Re-parse content after infinite scroll adds posts
document.addEventListener('postsLoaded', parsePostContent);
