const state = {
  config: { targets: {}, profiles: {} },
  currentJob: null,
  eventSource: null,
};

const qs = (selector) => document.querySelector(selector);

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
  li.innerHTML = `<strong>${event.stage}</strong><div>${event.message}</div><small>${new Date(event.timestamp).toLocaleString()} · ${event.progress}%</small>`;
  qs('#event-list').prepend(li);
  setProgress(event.progress, event.stage);
}

function badge(value) {
  const normalised = String(value || 'unknown').toLowerCase();
  return `<span class="badge ${normalised}">${normalised}</span>`;
}

async function loadConfig() {
  const response = await fetch('/api/config');
  state.config = await response.json();
  const targetSelect = qs('#target-select');
  const profileSelect = qs('#profile-select');
  targetSelect.innerHTML = Object.entries(state.config.targets)
    .map(([name, target]) => `<option value="${name}">${name} · ${target.type || 'target'}</option>`)
    .join('');
  profileSelect.innerHTML = Object.entries(state.config.profiles)
    .map(([name, profile]) => `<option value="${name}">${name} · ${(profile.modules || []).length} modules</option>`)
    .join('');
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
        <strong>${job.target} / ${job.profile}</strong><br>
        <small>${job.status} · ${job.progress}% · ${new Date(job.created_at).toLocaleString()}</small>
      </div>
      <button type="button" data-job-id="${job.id}">View</button>
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
    button.textContent = 'Start assessment';
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
  qs('#empty-state').classList.add('hidden');
  qs('#dashboard').classList.remove('hidden');
  qs('#summary-target').textContent = summary.target || job.target;
  qs('#summary-profile').textContent = summary.profile || job.profile;
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
      <strong>${badge(policy.status)} ${policy.policy_id}</strong>
      <p>${policy.message || ''}</p>
    </article>
  `).join('') || '<p>No policy results.</p>';
}

function renderFindings(findings) {
  qs('#findings-list').innerHTML = findings.map((finding, index) => `
    <article class="finding-item">
      <strong>${index + 1}. ${finding.title}</strong>
      <p>${badge(finding.severity)} ${finding.owasp_id} · ${finding.affected_component}</p>
      <p>${finding.recommendation || ''}</p>
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
    <a href="/api/scans/${job.id}/artifact/${name}" target="_blank" rel="noreferrer">${labels[name] || name}</a>
  `).join('');
}

async function init() {
  await loadConfig();
  await refreshJobs();
  qs('#scan-form').addEventListener('submit', startScan);
  setProgress(0, 'Idle');
}

init().catch((error) => {
  qs('#form-message').textContent = error.message;
});
