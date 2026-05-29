/**
 * VIBE - Extra JavaScript
 * ========================
 * Advanced features:
 * - Emoji picker
 * - Story bar interactions
 * - Real-time character count
 * - Keyboard shortcuts
 * - Copy-to-clipboard
 * - Scroll to top button
 * - Progressive image loading
 * - Post preview before submit
 */

/* ============================================================
   EMOJI PICKER
   ============================================================ */
const EmojiPicker = {
  emojis: ['😀','😂','😍','🤩','😎','🥳','🎉','🔥','❤️','💜',
           '✨','🚀','💯','🎯','👏','💪','🙏','😅','🤔','😴',
           '🌈','🎵','🎨','📸','🍕','☕','🌸','🦋','⭐','🌟'],

  init() {
    this.picker = document.createElement('div');
    this.picker.className = 'emoji-picker-popup';
    this.picker.style.cssText = `
      position:fixed; background:var(--bg-card); border:1px solid var(--border-color);
      border-radius:var(--radius-xl); padding:.875rem; display:none;
      grid-template-columns:repeat(10, 1fr); gap:.25rem;
      box-shadow:var(--shadow-lg); backdrop-filter:blur(16px);
      z-index:10000; max-width:320px;
    `;
    this.emojis.forEach(emoji => {
      const btn = document.createElement('button');
      btn.textContent = emoji;
      btn.type = 'button';
      btn.style.cssText = `
        width:30px; height:30px; border:none; background:none;
        font-size:1.1rem; cursor:pointer; border-radius:6px;
        transition:.15s; display:flex; align-items:center; justify-content:center;
      `;
      btn.addEventListener('mouseover', () => btn.style.transform = 'scale(1.3)');
      btn.addEventListener('mouseout',  () => btn.style.transform = '');
      btn.addEventListener('click', () => this.insert(emoji));
      this.picker.appendChild(btn);
    });
    document.body.appendChild(this.picker);

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.emoji-btn') && !e.target.closest('.emoji-picker-popup')) {
        this.hide();
      }
    });
  },

  show(triggerEl) {
    const rect = triggerEl.getBoundingClientRect();
    this.picker.style.display = 'grid';
    this.picker.style.top = (rect.top - this.picker.offsetHeight - 8) + 'px';
    this.picker.style.left = rect.left + 'px';

    // Store active textarea
    this.activeInput = document.querySelector('#create-post-form .post-textarea') ||
                       document.querySelector('.post-textarea') ||
                       document.querySelector('.comment-input');
  },

  hide() {
    if (this.picker) this.picker.style.display = 'none';
  },

  toggle(triggerEl) {
    if (this.picker.style.display === 'grid') this.hide();
    else this.show(triggerEl);
  },

  insert(emoji) {
    const input = this.activeInput;
    if (input) {
      const start = input.selectionStart;
      const end = input.selectionEnd;
      const val = input.value;
      input.value = val.substring(0, start) + emoji + val.substring(end);
      input.selectionStart = input.selectionEnd = start + emoji.length;
      input.focus();
      input.dispatchEvent(new Event('input'));
    }
    this.hide();
  }
};

// Init emoji picker after DOM
document.addEventListener('DOMContentLoaded', () => {
  EmojiPicker.init();

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.emoji-btn');
    if (btn) {
      e.stopPropagation();
      EmojiPicker.toggle(btn);
    }
  });
});


/* ============================================================
   SCROLL TO TOP BUTTON
   ============================================================ */
const ScrollTop = {
  btn: null,

  init() {
    this.btn = document.createElement('button');
    this.btn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    this.btn.style.cssText = `
      position:fixed; bottom:5rem; right:1.25rem; width:44px; height:44px;
      border-radius:50%; background:var(--gradient-main); color:white;
      border:none; cursor:pointer; box-shadow:0 4px 16px rgba(124,58,237,.4);
      display:flex; align-items:center; justify-content:center; font-size:.9rem;
      opacity:0; pointer-events:none; transition:all .3s cubic-bezier(.34,1.56,.64,1);
      z-index:199;
    `;
    this.btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    document.body.appendChild(this.btn);

    window.addEventListener('scroll', () => {
      if (window.scrollY > 500) {
        this.btn.style.opacity = '1';
        this.btn.style.pointerEvents = 'auto';
        this.btn.style.transform = 'scale(1)';
      } else {
        this.btn.style.opacity = '0';
        this.btn.style.pointerEvents = 'none';
        this.btn.style.transform = 'scale(0.8)';
      }
    }, { passive: true });
  }
};

document.addEventListener('DOMContentLoaded', () => ScrollTop.init());


/* ============================================================
   KEYBOARD SHORTCUTS
   ============================================================ */
document.addEventListener('keydown', (e) => {
  // Only when not typing in input
  const tag = document.activeElement.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

  switch(e.key) {
    case '/': // Focus search
      e.preventDefault();
      document.querySelector('.navbar-search input')?.focus();
      break;
    case 'n': // New post
      if (!e.ctrlKey && !e.metaKey) {
        const modal = document.getElementById('create-post-modal');
        if (modal) modal.classList.add('open');
      }
      break;
    case 'Escape': // Close modals
      document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
      document.querySelectorAll('.dropdown-menu.open').forEach(m => m.classList.remove('open'));
      break;
    case 'g':
      // g+h = go home; g+e = go explore; g+n = go notifications
      if (!e.ctrlKey) {
        // Simple single-key shortcuts
      }
      break;
  }
});


/* ============================================================
   PROGRESSIVE IMAGE LOADING (blur-up)
   ============================================================ */
const LazyImages = {
  init() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.style.transition = 'filter .4s ease, opacity .4s ease';
          img.style.filter = 'blur(8px)';
          img.style.opacity = '0.7';

          const loader = new Image();
          loader.src = img.src;
          loader.onload = () => {
            img.style.filter = 'blur(0)';
            img.style.opacity = '1';
          };

          observer.unobserve(img);
        }
      });
    }, { rootMargin: '100px' });

    images.forEach(img => observer.observe(img));
  }
};

document.addEventListener('DOMContentLoaded', () => LazyImages.init());


/* ============================================================
   REAL-TIME POST FORM VALIDATION
   ============================================================ */
const PostFormValidator = {
  init() {
    const form = document.getElementById('create-post-form');
    if (!form) return;

    const textarea = form.querySelector('textarea');
    const submitBtn = form.querySelector('[type="submit"]');
    const counter = form.querySelector('.char-counter');

    if (!textarea || !submitBtn) return;

    textarea.addEventListener('input', () => {
      const len = textarea.value.trim().length;
      const maxLen = 2000;
      const hasMedia = form.querySelector('#image-upload')?.files?.length > 0 ||
                       form.querySelector('#video-upload')?.files?.length > 0;

      // Update counter
      if (counter) {
        counter.textContent = `${textarea.value.length}/${maxLen}`;
        counter.className = 'char-counter' +
          (textarea.value.length > 1800 ? ' danger' :
           textarea.value.length > 1500 ? ' warning' : '');
      }

      // Enable/disable submit based on content
      const hasContent = len > 0 || hasMedia;
      submitBtn.disabled = !hasContent || len > maxLen;
      submitBtn.style.opacity = submitBtn.disabled ? '0.6' : '1';
    });

    // Also check on file input change
    form.querySelectorAll('input[type="file"]').forEach(input => {
      input.addEventListener('change', () => textarea.dispatchEvent(new Event('input')));
    });
  }
};

document.addEventListener('DOMContentLoaded', () => PostFormValidator.init());


/* ============================================================
   MENTION AUTOCOMPLETE (basic)
   ============================================================ */
const MentionAutocomplete = {
  init() {
    document.querySelectorAll('.post-textarea, textarea[name="content"]').forEach(el => {
      el.addEventListener('input', (e) => this.check(e, el));
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') this.hideDropdown();
      });
    });
  },

  check(e, el) {
    const val = el.value;
    const pos = el.selectionStart;
    // Find @word before cursor
    const before = val.substring(0, pos);
    const match = before.match(/@(\w*)$/);

    if (match && match[1].length >= 2) {
      this.fetchSuggestions(match[1], el);
    } else {
      this.hideDropdown();
    }
  },

  async fetchSuggestions(query, el) {
    try {
      const res = await fetch(`/explore/?q=${query}&type=users`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      // In a full implementation, we'd parse results and show dropdown
      // For now, this is a placeholder for the feature
    } catch (err) { /* silent fail */ }
  },

  hideDropdown() {
    document.getElementById('mention-dropdown')?.remove();
  }
};

document.addEventListener('DOMContentLoaded', () => MentionAutocomplete.init());


/* ============================================================
   COPY CODE BLOCKS
   ============================================================ */
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-copy]');
  if (!btn) return;

  const text = btn.dataset.copy;
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = '✅ Copied!';
    setTimeout(() => btn.innerHTML = orig, 2000);
  });
});


/* ============================================================
   POST FORM SUBMIT via AJAX (enhanced)
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('create-post-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('[type="submit"]');
    const origText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="dots-loader"><span></span><span></span><span></span></span>';
    submitBtn.disabled = true;

    try {
      const formData = new FormData(form);
      const res = await fetch(form.action || '/posts/create/', {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      });
      const data = await res.json();

      if (data.success) {
        // Close modal
        document.getElementById('create-post-modal')?.classList.remove('open');
        Toast.show('🚀 Post published!', 'success');

        // Reset form
        form.reset();
        const preview = form.querySelector('.media-preview');
        if (preview) { preview.innerHTML = ''; preview.classList.remove('active'); }

        // Reload feed to show new post
        setTimeout(() => window.location.reload(), 800);
      } else {
        const errors = Object.values(data.errors || {}).flat().join(', ');
        Toast.show(errors || 'Could not publish post', 'error');
      }
    } catch (err) {
      Toast.show('Network error. Please try again.', 'error');
    }

    submitBtn.innerHTML = origText;
    submitBtn.disabled = false;
  });
});


/* ============================================================
   STORY BAR (UI only — backend can be extended)
   ============================================================ */
const StoryBar = {
  init() {
    const bar = document.querySelector('.story-bar');
    if (!bar) return;

    bar.querySelectorAll('.story-item').forEach(item => {
      item.addEventListener('click', () => {
        const ring = item.querySelector('.story-ring');
        if (ring) ring.classList.add('seen');
        Toast.show('📸 Stories coming soon!', 'info');
      });
    });
  }
};

document.addEventListener('DOMContentLoaded', () => StoryBar.init());


/* ============================================================
   SWIPE GESTURES (mobile)
   ============================================================ */
const SwipeGestures = {
  startX: 0,
  startY: 0,

  init() {
    document.addEventListener('touchstart', (e) => {
      this.startX = e.touches[0].clientX;
      this.startY = e.touches[0].clientY;
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - this.startX;
      const dy = e.changedTouches[0].clientY - this.startY;

      // Only horizontal swipes > 80px
      if (Math.abs(dx) > 80 && Math.abs(dy) < 40) {
        if (dx > 0) this.onSwipeRight();
        else this.onSwipeLeft();
      }
    }, { passive: true });
  },

  onSwipeRight() {
    // Open sidebar on swipe right from left edge
    const sidebar = document.querySelector('.vibe-sidebar-left');
    const overlay = document.getElementById('sidebar-overlay');
    if (this.startX < 30 && sidebar) {
      sidebar.classList.add('mobile-open');
      if (overlay) { overlay.style.display = 'block'; overlay.classList.add('active'); }
    }
  },

  onSwipeLeft() {
    // Close sidebar on swipe left
    const sidebar = document.querySelector('.vibe-sidebar-left');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar?.classList.contains('mobile-open')) {
      sidebar.classList.remove('mobile-open');
      if (overlay) overlay.classList.remove('active');
    }
  }
};

document.addEventListener('DOMContentLoaded', () => SwipeGestures.init());


/* ============================================================
   ONLINE STATUS INDICATOR (demo)
   ============================================================ */
const OnlineStatus = {
  init() {
    window.addEventListener('online',  () => Toast.show('🟢 Back online!', 'success'));
    window.addEventListener('offline', () => Toast.show('🔴 You are offline', 'error'));
  }
};

document.addEventListener('DOMContentLoaded', () => OnlineStatus.init());


/* ============================================================
   CONFETTI on first post! (fun easter egg)
   ============================================================ */
function launchConfetti() {
  const colors = ['#7C3AED', '#EC4899', '#F97316', '#06B6D4', '#10B981'];
  for (let i = 0; i < 60; i++) {
    const piece = document.createElement('div');
    piece.style.cssText = `
      position:fixed; top:-10px;
      left:${Math.random() * 100}%;
      width:${Math.random() * 8 + 4}px;
      height:${Math.random() * 8 + 4}px;
      background:${colors[Math.floor(Math.random() * colors.length)]};
      border-radius:${Math.random() > 0.5 ? '50%' : '2px'};
      opacity:1; z-index:99999;
      animation: confettiFall ${Math.random() * 2 + 1.5}s ease-out forwards;
      animation-delay:${Math.random() * 0.5}s;
    `;
    document.body.appendChild(piece);
    setTimeout(() => piece.remove(), 3500);
  }
}

// Add confetti keyframe to page
const style = document.createElement('style');
style.textContent = `
  @keyframes confettiFall {
    0%   { transform: translateY(-10px) rotate(0deg); opacity:1; }
    100% { transform: translateY(100vh) rotate(${Math.random() * 720}deg); opacity:0; }
  }
`;
document.head.appendChild(style);


/* ============================================================
   TYPED.JS EFFECT for hero text (auth pages)
   ============================================================ */
const TypedEffect = {
  init() {
    const el = document.querySelector('.typed-text');
    if (!el) return;

    const phrases = ['share your story', 'find your tribe', 'spark conversations', 'feel the vibe'];
    let phraseIdx = 0;
    let charIdx = 0;
    let isDeleting = false;

    const type = () => {
      const current = phrases[phraseIdx];
      if (isDeleting) {
        el.textContent = current.substring(0, charIdx--);
        if (charIdx < 0) {
          isDeleting = false;
          phraseIdx = (phraseIdx + 1) % phrases.length;
          charIdx = 0;
          setTimeout(type, 500);
          return;
        }
      } else {
        el.textContent = current.substring(0, charIdx++);
        if (charIdx > current.length) {
          isDeleting = true;
          setTimeout(type, 1800);
          return;
        }
      }
      setTimeout(type, isDeleting ? 60 : 100);
    };

    type();
  }
};

document.addEventListener('DOMContentLoaded', () => TypedEffect.init());


/* ============================================================
   UPDATE NAVBAR SCROLL EFFECT
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  const navbar = document.querySelector('.vibe-navbar');
  if (!navbar) return;

  let lastY = 0;
  window.addEventListener('scroll', () => {
    const currentY = window.scrollY;

    if (currentY > 100) {
      navbar.style.boxShadow = 'var(--shadow-md)';
    } else {
      navbar.style.boxShadow = 'var(--shadow-sm)';
    }

    // Hide navbar on scroll down (mobile) / show on scroll up
    if (window.innerWidth <= 768) {
      if (currentY > lastY && currentY > 200) {
        navbar.style.transform = 'translateY(-100%)';
      } else {
        navbar.style.transform = 'translateY(0)';
      }
    }

    lastY = currentY;
  }, { passive: true });

  navbar.style.transition = 'transform .3s ease, box-shadow .3s ease';
});
