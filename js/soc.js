let societies = [];

async function render_soc_page() {
  const container = document.getElementById('soc-teams-list');
  if (!container) return;

  try {
    const { all_clubs } = await get_CoSA_data();

    societies = all_clubs.filter(club => {
      const isWelfare = club.category === "Welfare & Governance" || club.parent_council === "Student Welfare and Governance";
      const isSports = club.category === "Sports" || club.parent_council === "Sports Council";

      return isWelfare || isSports;
    });

    render_cards(societies);
    search_filter();

  } catch (error) {
    console.error("Failed to load societies data:", error);
    container.innerHTML = `
      <div class="loading-state error-state">
        <p style="color: var(--primary); font-weight: 700;">Failed to fetch societies data</p>
        <p style="font-size: 0.9rem; margin-top: 8px;">If testing locally via file://, run a local server: <code>python3 -m http.server 8000</code></p>
      </div>
    `;
  }
}

function render_cards(clubs_2_render) {
  const container = document.getElementById('soc-teams-list');
  if (!container) return;

  if (clubs_2_render.length === 0) {
    container.innerHTML = `
      <div class="loading-state empty-state">
        <h3>No societies found matching your search.</h3>
        <p>Try searching for keywords like "Mentorship", "Sports", "NSS", "Hostel", or "Academics".</p>
      </div>
    `;
    return;
  }

  container.innerHTML = clubs_2_render.map(club => {
    const tagsList = club.tags || [club.category || "Societies & Campus Life"];
    const tagsHTML = tagsList.map(tag => `<li><small>${escape_html(tag)}</small></li>`).join('');

    const flagshipHTML = (club.flagship_events && club.flagship_events.length > 0)
      ? `<p><strong>Flagship Initiatives:</strong> ${escape_html(club.flagship_events.join(', '))}</p>`
      : '';

    const achievementsHTML = (club.achievements && club.achievements.length > 0)
      ? `<p><strong>Recent Honour:</strong> ${escape_html(club.achievements.join(', '))}</p>`
      : '';

    const links = [];
    const webUrl = club.social_links?.website || club.source_url;
    if (webUrl) {
      links.push(`<a href="${webUrl}" target="_blank" rel="noopener noreferrer">Official Portal &rarr;</a>`);
    }
    if (club.social_links?.github) {
      links.push(`<a href="${club.social_links.github}" target="_blank" rel="noopener noreferrer">GitHub</a>`);
    }
    if (club.social_links?.linkedin) {
      links.push(`<a href="${club.social_links.linkedin}" target="_blank" rel="noopener noreferrer">LinkedIn</a>`);
    }
    if (club.social_links?.instagram) {
      links.push(`<a href="${club.social_links.instagram}" target="_blank" rel="noopener noreferrer">Instagram</a>`);
    }
    if (club.leads?.[0]?.email) {
      links.push(`<a href="mailto:${club.leads[0].email}">${escape_html(club.leads[0].email)}</a>`);
    }

    const rawLogo = club.logo_url || '/assets/logos/cosa-crest.svg';
    const logoPath = rawLogo.startsWith('.') ? rawLogo : `./..${rawLogo}`;

    return `
      <article class="club-card" id="${escape_html(club.club_id || '')}">
        <header class="club-header">
          <a class="club-logo" href="${webUrl || '#'}" target="_blank" rel="noopener noreferrer">
            <img src="${logoPath}" alt="${escape_html(club.name)} Logo" width="64" height="64" style="width: 64px; height: 64px; object-fit: contain;" onerror="this.onerror=null;this.src='./../assets/logos/cosa-crest.svg';">
          </a>
          <div>
            <h2 class="club-title">${escape_html(club.name)}</h2>
            ${club.tagline ? `<p class="club-tagline"><em>${escape_html(club.tagline)}</em></p>` : ''}
          </div>
        </header>

        <p class="club-desc">${escape_html(club.description || '')}</p>

        ${achievementsHTML}

        <ul class="club-tags" aria-label="Tags">
          ${tagsHTML}
        </ul>

        ${flagshipHTML}

        <nav class="club-links" aria-label="${escape_html(club.name)} links">
          ${links.length > 0 ? links.join(' | ') : '<a href="./../Contact Us/contact_us.html">Contact via CoSA</a>'}
        </nav>
      </article>
    `;
  }).join('');
}

function search_filter() {
  const main = document.querySelector('main');
  const container = document.getElementById('soc-teams-list');
  if (!main || !container || document.getElementById('club-search-input')) return;

  const searchWrapper = document.createElement('div');
  searchWrapper.id = 'search-filter-wrapper';
  searchWrapper.className = 'search-wrapper wrap';
  searchWrapper.innerHTML = `
    <div>
      <input type="text" id="club-search-input" class="search-input" placeholder="🔍 Search societies by name, keywords, or domain..." />
    </div>
  `;
  main.insertBefore(searchWrapper, container);

  const searchInput = document.getElementById('club-search-input');
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
      render_cards(societies);
      return;
    }

    const filtered = societies.filter(club => {
      const matchName = (club.name || '').toLowerCase().includes(query);
      const matchDesc = (club.description || '').toLowerCase().includes(query);
      const matchTagline = (club.tagline || '').toLowerCase().includes(query);
      const matchTags = (club.tags || []).some(tag => tag.toLowerCase().includes(query));
      return matchName || matchDesc || matchTagline || matchTags;
    });

    render_cards(filtered);
  });
}

document.addEventListener('DOMContentLoaded', render_soc_page);
