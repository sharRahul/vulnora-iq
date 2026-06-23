(() => {
  const TOKEN_STORAGE_KEY = 'vulnoraiq.token';
  const qs = (selector) => document.querySelector(selector);

  function escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function bootstrapTokenFromUrl() {
    const url = new URL(window.location.href);
    const token = url.searchParams.get('token');
    if (!token) return;
    try {
      sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
    } catch (error) {
      /* Ignore storage failures; normal sign-in still works. */
    }
    url.searchParams.delete('token');
    if (url.searchParams.get('launcher') === '1') url.searchParams.delete('launcher');
    window.history.replaceState({}, document.title, `${url.pathname}${url.search}${url.hash}`);
  }

  function authHeaders(extra = {}) {
    const headers = { ...extra };
    try {
      const token = sessionStorage.getItem(TOKEN_STORAGE_KEY) || '';
      if (token) headers['X-VulnoraIQ-Token'] = token;
    } catch (error) {
      /* No persisted token available. */
    }
    return headers;
  }

  function setStartupState(status, title, message) {
    const badge = qs('#startup-status-badge');
    qs('#startup-status-title').textContent = title;
    qs('#startup-status-message').textContent = message;
    badge.textContent = status.replaceAll('_', ' ');
    badge.className = `startup-badge ${status}`;
  }

  function renderList(selector, items, emptyMessage) {
    const container = qs(selector);
    if (!items || !items.length) {
      container.innerHTML = `<div class="startup-item"><p>${escapeHtml(emptyMessage)}</p></div>`;
      return;
    }
    container.innerHTML = items.map((item) => `
      <article class="startup-item">
        <strong>
          ${escapeHtml(item.name || item.key || 'Check')}
          <span class="startup-pill ${escapeHtml(item.status || 'pending')}">${escapeHtml(item.status || 'pending')}</span>
        </strong>
        <p>${escapeHtml(item.detail || item.value || '')}</p>
      </article>
    `).join('');
  }

  function renderStartupStatus(data) {
    const status = data.status || 'warning';
    const title = status === 'ready' ? 'Ready for local assessment' : 'Startup checks need attention';
    const message = data.message || 'Review startup checks before running scans.';
    setStartupState(status, title, message);
    renderList('#startup-check-list', data.dependency_checks, 'No dependency checks reported.');
    renderList('#startup-action-list', data.quick_start_actions, 'No quick-start actions reported.');
    renderList('#startup-config-list', data.change_options, 'No configuration options reported.');
    const stopButton = qs('#stop-server');
    stopButton.disabled = !data.shutdown_allowed;
    qs('#stop-server-message').textContent = data.shutdown_allowed
      ? 'Local launcher mode is active. Use this button to stop the server cleanly.'
      : 'Stop is unavailable unless the local launcher enabled it and your session has admin runtime permission.';
  }

  async function refreshStartupStatus() {
    setStartupState('pending', 'Checking startup state', 'Contacting the local Web UI launcher.');
    try {
      const response = await fetch('/api/startup', { headers: authHeaders() });
      if (response.status === 401) {
        setStartupState('blocked', 'Sign in required', 'Enter the access token or launch from the double-click startup file to view checks.');
        renderList('#startup-check-list', [], 'Sign in to see checks.');
        renderList('#startup-action-list', [], 'Sign in to see actions.');
        renderList('#startup-config-list', [], 'Sign in to see options.');
        qs('#stop-server').disabled = true;
        return;
      }
      if (response.status === 404) {
        setStartupState('unavailable', 'Standard server mode', 'Startup controls are available when the Web UI is opened through the local launcher.');
        renderList('#startup-check-list', [], 'This server was not started by the local launcher.');
        renderList('#startup-action-list', [], 'Use launch-vulnoraiq-webui.bat, .command, or .sh to enable quick-start checks.');
        renderList('#startup-config-list', [], 'Use normal environment variables or CLI flags for this server mode.');
        qs('#stop-server').disabled = true;
        return;
      }
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to load startup checks');
      renderStartupStatus(data);
    } catch (error) {
      setStartupState('blocked', 'Startup check failed', error.message || 'Unable to load startup checks.');
      qs('#stop-server').disabled = true;
    }
  }

  async function getCsrfToken() {
    const response = await fetch('/api/csrf-token', { headers: authHeaders() });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to request CSRF token');
    return data.csrf_token;
  }

  async function stopServer() {
    const message = qs('#stop-server-message');
    const confirmed = window.confirm('Stop the local VulnoraIQ Web UI server now? The browser page will disconnect.');
    if (!confirmed) return;
    qs('#stop-server').disabled = true;
    message.textContent = 'Stopping local server...';
    try {
      const csrfToken = await getCsrfToken();
      const response = await fetch('/api/server/shutdown', {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken }),
        body: JSON.stringify({ confirm: true }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to stop server');
      setStartupState('stopping', 'Server stopping', data.message || 'The local server is shutting down.');
      message.textContent = 'Server stop requested successfully. You can close this browser tab.';
    } catch (error) {
      message.textContent = error.message || 'Unable to stop server.';
      qs('#stop-server').disabled = false;
    }
  }

  bootstrapTokenFromUrl();

  document.addEventListener('DOMContentLoaded', () => {
    const refreshButton = qs('#startup-refresh');
    const stopButton = qs('#stop-server');
    if (refreshButton) refreshButton.addEventListener('click', refreshStartupStatus);
    if (stopButton) stopButton.addEventListener('click', stopServer);
    refreshStartupStatus();
  });
})();
