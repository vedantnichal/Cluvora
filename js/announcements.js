
let allAnnouncements = [];
let currentCategory = 'all';
let searchQuery = '';

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatTimeAgo(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr.endsWith('Z') ? dateStr : dateStr + 'Z');
  const now = new Date();
  const diffSec = Math.floor((now - date) / 1000);

  if (isNaN(diffSec) || diffSec < 0) return 'Just now';
  if (diffSec < 60) return 'Just now';
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  if (diffSec < 604800) return `${Math.floor(diffSec / 86400)}d ago`;

  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function showToast(message, type = 'success') {
  const toast = document.getElementById('toast-msg');
  if (!toast) return;

  toast.textContent = message;
  toast.className = `toast-msg show ${type}`;

  setTimeout(() => {
    toast.className = 'toast-msg';
  }, 3500);
}

async function loadAnnouncements() {
  const container = document.getElementById('announcements-feed');
  if (!container) return;

  try {
    const res = await fetch('/api/announcements');
    if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);

    const data = await res.json();
    allAnnouncements = data.announcements || [];

    updateStats();
    renderAnnouncements();
  } catch (err) {
    console.error('Error fetching announcements:', err);
    container.innerHTML = `
      <div class="empty-feed">
        <h3>Could not load announcements</h3>
        <p>There was an error connecting to the server database. Please ensure the Flask backend is running.</p>
        <button class="btn-secondary" onclick="loadAnnouncements()">Try Again</button>
      </div>
    `;
  }
}

function updateStats() {
  const countEl = document.getElementById('stat-total-count');
  const clubsCountEl = document.getElementById('stat-clubs-count');
  const feedCountEl = document.getElementById('feed-count-display');

  const total = allAnnouncements.length;
  const uniqueClubs = new Set(allAnnouncements.map(a => a.club_name.toLowerCase().trim())).size;

  if (countEl) countEl.textContent = total;
  if (clubsCountEl) clubsCountEl.textContent = uniqueClubs;
  if (feedCountEl) feedCountEl.textContent = `${total} announcement${total === 1 ? '' : 's'}`;
}

function renderAnnouncements() {
  const container = document.getElementById('announcements-feed');
  if (!container) return;

  let filtered = allAnnouncements;

  if (currentCategory !== 'all') {
    filtered = filtered.filter(a => (a.category || '').toLowerCase() === currentCategory.toLowerCase());
  }

  if (searchQuery) {
    const q = searchQuery.toLowerCase().trim();
    filtered = filtered.filter(a =>
      (a.title || '').toLowerCase().includes(q) ||
      (a.content || '').toLowerCase().includes(q) ||
      (a.club_name || '').toLowerCase().includes(q) ||
      (a.category || '').toLowerCase().includes(q)
    );
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-feed">
        <span style="font-size: 2.2rem; display: block; margin-bottom: 8px;">📢</span>
        <h3>No announcements found</h3>
        <p>${searchQuery || currentCategory !== 'all'
          ? 'No announcements match your search or filter criteria. Try clearing your filters or search terms.'
          : 'No announcements have been posted yet. Be the first club to share an update!'}</p>
        <button class="post-btn-cta" onclick="openPostModal()">+ Post New Announcement</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(item => {
    const isPinned = Boolean(item.is_pinned);
    const catClass = escapeHtml(item.category || 'General');
    const avatarLetter = (item.club_name || 'C').charAt(0).toUpperCase();

    const linkHtml = item.link
      ? `<a href="${escapeHtml(item.link)}" target="_blank" rel="noopener noreferrer" class="card-link-btn">
           Learn More / Register <span>↗</span>
         </a>`
      : '';

    const dateHtml = item.event_date
      ? `<span class="detail-pill">📅 <strong>Event / Deadline:</strong> ${escapeHtml(item.event_date)}</span>`
      : '';

    const authorHtml = item.author_name
      ? `<span class="detail-pill">👤 <strong>By:</strong> ${escapeHtml(item.author_name)}</span>`
      : '';

    return `
      <article class="announcement-card ${isPinned ? 'is-pinned' : ''}" data-id="${item.id}">
        <div class="card-top">
          <div class="club-meta">
            <div class="club-avatar">${avatarLetter}</div>
            <div class="club-title-group">
              <span class="club-name">${escapeHtml(item.club_name)}</span>
              <span class="post-time">${formatTimeAgo(item.created_at)}</span>
            </div>
          </div>

          <div class="badges-group">
            ${isPinned ? `<span class="pinned-badge">📌 Pinned</span>` : ''}
            <span class="cat-badge ${catClass}">${escapeHtml(item.category || 'General')}</span>
          </div>
        </div>

        <h3 class="announcement-title">${escapeHtml(item.title)}</h3>
        <p class="announcement-desc">${escapeHtml(item.content)}</p>

        ${(dateHtml || authorHtml) ? `<div class="card-details-pills">${dateHtml}${authorHtml}</div>` : ''}

        <div class="card-footer">
          ${linkHtml}
          <div class="card-actions-right">
            <button class="delete-card-btn" title="Delete announcement" onclick="handleDeleteAnnouncement(${item.id})">
              🗑️
            </button>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

function openPostModal() {
  const modal = document.getElementById('announcement-modal');
  const feedback = document.getElementById('form-feedback');
  if (feedback) feedback.style.display = 'none';
  if (modal) {
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    const firstInput = document.getElementById('club-select');
    if (firstInput) firstInput.focus();
  }
}

function closePostModal() {
  const modal = document.getElementById('announcement-modal');
  if (modal) {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
  }
}

async function handleAnnouncementSubmit(e) {
  e.preventDefault();
  const form = document.getElementById('post-announcement-form');
  const submitBtn = document.getElementById('submit-announcement-btn');
  const feedback = document.getElementById('form-feedback');

  const clubSelect = document.getElementById('club-select').value;
  const customClub = document.getElementById('custom-club').value.trim();
  const clubName = customClub || clubSelect;

  const title = document.getElementById('announcement-title-input').value.trim();
  const category = document.getElementById('announcement-category-select').value;
  const content = document.getElementById('announcement-content-input').value.trim();
  const eventDate = document.getElementById('announcement-date-input').value.trim();
  const link = document.getElementById('announcement-link-input').value.trim();
  const authorName = document.getElementById('announcement-author-input').value.trim();
  const isPinned = document.getElementById('announcement-pinned-check').checked ? 1 : 0;

  if (!clubName || !title || !content) {
    feedback.textContent = 'Please fill out all required fields (Club name, Title, and Details).';
    feedback.className = 'form-feedback error';
    feedback.style.display = 'block';
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Publishing...';
  feedback.style.display = 'none';

  try {
    const response = await fetch('/api/announcements', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        club_name: clubName,
        title: title,
        category: category,
        content: content,
        event_date: eventDate,
        link: link,
        author_name: authorName,
        is_pinned: isPinned
      })
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(result.error || 'Failed to post announcement.');
    }

    form.reset();
    closePostModal();
    showToast('🎉 Announcement published successfully!', 'success');
    await loadAnnouncements();

  } catch (err) {
    console.error('Submission error:', err);
    feedback.textContent = err.message || 'Error creating announcement. Please try again.';
    feedback.className = 'form-feedback error';
    feedback.style.display = 'block';
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Publish Announcement';
  }
}

async function handleDeleteAnnouncement(id) {
  if (!confirm('Are you sure you want to remove this announcement?')) return;

  try {
    const res = await fetch(`/api/announcements/${id}`, {
      method: 'DELETE'
    });
    const result = await res.json();
    if (!res.ok || !result.success) {
      throw new Error(result.error || 'Failed to delete announcement.');
    }

    showToast('Announcement removed.', 'success');
    await loadAnnouncements();
  } catch (err) {
    console.error('Delete error:', err);
    showToast('Failed to delete announcement.', 'error');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadAnnouncements();

  const searchInput = document.getElementById('announcements-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value;
      renderAnnouncements();
    });
  }

  const pills = document.querySelectorAll('.category-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentCategory = pill.getAttribute('data-category') || 'all';
      renderAnnouncements();
    });
  });

  const openBtns = document.querySelectorAll('[data-open-modal]');
  openBtns.forEach(btn => btn.addEventListener('click', openPostModal));

  const closeBtns = document.querySelectorAll('[data-close-modal]');
  closeBtns.forEach(btn => btn.addEventListener('click', closePostModal));

  const modal = document.getElementById('announcement-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closePostModal();
    });
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && modal.classList.contains('is-open')) {
      closePostModal();
    }
  });

  const form = document.getElementById('post-announcement-form');
  if (form) {
    form.addEventListener('submit', handleAnnouncementSubmit);
  }

  const clubSelect = document.getElementById('club-select');
  const customClubWrap = document.getElementById('custom-club-wrap');
  if (clubSelect && customClubWrap) {
    clubSelect.addEventListener('change', () => {
      if (clubSelect.value === 'custom') {
        customClubWrap.style.display = 'block';
        document.getElementById('custom-club').focus();
      } else {
        customClubWrap.style.display = 'none';
        document.getElementById('custom-club').value = '';
      }
    });
  }
});

