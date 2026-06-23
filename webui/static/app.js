const state = {
  config: { targets: {}, profiles: {} },
  currentJob: null,
  eventSource: null,
};

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

function profileCategory(profile) {
  return profile.category || 'Other tests';
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
    const category = profileCategory(profile);
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push([name, profile]);
  });

  profileSelect.innerHTML = orderedCategories(groups).map((category) => {
    const options = groups.get(category)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([name, profile]) => `<option value="${escapeHtml(name)}">${escapeHtml(profileDisplayName(name, profile))} · ${profileModules(profile).length} module${profileModules(profile).length === 1 ? '' : 's'}</option>`)
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
    <small>${escapeHtml(profileCategory(profile))} · ${modules.length} module${modules.length === 1 ? '' : 's'} selected</small>
  `;
  document.querySelectorAll('.profile-card').forEach((card) => {
    card.classList.toggle('active', card.dataset.profile === selected);
  });
}

function renderTestCatalog() {
  const catalog = qs('#test-catalog');
  const groups = new Map();
  Object.entries(state.config.profiles || {}).forEach(([name, profile]) => {
    const category = profileCategory(profile);
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push([name, profile]);
  });

  catalog.innerHTML = orderedCategories(groups).map((category) => {
    const cards = groups.get(category)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([name, profile]) => {
        const modules = profileModules(profile);
        const moduleBadges = modules.map((moduleName) => `<span>${escapeHtml(moduleName)}</span>`).join('');
        return `
          <article class="profile-card" data-profile="${escapeHtml(name)}">
            <div>
              <strong>${escapeHtml(profileDisplayName(name, profile))}</strong>
              <p>${escapeHtml(profile.description || '')}</p>
              <div class="module-list">${moduleBadges}</div>
            </div>
            <button type="button" data-profile-select="${escapeHtml(name)}">Run this option</button>
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
  const response = await fetch('/api/config');
  state.config = await response.json();
  const targetSelect = qs('#target-select');
  targetSelect.innerHTML = Object.entries(state.config.targets || {})
    .map(([name, target]) => `<option value="${escapeHtml(name)}">${escapeHtml(name)} · ${escapeHtml(target.type || 'target')}</option>`)
    .join('');
  renderProfileSelect();
  renderTestCatalog();
}

async function refreshJobs() {
  const response = await fetch('/api/scans');
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
    const response = await fetch('/api/scans', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to start scan');
    state.currentJob = data;
    subscribeToJob(data.id);
    await refreshJobs();
  } catch (error) {
    qs('#form-message').textContent = error.message;
    setProgress(0, 'Failed to start');
  } finally {
    button.disabled = false;
    button.textContent = 'Start selected assessment';
  }
}

function subscribeToJob(jobId) {
  if (state.eventSource) state.eventSource.close();
  state.eventSource = new EventSource(`/api/scans/${jobId}/events`);
  state.eventSource.onmessage = (message) => {
    addEvent(JSON.parse(message.data));
  };
  state.eventSource.addEventListener('done', async (message) => {
    state.eventSource.close();
    const job = JSON.parse(message.data);
    state.currentJob = job;
    if (job.status === 'completed') renderDashboard(job);
    if (job.status === 'failed') qs('#form-message').textContent = job.error || 'Scan failed';
    await refreshJobs();
  });
  state.eventSource.onerror = () => {
    qs('#form-message').textContent = 'Realtime connection interrupted. Refreshing job status.';
    state.eventSource.close();
    loadJob(jobId);
  };
}

async function loadJob(jobId) {
  const response = await fetch(`/api/scans/${jobId}`);
  if (!response.ok) return;
  const job = await response.json();
  state.currentJob = job;
  qs('#event-list').innerHTML = '';
  job.events.forEach(addEvent);
  if (job.status === 'completed') renderDashboard(job);
  if (!['completed', 'failed'].includes(job.status)) subscribeToJob(job.id);
}

function renderDashboard(job) {
  const summary = job.summary || {};
  const profile = state.config.profiles[job.profile] || {};
  qs('#empty-state').classList.add('hidden');
  qs('#dashboard').classList.remove('hidden');
  qs('#summary-target').textContent = summary.target || job.target;
  qs('#summary-profile').textContent = profileDisplayName(summary.profile || job.profile, profile);
  qs('#summary-category').textContent = profileCategory(profile);
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

async function init() {
  await loadConfig();
  await refreshJobs();
  qs('#scan-form').addEventListener('submit', startScan);
  qs('#profile-select').addEventListener('change', renderSelectedProfile);
  qs('#select-full-profile').addEventListener('click', () => {
    qs('#profile-select').value = 'full';
    renderSelectedProfile();
  });
  setProgress(0, 'Idle');
}

init().catch((error) => {
  qs('#form-message').textContent = error.message;
});
