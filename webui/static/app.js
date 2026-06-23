const state = {
  config: { targets: {}, profiles: {} },
  session: { auth_enabled: false, authenticated: false, auth_required: false, permissions: [] },
  tokenHeader: 'X-VulnoraIQ-Token',
  currentJob: null,
  streamAbort: null,
  csrfToken: null,
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

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
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
  qs('#event-list').innerHTML = '';
  setProgress(0, 'Idle');
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

// ----- Progress + rendering ---------------------------------------------------

function setProgress(value, status) {
  const safe = Math.max(0, Math.min(100, Number(value || 0)));
  const circumference = 326.7;
  qs('#progress-circle').style.strokeDashoffset = String(circumference - (safe / 100) * circumference);
  qs('#progress-value').textContent = `${safe}%`;
  qs('#scan-status').textContent = status || 'Idle';
}

function addEvent(event) {
  const li = document.createElement('li');
  li.className = event.level === 'error' ? 'error' : '';
  li.innerHTML = `<strong>${escapeHtml(event.stage)}</strong><div>${escapeHtml(event.message)}</div><small>${new Date(event.timestamp).toLocaleString()} · ${event.progress}%</small>`;
  qs('#event-list').prepend(li);
  setProgress(event.progress, event.stage);
}

function badge(value) {
  const normalised = String(value || 'unknown').toLowerCase();
  return `<span class="badge ${escapeHtml(normalised)}">${escapeHtml(normalised)}</span>`;
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

function orderedCategories(groups) {
  const known = CATEGORY_ORDER.filter((category) => groups.has(category));
  const extra = [...groups.keys()].filter((category) => !CATEGORY_ORDER.includes(category)).sort();
  return [...known, ...extra];
}

function renderProfileSelect() {
  const profileSelect = qs('#profile-select');
  const groups = new Map();
  Object.entries(state.config.profiles || {}).forEach(([name, profile]) => {
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

function renderSelectedProfile() {
  const selected = qs('#profile-select').value;
  const profile = state.config.profiles[selected] || {};
  const modules = profileModules(profile);
  qs('#selected-profile-detail').innerHTML = `
    <strong>${escapeHtml(profileDisplayName(selected, profile))}</strong>
    <p>${escapeHtml(profile.description || 'No description available.')}</p>
    <small>${escapeHtml(profileCategory(profile, selected))} · ${modules.length || 'configured'} module${modules.length === 1 ? '' : 's'} selected</small>
  `;
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
  Object.entries(state.config.profiles || {}).forEach(([name, profile]) => {
    const category = profileCategory(profile, name);
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push([name, profile]);
  });

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
  renderTestCatalog();
}

async function refreshJobs() {
  const response = await apiFetch('/api/scans');
  const data = await response.json();
  const container = qs('#job-history');
  if (!data.jobs.length) {
    container.innerHTML = '<div class="empty-state">No scan history yet.</div>';
    return;
  }
  container.innerHTML = data.jobs.map((job) => `
    <div class="job-item">
      <div>
        <strong>${escapeHtml(job.target)} / ${escapeHtml(profileDisplayName(job.profile, state.config.profiles[job.profile] || {}))}</strong><br>
        <small>${escapeHtml(job.status)} · ${job.progress}% · ${new Date(job.created_at).toLocaleString()}</small>
      </div>
      <button type="button" data-job-id="${escapeHtml(job.id)}">View</button>
    </div>
  `).join('');
  container.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => loadJob(button.dataset.jobId));
  });
}

async function startScan(event) {
  event.preventDefault();
  qs('#form-message').textContent = '';
  qs('#event-list').innerHTML = '';
  setProgress(0, 'Queued');
  const payload = {
    target: qs('#target-select').value,
    profile: qs('#profile-select').value,
    authorised: qs('#authorised').checked,
  };
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
    streamJob(data.id);
    await refreshJobs();
  } catch (error) {
    qs('#form-message').textContent = error.message;
    setProgress(0, 'Failed to start');
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
  job.events.forEach(addEvent);
  if (job.status === 'completed') renderDashboard(job);
  if (!['completed', 'failed'].includes(job.status)) streamJob(job.id);
}

function renderDashboard(job) {
  const summary = job.summary || {};
  const profile = state.config.profiles[job.profile] || {};
  qs('#empty-state').classList.add('hidden');
  qs('#dashboard').classList.remove('hidden');
  qs('#summary-target').textContent = summary.target || job.target;
  qs('#summary-profile').textContent = profileDisplayName(summary.profile || job.profile, profile);
  qs('#summary-category').textContent = profileCategory(profile, job.profile);
  qs('#summary-findings').textContent = summary.finding_count ?? 0;
  qs('#summary-severity').textContent = summary.highest_severity || 'info';
  qs('#summary-policy').textContent = summary.policy_status || 'pass';
  renderSeverity(summary.severity_counts || {});
  renderPolicies(summary.policy_results || []);
  renderFindings(summary.findings || []);
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

function renderFindings(findings) {
  qs('#findings-list').innerHTML = findings.map((finding, index) => `
    <article class="finding-item">
      <strong>${index + 1}. ${escapeHtml(finding.title)}</strong>
      <p>${badge(finding.severity)} ${escapeHtml(finding.owasp_id)} · ${escapeHtml(finding.affected_component)}</p>
      <p>${escapeHtml(finding.recommendation || '')}</p>
    </article>
  `).join('') || '<p>No findings.</p>';
}

function renderArtifacts(job) {
  const labels = {
    markdown: 'Markdown report',
    json: 'JSON report',
    sarif: 'SARIF report',
    dashboard_markdown: 'Markdown dashboard',
    dashboard_html: 'HTML dashboard',
  };
  qs('#artifact-links').innerHTML = Object.keys(job.outputs || {}).map((name) => `
    <a href="/api/scans/${escapeHtml(job.id)}/artifact/${escapeHtml(name)}" target="_blank" rel="noreferrer">${escapeHtml(labels[name] || name)}</a>
  `).join('');
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
  qs('#scan-form').addEventListener('submit', startScan);
  qs('#profile-select').addEventListener('change', renderSelectedProfile);
  qs('#select-full-profile').addEventListener('click', () => {
    qs('#profile-select').value = 'full';
    renderSelectedProfile();
  });
  setProgress(0, 'Idle');
  await loadSession();
  await bootstrapData();
}

init().catch((error) => {
  qs('#form-message').textContent = error.message;
});
