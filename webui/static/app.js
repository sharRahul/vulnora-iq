const state = {
  config: { targets: {}, profiles: {} },
  session: { auth_enabled: false, authenticated: false, auth_required: false, permissions: [] },
  tokenHeader: 'X-VulnoraIQ-Token',
  currentJob: null,
  streamAbort: null,
  csrfToken: null,
  jobs: [],
  currentSummary: null,
  currentFindings: [],
  filters: {
    catalogSearch: '',
    catalogCategory: 'all',
    catalogMode: 'all',
    historySearch: '',
    historyStatus: 'all',
    findingSeverity: 'all',
    findingPolicy: 'all',
  },
};

const TOKEN_STORAGE_KEY = 'vulnoraiq.token';
const qs = (selector) => document.querySelector(selector);

const CATEGORY_ORDER = [
  'Assessment suites',
  'OWASP LLM Top 10 single tests',
  'RAG and vector store tests',
  'Agentic and tool-use tests',
  'Other tests',
];

const SEVERITY_ORDER = ['critical', 'high', 'medium', 'low', 'info'];

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function normalise(value) {
  return String(value || '').trim().toLowerCase();
}

// ----- Auth / session helpers -------------------------------------------------

function getToken() {
  try {
    return sessionStorage.getItem(TOKEN_STORAGE_KEY) || '';
  } catch (error) {
    return '';
  }
}

function setToken(token) {
  try {
    if (token) sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
    else sessionStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch (error) {
    /* storage unavailable - token simply will not persist */
  }
  state.csrfToken = null;
}

function authHeaders(extra = {}) {
  const headers = { ...extra };
  const token = getToken();
  if (token) headers[state.tokenHeader] = token;
  return headers;
}

async function apiFetch(url, options = {}) {
  const opts = { ...options };
  opts.headers = authHeaders(opts.headers || {});
  const response = await fetch(url, opts);
  if (response.status === 401) {
    state.session.authenticated = false;
    state.session.auth_required = true;
    renderSession();
    throw new Error('Authentication required. Enter a valid access token to continue.');
  }
  if (response.status === 403) {
    throw new Error('Your account does not have permission for that action.');
  }
  return response;
}

function can(permission) {
  return Array.isArray(state.session.permissions) && state.session.permissions.includes(permission);
}

async function loadSession() {
  const response = await apiFetch('/api/session');
  state.session = await response.json();
  if (state.session.token_header) state.tokenHeader = state.session.token_header;
  renderSession();
  return state.session;
}

function renderSession() {
  const area = qs('#session-area');
  if (!area) return;
  const session = state.session;

  if (!session.auth_enabled) {
    area.innerHTML = `
      <span class="session-badge open">Auth disabled</span>
      <div class="session-identity"><strong>Open access mode</strong><small>Demo testing only</small></div>
    `;
    return;
  }

  if (session.authenticated) {
    area.innerHTML = `
      <div class="session-identity">
        <strong>${escapeHtml(session.username || 'Authenticated user')}</strong>
        <small>${escapeHtml(session.role || 'role')} · ${session.permissions.length} permission${session.permissions.length === 1 ? '' : 's'}</small>
      </div>
      <span class="session-badge">Signed in</span>
      <button type="button" id="sign-out" class="topbar-button">Sign out</button>
    `;
    const signOut = qs('#sign-out');
    if (signOut) signOut.addEventListener('click', signOutHandler);
    return;
  }

  area.innerHTML = `
    <span class="session-badge locked">Sign in required</span>
    <form id="signin-form" class="signin-form">
      <input id="token-input" type="password" autocomplete="off" placeholder="Access token" aria-label="Access token">
      <button type="submit" class="topbar-button accent">Connect</button>
    </form>
  `;
  const form = qs('#signin-form');
  if (form) form.addEventListener('submit', signInHandler);
}

async function signInHandler(event) {
  event.preventDefault();
  const input = qs('#token-input');
  const token = (input && input.value || '').trim();
  if (!token) return;
  setToken(token);
  try {
    await loadSession();
    if (!state.session.authenticated) {
      setToken('');
      renderSession();
      qs('#form-message').textContent = 'That token was not accepted. Please check it and try again.';
      return;
    }
    qs('#form-message').textContent = '';
    await bootstrapData();
  } catch (error) {
    qs('#form-message').textContent = error.message;
  }
}

function signOutHandler() {
  setToken('');
  if (state.streamAbort) state.streamAbort.abort();
  loadSession().then(() => {
    clearWorkspace();
  });
}

function clearWorkspace() {
  qs('#target-select').innerHTML = '';
  qs('#profile-select').innerHTML = '';
  qs('#test-catalog').innerHTML = '';
  qs('#selected-profile-detail').innerHTML = '';
  qs('#job-history').innerHTML = '<div class="empty-state">Sign in to view and run assessments.</div>';
  qs('#history-summary').innerHTML = '';
  qs('#event-list').innerHTML = '';
  setProgress(0, 'Idle');
  renderActiveScan({ status: 'idle', stage: 'Idle', message: 'Sign in to view and run assessments.', progress: 0 });
  renderRunReadiness();
  updateFormAvailability();
}

function updateFormAvailability() {
  const button = qs('.primary');
  const locked = state.session.auth_enabled && !state.session.authenticated;
  button.disabled = locked;
  qs('#authorised').disabled = locked;
  qs('#target-select').disabled = locked;
  qs('#profile-select').disabled = locked;
}

async function getCsrfToken() {
  if (state.csrfToken) return state.csrfToken;
  const response = await apiFetch('/api/csrf-token');
  const data = await response.json();
  state.csrfToken = data.csrf_token;
  return state.csrfToken;
}

// ----- Progress + running scan rendering -------------------------------------

function setProgress(value, status) {
  const safe = Math.round(Math.max(0, Math.min(100, Number(value || 0))));
  const circumference = 326.7;
  qs('#progress-circle').style.strokeDashoffset = String(circumference - (safe / 100) * circumference);
  qs('#progress-value').textContent = `${safe}%`;
  qs('#active-scan-percent').textContent = `${safe}%`;
  qs('#scan-status').textContent = status || 'Idle';
  qs('#progress-bar').style.width = `${safe}%`;
}

function scanCardClass(status) {
  const normalisedStatus = normalise(status || 'idle');
  if (normalisedStatus === 'completed') return 'completed';
  if (normalisedStatus === 'failed' || normalisedStatus === 'error') return 'failed';
  if (normalisedStatus === 'idle') return 'idle';
  return 'running';
}

function formatTimestamp(value) {
  if (!value) return 'Just now';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Just now';
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function renderActiveScan(update = {}) {
  const current = state.currentJob || {};
  const target = update.target || current.target || qs('#target-select')?.value || '-';
  const profileName = update.profile || current.profile || qs('#profile-select')?.value || '';
  const profile = state.config.profiles?.[profileName] || {};
  const profileNameDisplay = profileName ? profileDisplayName(profileName, profile) : '-';
  const progress = update.progress ?? current.progress ?? 0;
  const status = update.status || current.status || 'idle';
  const stage = update.stage || status || 'Idle';
  const message = update.message || 'Waiting for scan activity.';

  const card = qs('#active-scan-card');
  card.className = `active-scan-card ${scanCardClass(status)}`;
  qs('#active-scan-title').textContent = scanCardClass(status) === 'idle' ? 'No scan running' : `${profileNameDisplay} on ${target}`;
  qs('#active-scan-detail').textContent = scanCardClass(status) === 'idle'
    ? 'Choose a target and test option to start a live assessment.'
    : `${profileCategory(profile, profileName)} · ${profileModules(profile).length || 'configured'} module${profileModules(profile).length === 1 ? '' : 's'}`;
  qs('#active-scan-target').textContent = target || '-';
  qs('#active-scan-profile').textContent = profileNameDisplay || '-';
  qs('#active-scan-stage').textContent = stage || 'Idle';
  qs('#active-scan-updated').textContent = formatTimestamp(update.timestamp);
  qs('#active-scan-message').textContent = message;
  setProgress(progress, stage);
}

function updateActiveScanFromJob(job, message = '') {
  const events = Array.isArray(job.events) ? job.events : [];
  const latest = events.length ? events[events.length - 1] : null;
  renderActiveScan({
    target: job.target,
    profile: job.profile,
    status: job.status || 'running',
    stage: latest?.stage || job.status || 'Running',
    message: message || latest?.message || `Scan ${job.status || 'running'}.`,
    progress: job.progress ?? latest?.progress ?? (job.status === 'completed' ? 100 : 0),
    timestamp: latest?.timestamp || job.updated_at || job.created_at,
  });
}

function addEvent(event) {
  const li = document.createElement('li');
  li.className = event.level === 'error' ? 'error' : '';
  li.innerHTML = `<strong>${escapeHtml(event.stage)}</strong><div>${escapeHtml(event.message)}</div><small>${new Date(event.timestamp).toLocaleString()} · ${event.progress}%</small>`;
  qs('#event-list').prepend(li);
  renderActiveScan({
    status: event.level === 'error' ? 'failed' : 'running',
    stage: event.stage,
    message: event.message,
    progress: event.progress,
    timestamp: event.timestamp,
  });
}

function badge(value) {
  const normalisedValue = normalise(value || 'unknown');
  return `<span class="badge ${escapeHtml(normalisedValue)}">${escapeHtml(normalisedValue)}</span>`;
}

function profileDisplayName(name, profile) {
  return profile.display_name || name.replace(/^test_/, '').replaceAll('_', ' ');
}

function profileCategory(profile, name = '') {
  if (profile.category) return profile.category;
  if (['baseline', 'rag', 'agent', 'full'].includes(name)) return 'Assessment suites';
  if (name.startsWith('test_owasp_llm')) return 'OWASP LLM Top 10 single tests';
  if (name.startsWith('test_rag') || name.startsWith('test_retrieval') || name.startsWith('test_corpus')) return 'RAG and vector store tests';
  if (name.startsWith('test_agent') || name.startsWith('test_tool') || name.startsWith('test_memory') || name.startsWith('test_multi_agent')) return 'Agentic and tool-use tests';
  return 'Other tests';
}

function profileModules(profile) {
  return Array.isArray(profile.modules) ? profile.modules : [];
}

function isSuiteProfile(name, profile) {
  return profileCategory(profile, name) === 'Assessment suites' || ['baseline', 'rag', 'agent', 'full'].includes(name);
}

function orderedCategories(groups) {
  const known = CATEGORY_ORDER.filter((category) => groups.has(category));
  const extra = [...groups.keys()].filter((category) => !CATEGORY_ORDER.includes(category)).sort();
  return [...known, ...extra];
}

function profileEntries() {
  return Object.entries(state.config.profiles || {});
}

function filteredProfileEntries() {
  const query = state.filters.catalogSearch;
  return profileEntries().filter(([name, profile]) => {
    const category = profileCategory(profile, name);
    if (state.filters.catalogCategory !== 'all' && category !== state.filters.catalogCategory) return false;
    if (state.filters.catalogMode === 'suite' && !isSuiteProfile(name, profile)) return false;
    if (state.filters.catalogMode === 'single' && isSuiteProfile(name, profile)) return false;
    if (!query) return true;
    const modules = profileModules(profile).join(' ');
    const haystack = normalise(`${name} ${profileDisplayName(name, profile)} ${profile.description || ''} ${category} ${modules}`);
    return haystack.includes(query);
  });
}

function renderCatalogFilters() {
  const categorySelect = qs('#catalog-category-filter');
  if (!categorySelect) return;
  const groups = new Map();
  profileEntries().forEach(([name, profile]) => {
    const category = profileCategory(profile, name);
    if (!groups.has(category)) groups.set(category, 0);
    groups.set(category, groups.get(category) + 1);
  });
  const options = ['<option value="all">All categories</option>'].concat(
    orderedCategories(groups).map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)} (${groups.get(category)})</option>`),
  );
  categorySelect.innerHTML = options.join('');
  categorySelect.value = state.filters.catalogCategory;
  qs('#catalog-search').value = state.filters.catalogSearch;
  qs('#catalog-mode-filter').value = state.filters.catalogMode;
}

function renderProfileSelect() {
  const profileSelect = qs('#profile-select');
  const groups = new Map();
  profileEntries().forEach(([name, profile]) => {
    const category = profileCategory(profile, name);
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push([name, profile]);
  });

  profileSelect.innerHTML = orderedCategories(groups).map((category) => {
    const options = groups.get(category)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([name, profile]) => `<option value="${escapeHtml(name)}">${escapeHtml(profileDisplayName(name, profile))} · ${profileModules(profile).length || 'configured'} module${profileModules(profile).length === 1 ? '' : 's'}</option>`)
      .join('');
    return `<optgroup label="${escapeHtml(category)}">${options}</optgroup>`;
  }).join('');
}

function renderRunReadiness() {
  const target = qs('#target-select')?.value || '-';
  const selected = qs('#profile-select')?.value || '';
  const profile = state.config.profiles[selected] || {};
  const modules = profileModules(profile);
  const targetConfig = state.config.targets?.[target] || {};
  const targetType = targetConfig.type || (target === 'demo' ? 'demo' : 'configured');
  const needsAuthorisation = target !== 'demo' && targetType !== 'demo';
  const authorised = qs('#authorised')?.checked;
  const canRunConfigured = can('scan:configured') || can('scan:create') || !state.session.auth_enabled;
  const blocked = needsAuthorisation && (!authorised || !canRunConfigured);

  qs('#readiness-target').textContent = target;
  qs('#readiness-profile').textContent = selected ? profileDisplayName(selected, profile) : '-';
  qs('#readiness-modules').textContent = modules.length ? `${modules.length} module${modules.length === 1 ? '' : 's'}` : 'Configured server-side';
  qs('#readiness-authorisation').textContent = needsAuthorisation ? (authorised ? 'Confirmed' : 'Required') : 'Demo/local';
  qs('#readiness-title').textContent = blocked ? 'Action needed before run' : 'Ready to run';
  qs('#readiness-message').textContent = blocked
    ? 'Configured targets require authorisation confirmation and a role that can run configured scans.'
    : `${profileDisplayName(selected, profile)} will run against ${target}.`;
  qs('#run-readiness').classList.toggle('blocked', blocked);
}

function renderSelectedProfile() {
  const selected = qs('#profile-select').value;
  const profile = state.config.profiles[selected] || {};
  const modules = profileModules(profile);
  qs('#selected-profile-detail').innerHTML = `
    <strong>${escapeHtml(profileDisplayName(selected, profile))}</strong>
    <p>${escapeHtml(profile.description || 'No description available.')}</p>
    <small>${escapeHtml(profileCategory(profile, selected))} · ${modules.length || 'configured'} module${modules.length === 1 ? '' : 's'} selected</small>
  `;
  renderRunReadiness();
  if (!state.currentJob || ['completed', 'failed'].includes(state.currentJob.status)) {
    renderActiveScan({
      status: 'idle',
      stage: 'Ready',
      message: `Ready to run ${profileDisplayName(selected, profile)}.`,
      progress: 0,
      target: qs('#target-select').value,
      profile: selected,
    });
  }
  document.querySelectorAll('.profile-card').forEach((card) => {
    const active = card.dataset.profile === selected;
    card.classList.toggle('active', active);
    const selectButton = card.querySelector('[data-profile-select]');
    if (selectButton) {
      selectButton.setAttribute('aria-pressed', active ? 'true' : 'false');
      selectButton.textContent = active ? 'Selected' : 'Select this option';
    }
  });
}

function renderTestCatalog() {
  const catalog = qs('#test-catalog');
  const groups = new Map();
  const entries = filteredProfileEntries();
  entries.forEach(([name, profile]) => {
    const category = profileCategory(profile, name);
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push([name, profile]);
  });

  qs('#catalog-count').textContent = `Showing ${entries.length} of ${profileEntries().length} option${profileEntries().length === 1 ? '' : 's'}`;
  if (!entries.length) {
    catalog.innerHTML = '<div class="empty-state compact-empty">No test options match the current filters.</div>';
    return;
  }

  catalog.innerHTML = orderedCategories(groups).map((category) => {
    const cards = groups.get(category)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([name, profile]) => {
        const modules = profileModules(profile);
        const moduleBadges = modules.length
          ? modules.map((moduleName) => `<span>${escapeHtml(moduleName)}</span>`).join('')
          : '<span>Configured server-side profile</span>';
        return `
          <article class="profile-card" data-profile="${escapeHtml(name)}">
            <div>
              <strong>${escapeHtml(profileDisplayName(name, profile))}</strong>
              <p>${escapeHtml(profile.description || '')}</p>
              <div class="module-list">${moduleBadges}</div>
            </div>
            <button type="button" data-profile-select="${escapeHtml(name)}" aria-pressed="false">Select this option</button>
          </article>
        `;
      }).join('');
    return `
      <section class="test-category">
        <div class="test-category-header">
          <h4>${escapeHtml(category)}</h4>
          <span>${groups.get(category).length} option${groups.get(category).length === 1 ? '' : 's'}</span>
        </div>
        <div class="profile-card-grid">${cards}</div>
      </section>
    `;
  }).join('');

  catalog.querySelectorAll('[data-profile-select]').forEach((button) => {
    button.addEventListener('click', () => {
      qs('#profile-select').value = button.dataset.profileSelect;
      renderSelectedProfile();
      qs('#scan-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
  renderSelectedProfile();
}

async function loadConfig() {
  const response = await apiFetch('/api/config');
  state.config = await response.json();
  const targetSelect = qs('#target-select');
  const targets = Object.keys(state.config.targets || {}).length ? state.config.targets : { demo: { type: 'demo' } };
  targetSelect.innerHTML = Object.entries(targets)
    .map(([name, target]) => `<option value="${escapeHtml(name)}">${escapeHtml(name)} · ${escapeHtml(target.type || 'target')}</option>`)
    .join('');
  renderProfileSelect();
  renderCatalogFilters();
  renderTestCatalog();
}

// ----- History ----------------------------------------------------------------

function renderHistorySummary(jobs) {
  const counts = jobs.reduce((acc, job) => {
    const status = normalise(job.status || 'unknown');
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});
  const items = [
    ['Total', jobs.length],
    ['Running', counts.running || 0],
    ['Queued', counts.queued || 0],
    ['Completed', counts.completed || 0],
    ['Failed', counts.failed || 0],
  ];
  qs('#history-summary').innerHTML = items.map(([label, count]) => `
    <article><span>${escapeHtml(label)}</span><strong>${count}</strong></article>
  `).join('');
}

function filteredJobs() {
  const search = state.filters.historySearch;
  return state.jobs.filter((job) => {
    const status = normalise(job.status || 'unknown');
    if (state.filters.historyStatus !== 'all' && status !== state.filters.historyStatus) return false;
    if (!search) return true;
    const profile = state.config.profiles[job.profile] || {};
    const haystack = normalise(`${job.target} ${job.profile} ${profileDisplayName(job.profile, profile)} ${status}`);
    return haystack.includes(search);
  });
}

function renderJobHistory() {
  const container = qs('#job-history');
  renderHistorySummary(state.jobs);
  const jobs = filteredJobs();
  if (!state.jobs.length) {
    container.innerHTML = '<div class="empty-state">No scan history yet.</div>';
    return;
  }
  if (!jobs.length) {
    container.innerHTML = '<div class="empty-state compact-empty">No scans match the current filters.</div>';
    return;
  }
  container.innerHTML = jobs.map((job) => `
    <div class="job-item status-${escapeHtml(normalise(job.status || 'unknown'))}">
      <div>
        <strong>${escapeHtml(job.target)} / ${escapeHtml(profileDisplayName(job.profile, state.config.profiles[job.profile] || {}))}</strong><br>
        <small>${badge(job.status)} ${job.progress}% · ${new Date(job.created_at).toLocaleString()}</small>
      </div>
      <button type="button" data-job-id="${escapeHtml(job.id)}">View</button>
    </div>
  `).join('');
  container.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => loadJob(button.dataset.jobId));
  });
}

async function refreshJobs() {
  const response = await apiFetch('/api/scans');
  const data = await response.json();
  state.jobs = [...(data.jobs || [])].sort((left, right) => new Date(right.created_at) - new Date(left.created_at));
  renderJobHistory();
}

async function startScan(event) {
  event.preventDefault();
  qs('#form-message').textContent = '';
  qs('#event-list').innerHTML = '';
  const payload = {
    target: qs('#target-select').value,
    profile: qs('#profile-select').value,
    authorised: qs('#authorised').checked,
  };
  renderActiveScan({
    target: payload.target,
    profile: payload.profile,
    status: 'queued',
    stage: 'Queued',
    message: 'Submitting assessment request to the local server.',
    progress: 0,
  });
  const button = qs('.primary');
  button.disabled = true;
  button.textContent = 'Starting...';
  try {
    const csrfToken = await getCsrfToken();
    const response = await apiFetch('/api/scans', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to start scan');
    state.currentJob = data;
    updateActiveScanFromJob(data, 'Scan accepted. Waiting for first progress event.');
    streamJob(data.id);
    await refreshJobs();
  } catch (error) {
    qs('#form-message').textContent = error.message;
    renderActiveScan({
      target: payload.target,
      profile: payload.profile,
      status: 'failed',
      stage: 'Failed to start',
      message: error.message,
      progress: 0,
    });
  } finally {
    button.disabled = false;
    button.textContent = 'Start selected assessment';
    updateFormAvailability();
  }
}

// Header-capable replacement for EventSource: streams the SSE body via fetch so
// the auth token can be sent. Falls back to a status reload on interruption.
async function streamJob(jobId) {
  if (state.streamAbort) state.streamAbort.abort();
  const controller = new AbortController();
  state.streamAbort = controller;
  try {
    const response = await apiFetch(`/api/scans/${jobId}/events`, {
      headers: { Accept: 'text/event-stream' },
      signal: controller.signal,
    });
    if (!response.ok || !response.body) throw new Error('stream unavailable');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const frames = buffer.split('\n\n');
      buffer = frames.pop() || '';
      for (const frame of frames) {
        handleStreamFrame(frame);
      }
    }
  } catch (error) {
    if (controller.signal.aborted) return;
    qs('#form-message').textContent = 'Realtime connection interrupted. Refreshing job status.';
    renderActiveScan({
      status: 'running',
      stage: 'Refreshing',
      message: 'Realtime connection interrupted. Refreshing job status from server.',
      progress: state.currentJob?.progress ?? 0,
    });
    loadJob(jobId);
  }
}

function handleStreamFrame(frame) {
  let eventType = 'message';
  const dataLines = [];
  for (const line of frame.split('\n')) {
    if (line.startsWith('event:')) eventType = line.slice(6).trim();
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim());
  }
  if (!dataLines.length) return;
  let parsed;
  try {
    parsed = JSON.parse(dataLines.join('\n'));
  } catch (error) {
    return;
  }
  if (eventType === 'done') {
    state.currentJob = parsed;
    updateActiveScanFromJob(parsed, parsed.status === 'completed' ? 'Scan completed. Dashboard and report outputs are ready.' : parsed.error || 'Scan failed.');
    if (parsed.status === 'completed') renderDashboard(parsed);
    if (parsed.status === 'failed') qs('#form-message').textContent = parsed.error || 'Scan failed';
    refreshJobs();
    return;
  }
  addEvent(parsed);
}

async function loadJob(jobId) {
  const response = await apiFetch(`/api/scans/${jobId}`);
  if (!response.ok) return;
  const job = await response.json();
  state.currentJob = job;
  qs('#event-list').innerHTML = '';
  updateActiveScanFromJob(job);
  job.events.forEach(addEvent);
  if (job.status === 'completed') {
    renderDashboard(job);
    updateActiveScanFromJob(job, 'Scan completed. Dashboard and report outputs are ready.');
  }
  if (job.status === 'failed') updateActiveScanFromJob(job, job.error || 'Scan failed.');
  if (!['completed', 'failed'].includes(job.status)) streamJob(job.id);
}

// ----- Completed dashboard ----------------------------------------------------

function findingPolicyStatus(finding) {
  if (finding.manual_review_required || finding.manual_review_reason) return 'manual_review';
  if (finding.policy_status || finding.status) return normalise(finding.policy_status || finding.status);
  const severity = normalise(finding.severity);
  if (severity === 'critical' || severity === 'high') return 'fail';
  if (severity === 'medium') return 'warn';
  return 'pass';
}

function filteredFindings() {
  return state.currentFindings.filter((finding) => {
    const severity = normalise(finding.severity || 'info');
    if (state.filters.findingSeverity !== 'all' && severity !== state.filters.findingSeverity) return false;
    if (state.filters.findingPolicy !== 'all' && findingPolicyStatus(finding) !== state.filters.findingPolicy) return false;
    return true;
  });
}

function renderDashboard(job) {
  const summary = job.summary || {};
  const profile = state.config.profiles[job.profile] || {};
  state.currentSummary = { ...summary, target: summary.target || job.target, profile: summary.profile || job.profile };
  state.currentFindings = Array.isArray(summary.findings) ? summary.findings : [];
  qs('#empty-state').classList.add('hidden');
  qs('#dashboard').classList.remove('hidden');
  qs('#summary-target').textContent = state.currentSummary.target;
  qs('#summary-profile').textContent = profileDisplayName(state.currentSummary.profile, profile);
  qs('#summary-category').textContent = profileCategory(profile, job.profile);
  qs('#summary-findings').textContent = summary.finding_count ?? state.currentFindings.length;
  qs('#summary-severity').textContent = summary.highest_severity || 'info';
  qs('#summary-policy').textContent = summary.policy_status || 'pass';
  renderSeverity(summary.severity_counts || {});
  renderPolicies(summary.policy_results || []);
  renderTopRisks();
  renderFindings();
  renderArtifacts(job);
}

function renderSeverity(counts) {
  const max = Math.max(1, ...Object.values(counts).map(Number));
  qs('#severity-bars').innerHTML = Object.entries(counts).map(([severity, count]) => `
    <div class="bar-row">
      <span>${badge(severity)}</span>
      <div class="bar-track"><div class="bar-fill" style="width: ${(Number(count) / max) * 100}%"></div></div>
      <strong>${count}</strong>
    </div>
  `).join('') || '<p>No severity data.</p>';
}

function renderPolicies(policies) {
  qs('#policy-list').innerHTML = policies.map((policy) => `
    <article class="policy-item">
      <strong>${badge(policy.status)} ${escapeHtml(policy.policy_id)}</strong>
      <p>${escapeHtml(policy.message || '')}</p>
    </article>
  `).join('') || '<p>No policy results.</p>';
}

function findingSortScore(finding) {
  const severity = normalise(finding.severity || 'info');
  const index = SEVERITY_ORDER.indexOf(severity);
  return index === -1 ? SEVERITY_ORDER.length : index;
}

function renderTopRisks() {
  const risks = [...state.currentFindings]
    .sort((left, right) => findingSortScore(left) - findingSortScore(right))
    .slice(0, 3);
  qs('#top-risks-list').innerHTML = risks.map((finding, index) => `
    <article class="top-risk-item">
      <span>${index + 1}</span>
      <div>
        <strong>${escapeHtml(finding.title || 'Untitled finding')}</strong>
        <p>${badge(finding.severity)} ${escapeHtml(finding.owasp_id || finding.genai_id || finding.agentic_id || 'mapped finding')}</p>
      </div>
    </article>
  `).join('') || '<div class="empty-state compact-empty">No risks to prioritise.</div>';
}

function renderFindings() {
  const findings = filteredFindings();
  qs('#findings-count').textContent = `Showing ${findings.length} of ${state.currentFindings.length} finding${state.currentFindings.length === 1 ? '' : 's'}`;
  qs('#findings-list').innerHTML = findings.map((finding, index) => {
    const mapping = finding.owasp_id || finding.genai_id || finding.agentic_id || 'framework mapping unavailable';
    const confidence = finding.confidence || finding.confidence_score || finding.score;
    const evidence = finding.evidence || finding.evidence_preview || finding.metadata || null;
    const evidenceText = evidence ? JSON.stringify(evidence, null, 2) : 'No evidence preview included in this summary.';
    return `
      <article class="finding-item enhanced-finding">
        <div class="finding-heading">
          <strong>${index + 1}. ${escapeHtml(finding.title || 'Untitled finding')}</strong>
          <span>${badge(finding.severity)} ${badge(findingPolicyStatus(finding))}</span>
        </div>
        <dl class="finding-meta">
          <div><dt>Mapping</dt><dd>${escapeHtml(mapping)}</dd></div>
          <div><dt>Component</dt><dd>${escapeHtml(finding.affected_component || 'Not specified')}</dd></div>
          <div><dt>Confidence</dt><dd>${escapeHtml(confidence ?? 'Not provided')}</dd></div>
          <div><dt>Review</dt><dd>${findingPolicyStatus(finding) === 'manual_review' ? 'Manual review required' : 'Review recommended'}</dd></div>
        </dl>
        <p>${escapeHtml(finding.recommendation || 'Review the finding evidence and confirm remediation with the system owner.')}</p>
        <details>
          <summary>Evidence preview</summary>
          <pre>${escapeHtml(evidenceText)}</pre>
        </details>
      </article>
    `;
  }).join('') || '<p>No findings match the current filters.</p>';
}

function renderArtifacts(job) {
  const labels = {
    markdown: 'Markdown report',
    json: 'JSON report',
    sarif: 'SARIF report',
    dashboard_markdown: 'Markdown dashboard',
    dashboard_html: 'HTML dashboard',
  };
  const groups = {
    Report: ['markdown'],
    'Machine-readable': ['json', 'sarif'],
    Dashboard: ['dashboard_markdown', 'dashboard_html'],
  };
  const outputs = job.outputs || {};
  qs('#artifact-links').innerHTML = Object.entries(groups).map(([group, names]) => {
    const links = names.filter((name) => Object.prototype.hasOwnProperty.call(outputs, name)).map((name) => `
      <a href="/api/scans/${escapeHtml(job.id)}/artifact/${escapeHtml(name)}" target="_blank" rel="noreferrer">${escapeHtml(labels[name] || name)}</a>
    `).join('');
    if (!links) return '';
    return `<section class="artifact-group"><h4>${escapeHtml(group)}</h4>${links}</section>`;
  }).join('') || '<p>No report artifacts available.</p>';
}

function dashboardSummaryText() {
  const summary = state.currentSummary || {};
  const profile = state.config.profiles?.[summary.profile] || {};
  const findings = state.currentFindings;
  const topRisks = [...findings]
    .sort((left, right) => findingSortScore(left) - findingSortScore(right))
    .slice(0, 3)
    .map((finding) => `- ${finding.severity || 'info'}: ${finding.title || 'Untitled finding'}`)
    .join('\n') || '- No findings reported';
  return [
    'VulnoraIQ assessment summary',
    `Target: ${summary.target || '-'}`,
    `Test option: ${summary.profile ? profileDisplayName(summary.profile, profile) : '-'}`,
    `Findings: ${summary.finding_count ?? findings.length}`,
    `Highest severity: ${summary.highest_severity || 'info'}`,
    `Policy status: ${summary.policy_status || 'pass'}`,
    'Top risks:',
    topRisks,
  ].join('\n');
}

async function copyDashboardSummary() {
  const message = qs('#copy-summary-message');
  const text = dashboardSummaryText();
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      message.textContent = 'Summary copied to clipboard.';
      return;
    }
  } catch (error) {
    /* fall through to textarea fallback */
  }
  const textarea = document.createElement('textarea');
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  textarea.remove();
  message.textContent = 'Summary copied to clipboard.';
}

// ----- Boot -------------------------------------------------------------------

function attachUiListeners() {
  qs('#scan-form').addEventListener('submit', startScan);
  qs('#profile-select').addEventListener('change', renderSelectedProfile);
  qs('#target-select').addEventListener('change', renderSelectedProfile);
  qs('#authorised').addEventListener('change', renderRunReadiness);
  qs('#select-full-profile').addEventListener('click', () => {
    qs('#profile-select').value = 'full';
    renderSelectedProfile();
  });
  qs('#catalog-search').addEventListener('input', (event) => {
    state.filters.catalogSearch = normalise(event.target.value);
    renderTestCatalog();
  });
  qs('#catalog-category-filter').addEventListener('change', (event) => {
    state.filters.catalogCategory = event.target.value;
    renderTestCatalog();
  });
  qs('#catalog-mode-filter').addEventListener('change', (event) => {
    state.filters.catalogMode = event.target.value;
    renderTestCatalog();
  });
  qs('#history-search').addEventListener('input', (event) => {
    state.filters.historySearch = normalise(event.target.value);
    renderJobHistory();
  });
  qs('#history-status-filter').addEventListener('change', (event) => {
    state.filters.historyStatus = event.target.value;
    renderJobHistory();
  });
  qs('#finding-severity-filter').addEventListener('change', (event) => {
    state.filters.findingSeverity = event.target.value;
    renderFindings();
  });
  qs('#finding-policy-filter').addEventListener('change', (event) => {
    state.filters.findingPolicy = event.target.value;
    renderFindings();
  });
  qs('#copy-summary').addEventListener('click', copyDashboardSummary);
}

async function bootstrapData() {
  updateFormAvailability();
  if (state.session.auth_enabled && !state.session.authenticated) {
    clearWorkspace();
    return;
  }
  await loadConfig();
  await refreshJobs();
}

async function init() {
  attachUiListeners();
  setProgress(0, 'Idle');
  renderActiveScan({ status: 'idle', stage: 'Idle', message: 'Waiting for a scan to start.', progress: 0 });
  renderRunReadiness();
  await loadSession();
  await bootstrapData();
}

init().catch((error) => {
  qs('#form-message').textContent = error.message;
});
