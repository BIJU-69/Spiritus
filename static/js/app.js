/* ── SPIRITUS — Frontend Application ────────────────────────────────────── */

const API = {
  get: (url) => fetch(url).then(r => r.json()),
  post: (url, body) => fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(r => r.json()),
};

/* ── State ───────────────────────────────────────────────────────────────── */
const state = {
  currentSection: 'hero',
  filters: { type: '', quality_tier: '', min_abv: '', max_abv: '', sort: 'name' },
  cocktailFilters: { base_spirit: '', mood: '', difficulty: '' },
  recommend: { mood: '', strength: '', flavors: [] },
  compareIds: [],
  filterOptions: {},
  searchDebounceTimer: null,
};

/* ── Type Icons ──────────────────────────────────────────────────────────── */
const TYPE_ICONS = {
  whiskey: '🥃', vodka: '🍸', rum: '🍹', gin: '🌿',
  tequila: '🌵', wine: '🍷', beer: '🍺', champagne: '🥂',
  brandy: '🫙', liqueur: '🍫', mezcal: '🌑',
};

const TIER_LABELS = {
  budget: 'Budget', 'mid-range': 'Mid-Range',
  premium: 'Premium', 'ultra-premium': 'Ultra-Premium',
};

/* ── Navigation ──────────────────────────────────────────────────────────── */
function navigate(target) {
  document.querySelectorAll('.section').forEach(s => {
    s.classList.add('hidden');
    s.classList.remove('active');
  });

  const el = document.getElementById(`section-${target}`);
  if (!el) return;
  el.classList.remove('hidden');
  el.classList.add('active');
  el.style.display = 'block';

  state.currentSection = target;
  window.scrollTo({ top: 0, behavior: 'smooth' });

  document.querySelectorAll('.nav-link').forEach(l => {
    l.classList.toggle('active', l.dataset.nav === target);
  });

  if (target === 'explore') loadExplore();
  if (target === 'cocktails') loadCocktails();
  if (target === 'compare') initCompare();
}

/* ── Toast ────────────────────────────────────────────────────────────────── */
function toast(msg, duration = 3000) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.add('hidden'), duration);
}

/* ── Helpers ──────────────────────────────────────────────────────────────── */
function capitalize(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
}

function tierBadge(tier) {
  const cls = `tier-${tier}`.replace(/ /g, '-');
  return `<span class="bev-tier-badge ${cls}">${TIER_LABELS[tier] || tier}</span>`;
}

function flavorTagsHTML(topFlavors) {
  return topFlavors.map(f => `<span class="flavor-tag">${f}</span>`).join('');
}

function bevCardHTML(bev) {
  const icon = TYPE_ICONS[bev.type] || '🍶';
  return `
    <div class="bev-card" data-id="${bev.id}" onclick="openBeverageModal(${bev.id})">
      <div class="bev-card-header">
        <span class="bev-type-icon">${icon}</span>
        ${tierBadge(bev.quality_tier)}
      </div>
      <div class="bev-name">${bev.name}</div>
      <div class="bev-brand">${bev.brand} · ${bev.country}</div>
      <div class="bev-meta">
        <span class="bev-meta-tag bev-abv-tag">${bev.abv}% ABV</span>
        <span class="bev-meta-tag">${capitalize(bev.type)}</span>
        ${bev.subtype ? `<span class="bev-meta-tag">${bev.subtype}</span>` : ''}
      </div>
      <div class="flavor-tags">${flavorTagsHTML(bev.top_flavors || [])}</div>
      <div class="bev-footer">
        <span class="bev-price">${bev.price_label || '—'}</span>
        <span class="bev-country">${bev.country}</span>
      </div>
    </div>`;
}

/* ── EXPLORE ──────────────────────────────────────────────────────────────── */
async function loadExplore(overrides = {}) {
  const grid = document.getElementById('explore-grid');
  grid.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading spirits…</p></div>`;

  const f = { ...state.filters, ...overrides };
  const params = new URLSearchParams();
  if (f.type) params.set('type', f.type);
  if (f.quality_tier) params.set('quality_tier', f.quality_tier);
  if (f.min_abv) params.set('min_abv', f.min_abv);
  if (f.max_abv) params.set('max_abv', f.max_abv);
  if (f.sort) params.set('sort', f.sort);

  try {
    const data = await API.get(`/api/beverages?${params}`);
    const count = document.getElementById('explore-count');
    count.textContent = `${data.total} result${data.total !== 1 ? 's' : ''}`;

    if (!data.items.length) {
      grid.innerHTML = `<div class="empty-state"><div class="empty-state-icon">🔍</div><p>No spirits match your filters.</p></div>`;
      return;
    }
    grid.innerHTML = data.items.map(bevCardHTML).join('');
  } catch (e) {
    grid.innerHTML = `<div class="empty-state"><p>Failed to load spirits. Please try again.</p></div>`;
  }
}

function initExploreFilters() {
  // Populate type dropdown
  const typeSelect = document.getElementById('filter-type');
  const types = state.filterOptions.beverage_types || [];
  types.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = capitalize(t);
    typeSelect.appendChild(opt);
  });

  document.getElementById('apply-filters').addEventListener('click', () => {
    state.filters.type = document.getElementById('filter-type').value;
    state.filters.quality_tier = document.getElementById('filter-quality').value;
    state.filters.min_abv = document.getElementById('filter-abv-min').value;
    state.filters.max_abv = document.getElementById('filter-abv-max').value;
    state.filters.sort = document.getElementById('filter-sort').value;
    loadExplore();
  });

  document.getElementById('reset-filters').addEventListener('click', () => {
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-quality').value = '';
    document.getElementById('filter-abv-min').value = '';
    document.getElementById('filter-abv-max').value = '';
    document.getElementById('filter-sort').value = 'name';
    state.filters = { type: '', quality_tier: '', min_abv: '', max_abv: '', sort: 'name' };
    loadExplore();
  });
}

/* ── BEVERAGE MODAL ───────────────────────────────────────────────────────── */
async function openBeverageModal(id) {
  const modal = document.getElementById('beverage-modal');
  const body  = document.getElementById('bev-modal-body');
  body.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading…</p></div>`;
  modal.classList.remove('hidden');

  try {
    const [bev, pairings] = await Promise.all([
      API.get(`/api/beverages/${id}`),
      API.get(`/api/pairings/${id}`),
    ]);
    body.innerHTML = buildBevModal(bev, pairings);
  } catch (e) {
    body.innerHTML = `<button class="modal-close" onclick="closeModal('beverage-modal')">×</button><p style="color:var(--text-muted);padding:40px">Failed to load details.</p>`;
  }
}

function buildBevModal(bev, pairings) {
  const icon = TYPE_ICONS[bev.type] || '🍶';
  const flavors = bev.flavors || {};

  const flavorRows = Object.entries(flavors).map(([key, val]) => {
    if (val === 0) return '';
    return `
      <div class="flavor-row">
        <span class="flavor-row-name">${key}</span>
        <div class="flavor-track"><div class="flavor-fill" style="width:${val * 10}%"></div></div>
        <span class="flavor-row-val">${val}</span>
      </div>`;
  }).join('');

  const mixersHTML = (pairings.mixers || []).map(m =>
    `<div class="pairing-item"><span class="pairing-item-name">${m.mixer}:</span> ${m.reason}</div>`
  ).join('');

  const foodHTML = (pairings.food_pairings || []).map(f =>
    `<div class="pairing-item"><span class="pairing-item-name">${f.food}:</span> ${f.reason}</div>`
  ).join('');

  const garnishHTML = (pairings.garnishes || []).map(g => `<span class="flavor-tag">${g}</span>`).join('');

  const cocktailsHTML = (pairings.cocktail_suggestions || []).map(c => `
    <span class="flavor-tag" style="cursor:${c.id ? 'pointer' : 'default'}" onclick="${c.id ? `openCocktailModal(${c.id})` : ''}">
      ${c.name}
    </span>`).join('');

  return `
    <button class="modal-close" onclick="closeModal('beverage-modal')">×</button>
    <div class="modal-eyebrow">${capitalize(bev.type)} ${bev.subtype ? '· ' + bev.subtype : ''}</div>
    <div style="font-size:2.8rem;margin-bottom:8px">${icon}</div>
    <h2 class="modal-title">${bev.name}</h2>
    <div class="modal-brand">${bev.brand} · ${bev.region ? bev.region + ', ' : ''}${bev.country}</div>

    <div class="modal-meta-row">
      <span class="modal-meta-chip gold">${bev.abv}% ABV</span>
      ${tierBadge(bev.quality_tier)}
      <span class="modal-meta-chip">${bev.price_label || 'Price varies'}</span>
      <span class="modal-meta-chip">${bev.country}</span>
    </div>

    <p class="modal-description">${bev.description || ''}</p>

    ${bev.tasting_notes ? `<div class="modal-tasting">✦ ${bev.tasting_notes}</div>` : ''}

    <div class="modal-section-title">Flavour Profile</div>
    <div class="flavor-profile-chart">${flavorRows}</div>

    <div class="modal-section-title">Pairing & Mixing</div>
    <div class="pairing-grid">
      <div class="pairing-card">
        <div class="pairing-card-title">🧊 Mixers</div>
        ${mixersHTML}
      </div>
      <div class="pairing-card">
        <div class="pairing-card-title">🍽 Food Pairings</div>
        ${foodHTML}
      </div>
    </div>

    <div class="modal-section-title">Garnishes</div>
    <div class="flavor-tags">${garnishHTML}</div>

    <div class="modal-section-title">Recommended Cocktails</div>
    <div class="flavor-tags">${cocktailsHTML}</div>

    <div class="modal-actions">
      <button class="btn-primary" onclick="addToCompare(${bev.id}, '${bev.name.replace(/'/g, "\\'")}', '${bev.type}');closeModal('beverage-modal');">+ Add to Compare</button>
      <button class="btn-ghost" onclick="closeModal('beverage-modal')">Close</button>
    </div>`;
}

/* ── RECOMMEND ────────────────────────────────────────────────────────────── */
function initRecommend() {
  // Mood buttons
  document.querySelectorAll('.mood-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      state.recommend.mood = btn.dataset.mood;
    });
  });

  // Strength buttons
  document.querySelectorAll('.strength-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.strength-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      state.recommend.strength = btn.dataset.strength;
    });
  });

  // Flavor buttons (max 3)
  document.querySelectorAll('.flavor-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const flavor = btn.dataset.flavor;
      const idx = state.recommend.flavors.indexOf(flavor);
      if (idx > -1) {
        state.recommend.flavors.splice(idx, 1);
        btn.classList.remove('selected');
      } else {
        if (state.recommend.flavors.length >= 3) {
          toast('You can select up to 3 flavours.');
          return;
        }
        state.recommend.flavors.push(flavor);
        btn.classList.add('selected');
      }
      // Disable unselected if at limit
      document.querySelectorAll('.flavor-btn:not(.selected)').forEach(b => {
        b.classList.toggle('disabled', state.recommend.flavors.length >= 3);
      });
    });
  });

  document.getElementById('get-recommendations').addEventListener('click', fetchRecommendations);
}

async function fetchRecommendations() {
  if (!state.recommend.mood) { toast('Please select a mood first.'); return; }
  if (!state.recommend.strength) { toast('Please select a strength preference.'); return; }

  const resultsEl = document.getElementById('recommendations-results');
  resultsEl.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Finding your perfect drinks…</p></div>`;

  try {
    const data = await API.post('/api/recommend', {
      mood: state.recommend.mood,
      strength: state.recommend.strength,
      flavors: state.recommend.flavors,
      limit: 5,
    });

    if (!data.recommendations.length) {
      resultsEl.innerHTML = `<div class="results-placeholder"><div class="placeholder-icon">🔍</div><p>No matches found. Try adjusting your preferences.</p></div>`;
      return;
    }

    resultsEl.innerHTML = data.recommendations.map((r, i) => buildRecCard(r, i + 1)).join('');
  } catch (e) {
    resultsEl.innerHTML = `<div class="results-placeholder"><div class="placeholder-icon">⚠️</div><p>Failed to fetch recommendations. Please try again.</p></div>`;
  }
}

function buildRecCard(r, rank) {
  const breakdown = r.score_breakdown || {};
  const maxScore = 100;

  const scoreBar = (label, val) => `
    <div class="score-bar-row">
      <span class="score-bar-label">${label}</span>
      <div class="score-bar-track">
        <div class="score-bar-fill" style="width:${(val / 40) * 100}%"></div>
      </div>
      <span class="score-bar-val">${val}</span>
    </div>`;

  const icon = TYPE_ICONS[r.type] || '🍶';
  return `
    <div class="rec-card" onclick="openBeverageModal(${r.id})">
      <div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
          <span style="font-size:1.6rem">${icon}</span>
          <div>
            <div class="rec-name">${r.name}</div>
            <div class="rec-brand">${r.brand} · ${r.country} · ${r.abv}% ABV</div>
          </div>
        </div>
        <div class="rec-explanation">${r.explanation}</div>
        <div class="rec-score-bar-group">
          ${scoreBar('Mood', breakdown.mood || 0)}
          ${scoreBar('Strength', breakdown.strength || 0)}
          ${scoreBar('Flavour', breakdown.flavor || 0)}
        </div>
      </div>
      <div class="rec-right">
        <div class="rec-rank">#${rank}</div>
        <div class="rec-score-ring">
          <span class="rec-score-num">${Math.round(r.recommendation_score)}</span>
          <span class="rec-score-label">Score</span>
        </div>
        <span class="bev-price">${r.price_label || '—'}</span>
      </div>
    </div>`;
}

/* ── COMPARE ──────────────────────────────────────────────────────────────── */
function initCompare() {
  renderCompareSlots();

  // Set up search
  const searchInput = document.createElement('input');
  searchInput.type = 'text';
  searchInput.placeholder = 'Search to add a spirit to compare…';
  const searchResultsEl = document.createElement('div');
  searchResultsEl.className = 'compare-search-results';

  const container = document.createElement('div');
  container.className = 'compare-search-container';
  container.appendChild(searchInput);

  const selector = document.querySelector('.compare-selector');
  const slots = document.getElementById('compare-slots');
  selector.insertBefore(container, slots.nextSibling);
  selector.insertBefore(searchResultsEl, container.nextSibling);

  let debounce;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounce);
    const q = searchInput.value.trim();
    if (q.length < 2) { searchResultsEl.innerHTML = ''; return; }
    debounce = setTimeout(async () => {
      const data = await API.get(`/api/search?q=${encodeURIComponent(q)}`);
      searchResultsEl.innerHTML = (data.beverages || []).map(b => `
        <div class="compare-search-item" onclick="addToCompare(${b.id}, '${b.name.replace(/'/g, "\\'")}', '${b.type}')">
          ${TYPE_ICONS[b.type] || '🍶'} ${b.name} <span style="color:var(--text-muted);font-size:0.7rem">· ${b.abv}% · ${capitalize(b.type)}</span>
        </div>`).join('') || '<div class="compare-search-item" style="cursor:default;color:var(--text-muted)">No results</div>';
    }, 280);
  });

  document.getElementById('run-compare').addEventListener('click', runCompare);
  document.getElementById('clear-compare').addEventListener('click', () => {
    state.compareIds = [];
    renderCompareSlots();
    document.getElementById('compare-results').classList.add('hidden');
    document.getElementById('run-compare').disabled = true;
  });
}

function addToCompare(id, name, type) {
  if (state.compareIds.length >= 4) { toast('Maximum 4 spirits can be compared at once.'); return; }
  if (state.compareIds.includes(id)) { toast(`${name} is already in the comparison.`); return; }
  state.compareIds.push(id);
  renderCompareSlots();
  document.getElementById('run-compare').disabled = state.compareIds.length < 2;
  toast(`${name} added to comparison.`);
}

function removeFromCompare(id) {
  state.compareIds = state.compareIds.filter(i => i !== id);
  renderCompareSlots();
  document.getElementById('run-compare').disabled = state.compareIds.length < 2;
  document.getElementById('compare-results').classList.add('hidden');
}

async function renderCompareSlots() {
  const slotsEl = document.getElementById('compare-slots');
  if (!slotsEl) return;

  let html = '';
  // Filled slots
  for (const id of state.compareIds) {
    const bev = await API.get(`/api/beverages/${id}`);
    html += `
      <div class="compare-slot filled">
        <span style="font-size:1.6rem">${TYPE_ICONS[bev.type] || '🍶'}</span>
        <span class="compare-slot-name">${bev.name}</span>
        <span class="compare-slot-type">${capitalize(bev.type)}</span>
        <span class="compare-slot-remove" onclick="removeFromCompare(${id})">×</span>
      </div>`;
  }
  // Empty slots
  const emptyCount = 4 - state.compareIds.length;
  for (let i = 0; i < emptyCount; i++) {
    html += `
      <div class="compare-slot">
        <div class="slot-add-prompt">
          <span class="slot-add-icon">+</span>
          <span>Search to add</span>
        </div>
      </div>`;
  }
  slotsEl.innerHTML = html;
}

async function runCompare() {
  if (state.compareIds.length < 2) return;

  const resultsEl = document.getElementById('compare-results');
  resultsEl.classList.remove('hidden');
  resultsEl.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Analysing spirits…</p></div>`;

  try {
    const data = await API.post('/api/compare', { ids: state.compareIds });
    resultsEl.innerHTML = buildCompareTable(data);
  } catch (e) {
    resultsEl.innerHTML = `<p style="color:var(--text-muted);padding:20px">Failed to compare spirits. Please try again.</p>`;
  }
}

function buildCompareTable(data) {
  const bevs = data.beverages || [];
  if (!bevs.length) return '<p>No comparison data.</p>';

  const summary = data.summary || {};
  const summaryHTML = `
    <div class="compare-summary-card">
      ${summary.highest_abv ? `<div class="summary-fact"><div class="summary-fact-label">Highest ABV</div><div class="summary-fact-value">${summary.highest_abv}</div></div>` : ''}
      ${summary.lowest_abv  ? `<div class="summary-fact"><div class="summary-fact-label">Lowest ABV</div><div class="summary-fact-value">${summary.lowest_abv}</div></div>` : ''}
      ${summary.best_value  ? `<div class="summary-fact"><div class="summary-fact-label">Best Value</div><div class="summary-fact-value">${summary.best_value}</div></div>` : ''}
    </div>`;

  const headerCols = bevs.map(b => `<th class="bev-col">${TYPE_ICONS[b.type] || '🍶'} ${b.name}</th>`).join('');

  const row = (label, fn) => `
    <tr>
      <td class="row-label">${label}</td>
      ${bevs.map(b => `<td>${fn(b)}</td>`).join('')}
    </tr>`;

  const flavorKeys = data.flavor_keys || ['sweet','bitter','smoky','fruity','spicy','floral','earthy','crisp','woody','creamy'];
  const flavorRows = flavorKeys.map(key => `
    <tr>
      <td class="row-label">${capitalize(key)}</td>
      ${bevs.map(b => {
        const val = (b.flavors || {})[key] || 0;
        return `<td><div class="flavor-bar-cell">
          <div class="flavor-bar-mini"><div class="flavor-bar-mini-fill" style="width:${val*10}%"></div></div>
          <span style="font-size:0.75rem;color:var(--gold-light)">${val}</span>
        </div></td>`;
      }).join('')}
    </tr>`).join('');

  return `
    ${summaryHTML}
    <div class="glass-card compare-table-wrapper">
      <table class="compare-table">
        <thead>
          <tr>
            <th>Attribute</th>
            ${headerCols}
          </tr>
        </thead>
        <tbody>
          ${row('Brand',         b => b.brand)}
          ${row('Type',          b => capitalize(b.type) + (b.subtype ? ` / ${b.subtype}` : ''))}
          ${row('Country',       b => b.country)}
          ${row('ABV',           b => `<span class="highlight">${b.abv}%</span>`)}
          ${row('Quality Tier',  b => TIER_LABELS[b.quality_tier] || b.quality_tier)}
          ${row('Price Range',   b => b.price_label || '—')}
          <tr><td colspan="${bevs.length + 1}" style="padding:8px 20px;font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--gold);border-bottom:1px solid var(--border)">Flavour Profile (0–10)</td></tr>
          ${flavorRows}
        </tbody>
      </table>
    </div>`;
}

/* ── COCKTAILS ────────────────────────────────────────────────────────────── */
async function loadCocktails() {
  const grid = document.getElementById('cocktail-grid');
  grid.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading cocktails…</p></div>`;

  const f = state.cocktailFilters;
  const params = new URLSearchParams();
  if (f.base_spirit) params.set('base_spirit', f.base_spirit);
  if (f.mood) params.set('mood', f.mood);
  if (f.difficulty) params.set('difficulty', f.difficulty);

  try {
    const data = await API.get(`/api/cocktails?${params}`);
    if (!data.cocktails.length) {
      grid.innerHTML = `<div class="empty-state"><div class="empty-state-icon">🍹</div><p>No cocktails match your filters.</p></div>`;
      return;
    }
    grid.innerHTML = data.cocktails.map(cocktailCardHTML).join('');
  } catch (e) {
    grid.innerHTML = `<div class="empty-state"><p>Failed to load cocktails.</p></div>`;
  }
}

function cocktailCardHTML(c) {
  const diffCls = `diff-${c.difficulty}`;
  const moodTags = (c.mood_tags || []).map(m => `<span class="mood-tag">${m}</span>`).join('');
  return `
    <div class="cocktail-card" onclick="openCocktailModal(${c.id})">
      <div class="cocktail-card-header">
        <div class="cocktail-name">${c.name}</div>
        <span class="difficulty-badge ${diffCls}">${capitalize(c.difficulty)}</span>
      </div>
      <div class="cocktail-base">${capitalize(c.base_spirit)} Base</div>
      <div class="cocktail-desc">${c.description || ''}</div>
      <div class="cocktail-meta">
        <span class="cocktail-meta-item">🥃 ~${c.abv_estimate || '?'}% ABV</span>
        <span class="cocktail-meta-item">🥛 ${c.glass_type || ''}</span>
      </div>
      <div class="cocktail-mood-tags">${moodTags}</div>
    </div>`;
}

async function openCocktailModal(id) {
  const modal = document.getElementById('cocktail-modal');
  const body  = document.getElementById('cocktail-modal-body');
  body.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading…</p></div>`;
  modal.classList.remove('hidden');

  try {
    const c = await API.get(`/api/cocktails/${id}`);
    body.innerHTML = buildCocktailModal(c);
  } catch (e) {
    body.innerHTML = `<button class="modal-close" onclick="closeModal('cocktail-modal')">×</button><p style="color:var(--text-muted);padding:40px">Failed to load cocktail details.</p>`;
  }
}

function buildCocktailModal(c) {
  const diffCls = `diff-${c.difficulty}`;
  const ingredientsHTML = (c.ingredients || []).map(ing => `
    <li>
      <span class="ingredient-name">${ing.item}</span>
      <span class="ingredient-amount">${ing.amount}</span>
    </li>`).join('');

  const moodTagsHTML = (c.mood_tags || []).map(m => `<span class="mood-tag">${m}</span>`).join('');
  const flavorHTML   = (c.flavor_profile || []).map(f => `<span class="flavor-tag">${f}</span>`).join('');

  return `
    <button class="modal-close" onclick="closeModal('cocktail-modal')">×</button>
    <div class="modal-eyebrow">${capitalize(c.base_spirit)} Cocktail</div>
    <h2 class="modal-title">${c.name}</h2>
    <div class="modal-brand">${c.glass_type || ''} · ~${c.abv_estimate || '?'}% ABV</div>

    <div class="modal-meta-row">
      <span class="modal-meta-chip gold">${capitalize(c.base_spirit)} Base</span>
      <span class="difficulty-badge ${diffCls}">${capitalize(c.difficulty)}</span>
      ${moodTagsHTML}
    </div>

    <p class="modal-description">${c.description || ''}</p>

    <div class="modal-section-title">Ingredients</div>
    <ul class="ingredient-list">${ingredientsHTML}</ul>

    <div class="modal-section-title">Instructions</div>
    <p class="instructions-text">${c.instructions || ''}</p>

    ${c.garnish ? `<div class="modal-section-title">Garnish</div><p class="modal-description">${c.garnish}</p>` : ''}

    <div class="modal-section-title">Flavour Profile</div>
    <div class="flavor-tags">${flavorHTML}</div>

    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeModal('cocktail-modal')">Close</button>
    </div>`;
}

/* ── GLOBAL SEARCH ────────────────────────────────────────────────────────── */
function initGlobalSearch() {
  const input    = document.getElementById('global-search');
  const dropdown = document.getElementById('search-results-dropdown');

  input.addEventListener('input', () => {
    clearTimeout(state.searchDebounceTimer);
    const q = input.value.trim();
    if (q.length < 2) { dropdown.classList.add('hidden'); return; }
    state.searchDebounceTimer = setTimeout(async () => {
      const data = await API.get(`/api/search?q=${encodeURIComponent(q)}`);
      renderSearchDropdown(data, dropdown);
    }, 300);
  });

  document.addEventListener('click', e => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.add('hidden');
    }
  });
}

function renderSearchDropdown(data, el) {
  const bevs = data.beverages || [];
  const cocktails = data.cocktails || [];

  if (!bevs.length && !cocktails.length) {
    el.innerHTML = `<div class="search-item"><span class="search-item-name" style="color:var(--text-muted)">No results found</span></div>`;
    el.classList.remove('hidden');
    return;
  }

  let html = '';
  if (bevs.length) {
    html += `<div class="search-section-title">Spirits & Beverages</div>`;
    html += bevs.map(b => `
      <div class="search-item" onclick="openBeverageModal(${b.id});document.getElementById('search-results-dropdown').classList.add('hidden');document.getElementById('global-search').value=''">
        <span class="search-item-type">${TYPE_ICONS[b.type] || ''} ${capitalize(b.type)}</span>
        <div>
          <div class="search-item-name">${b.name}</div>
          <div class="search-item-sub">${b.brand} · ${b.abv}% ABV</div>
        </div>
      </div>`).join('');
  }
  if (cocktails.length) {
    html += `<div class="search-section-title">Cocktails</div>`;
    html += cocktails.map(c => `
      <div class="search-item" onclick="openCocktailModal(${c.id});document.getElementById('search-results-dropdown').classList.add('hidden');document.getElementById('global-search').value=''">
        <span class="search-item-type">🍹 Cocktail</span>
        <div>
          <div class="search-item-name">${c.name}</div>
          <div class="search-item-sub">${capitalize(c.base_spirit)} base</div>
        </div>
      </div>`).join('');
  }

  el.innerHTML = html;
  el.classList.remove('hidden');
}

/* ── MODAL HELPERS ────────────────────────────────────────────────────────── */
function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
}

/* ── COCKTAIL FILTERS ─────────────────────────────────────────────────────── */
function initCocktailFilters() {
  const spiritSelect = document.getElementById('cocktail-filter-spirit');
  const spirits = state.filterOptions.cocktail_spirits || [];
  spirits.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s;
    opt.textContent = capitalize(s);
    spiritSelect.appendChild(opt);
  });

  document.getElementById('apply-cocktail-filters').addEventListener('click', () => {
    state.cocktailFilters.base_spirit = document.getElementById('cocktail-filter-spirit').value;
    state.cocktailFilters.mood = document.getElementById('cocktail-filter-mood').value;
    state.cocktailFilters.difficulty = document.getElementById('cocktail-filter-difficulty').value;
    loadCocktails();
  });
}

/* ── HERO CATEGORY PILLS ──────────────────────────────────────────────────── */
function initCategoryPills() {
  document.querySelectorAll('.cat-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      state.filters.type = btn.dataset.type;
      // Reset other filters
      document.getElementById('filter-type').value = btn.dataset.type;
      navigate('explore');
    });
  });
}

/* ── INIT ─────────────────────────────────────────────────────────────────── */
async function init() {
  // Load filter options from API
  try {
    state.filterOptions = await API.get('/api/filters');
  } catch (e) {
    console.error('Failed to load filter options:', e);
  }

  // Wire up navigation
  document.querySelectorAll('[data-nav]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      navigate(el.dataset.nav);
    });
  });

  // Modal close on overlay click
  document.getElementById('bev-modal-overlay').addEventListener('click',     () => closeModal('beverage-modal'));
  document.getElementById('cocktail-modal-overlay').addEventListener('click', () => closeModal('cocktail-modal'));

  // Escape key to close modals
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closeModal('beverage-modal');
      closeModal('cocktail-modal');
    }
  });

  initExploreFilters();
  initRecommend();
  initGlobalSearch();
  initCategoryPills();
  initCocktailFilters();

  // Show hero on load
  navigate('hero');
}

document.addEventListener('DOMContentLoaded', init);
