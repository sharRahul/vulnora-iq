const THEME_STORAGE_KEY = 'vulnoraiq.theme';
const ENHANCED_START_LABEL = 'Start selected assessment';
const INTERACTION_DEBOUNCE_MS = 220;

const progressRuntime = {
  startedAt: null,
  lastProgress: 0,
  timer: null,
};

function webuiEnhancementQs(selector) {
  return document.querySelector(selector);
}

function enhancementNormalise(value) {
  return String(value || '').trim().toLowerCase();
}

function enhancementDebounce(fn, delay = INTERACTION_DEBOUNCE_MS) {
  let timer = null;
  return (...args) => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), delay);
  };
}

function preferredTheme() {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
  } catch (error) {
    /* localStorage may be unavailable in locked-down browsers */
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const toggle = webuiEnhancementQs('#theme-toggle');
  if (!toggle) return;
  const dark = theme === 'dark';
  toggle.setAttribute('aria-pressed', dark ? 'true' : 'false');
  toggle.textContent = dark ? 'Light mode' : 'Dark mode';
}

function toggleTheme() {
  const current = document.documentElement.dataset.theme || preferredTheme();
  const next = current === 'dark' ? 'light' : 'dark';
  try {
    localStorage.setItem(THEME_STORAGE_KEY, next);
  } catch (error) {
    /* preference simply will not persist */
  }
  applyTheme(next);
  showToast(next === 'dark' ? 'Dark mode enabled' : 'Light mode enabled');
}

function showToast(message) {
  const region = webuiEnhancementQs('#toast-region');
  if (!region) return;
  const toast = document.createElement('div');
  toast.className = 'toast-message';
  toast.textContent = message;
  region.appendChild(toast);
  window.setTimeout(() => {
    toast.classList.add('toast-message-out');
    window.setTimeout(() => toast.remove(), 220);
  }, 1800);
}

function setGlobalStatus(message, kind = 'info') {
  const banner = webuiEnhancementQs('#global-status');
  if (!banner) return;
  banner.className = `status-banner ${kind}`;
  banner.textContent = message;
  banner.classList.toggle('hidden', !message);
}

function ensureRetryActions() {
  let actions = webuiEnhancementQs('#retry-actions');
  if (actions) return actions;
  const banner = webuiEnhancementQs('#global-status');
  if (!banner) return null;
  actions = document.createElement('div');
  actions.id = 'retry-actions';
  actions.className = 'retry-actions hidden';
  banner.insertAdjacentElement('afterend', actions);
  return actions;
}

function clearRetryActions() {
  const actions = ensureRetryActions();
  if (!actions) return;
  actions.classList.add('hidden');
  actions.replaceChildren();
}

function retryActionForMessage(message) {
  const text = enhancementNormalise(message);
  if (!text) return null;
  if (text.includes('interrupted') || text.includes('refreshing job status')) {
    return {
      label: 'Retry live refresh',
      run: () => {
        const jobId = state?.currentJob?.id;
        if (jobId && typeof loadJob === 'function') loadJob(jobId);
        else if (typeof refreshJobs === 'function') refreshJobs();
      },
    };
  }
  if (text.includes('unable to start') || text.includes('failed to start')) {
    return {
      label: 'Retry start',
      run: () => webuiEnhancementQs('#scan-form')?.requestSubmit(),
    };
  }
  if (text.includes('authentication') || text.includes('permission')) return null;
  return {
    label: 'Retry loading data',
    run: () => {
      if (typeof bootstrapData === 'function') bootstrapData();
      else if (typeof refreshJobs === 'function') refreshJobs();
    },
  };
}

function updateRetryActions(messageText) {
  const actions = ensureRetryActions();
  if (!actions) return;
  const action = retryActionForMessage(messageText);
  if (!action) {
    clearRetryActions();
    return;
  }
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'secondary compact';
  button.textContent = action.label;
  button.addEventListener('click', async () => {
    try {
      actions.classList.add('is-loading');
      button.disabled = true;
      await action.run();
      showToast('Retry requested');
    } finally {
      actions.classList.remove('is-loading');
      button.disabled = false;
    }
  });
  actions.replaceChildren(button);
  actions.classList.remove('hidden');
}

function mirrorInlineFormMessage() {
  const message = webuiEnhancementQs('#form-message');
  if (!message) return;
  const observer = new MutationObserver(() => {
    const text = message.textContent.trim();
    if (!text) {
      setGlobalStatus('', 'info');
      clearRetryActions();
      return;
    }
    const kind = /fail|error|interrupted|required|permission|forbidden|invalid|unable/i.test(text) ? 'error' : 'info';
    setGlobalStatus(text, kind);
    updateRetryActions(text);
  });
  observer.observe(message, { childList: true, subtree: true, characterData: true });
}

function enhanceStartButtonState() {
  const button = webuiEnhancementQs('#start-scan');
  if (!button) return;
  const update = () => {
    const busy = button.disabled && /starting/i.test(button.textContent || '');
    button.classList.toggle('is-loading', busy);
    button.setAttribute('aria-busy', busy ? 'true' : 'false');
    if (!busy && !button.textContent.trim()) button.textContent = ENHANCED_START_LABEL;
  };
  new MutationObserver(update).observe(button, { attributes: true, childList: true, subtree: true });
  update();
}

function enhanceProgressBarA11y() {
  const progressBar = webuiEnhancementQs('.progress-bar-shell');
  const value = webuiEnhancementQs('#progress-value');
  if (!progressBar || !value) return;
  const observer = new MutationObserver(() => {
    const numeric = Number((value.textContent || '0').replace('%', '')) || 0;
    progressBar.setAttribute('aria-valuenow', String(Math.max(0, Math.min(100, numeric))));
  });
  observer.observe(value, { childList: true, characterData: true, subtree: true });
}

function formatDuration(ms) {
  if (!Number.isFinite(ms) || ms <= 0) return '-';
  const totalSeconds = Math.max(1, Math.round(ms / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  }
  return `${minutes}m ${String(seconds).padStart(2, '0')}s`;
}

function ensureRuntimeMetricCards() {
  const grid = webuiEnhancementQs('.scan-stage-grid');
  if (!grid) return;
  if (!webuiEnhancementQs('#active-scan-elapsed')) {
    grid.insertAdjacentHTML('beforeend', '<article><span>Elapsed</span><strong id="active-scan-elapsed">-</strong></article>');
  }
  if (!webuiEnhancementQs('#active-scan-eta')) {
    grid.insertAdjacentHTML('beforeend', '<article><span>ETA</span><strong id="active-scan-eta">-</strong></article>');
  }
}

function currentProgressPercent() {
  return Number((webuiEnhancementQs('#progress-value')?.textContent || '0').replace('%', '')) || 0;
}

function scanIsRunning() {
  const card = webuiEnhancementQs('#active-scan-card');
  if (!card) return false;
  return card.classList.contains('running') || card.classList.contains('queued');
}

function resetRuntimeMetrics() {
  progressRuntime.startedAt = null;
  progressRuntime.lastProgress = 0;
  const elapsed = webuiEnhancementQs('#active-scan-elapsed');
  const eta = webuiEnhancementQs('#active-scan-eta');
  if (elapsed) elapsed.textContent = '-';
  if (eta) eta.textContent = '-';
}

function updateRuntimeMetrics() {
  ensureRuntimeMetricCards();
  const progress = currentProgressPercent();
  const running = scanIsRunning();
  if (!running || progress >= 100) {
    if (progress >= 100 && progressRuntime.startedAt) {
      const elapsed = webuiEnhancementQs('#active-scan-elapsed');
      const eta = webuiEnhancementQs('#active-scan-eta');
      if (elapsed) elapsed.textContent = formatDuration(Date.now() - progressRuntime.startedAt);
      if (eta) eta.textContent = 'Complete';
      return;
    }
    resetRuntimeMetrics();
    return;
  }
  if (!progressRuntime.startedAt) progressRuntime.startedAt = Date.now();
  progressRuntime.lastProgress = progress;
  const elapsedMs = Date.now() - progressRuntime.startedAt;
  const elapsed = webuiEnhancementQs('#active-scan-elapsed');
  const eta = webuiEnhancementQs('#active-scan-eta');
  if (elapsed) elapsed.textContent = formatDuration(elapsedMs);
  if (eta) {
    eta.textContent = progress > 0 && progress < 100
      ? formatDuration((elapsedMs / progress) * (100 - progress))
      : 'Calculating';
  }
}

function enhanceRuntimeMetrics() {
  ensureRuntimeMetricCards();
  const progressValue = webuiEnhancementQs('#progress-value');
  const activeCard = webuiEnhancementQs('#active-scan-card');
  if (progressValue) new MutationObserver(updateRuntimeMetrics).observe(progressValue, { childList: true, characterData: true, subtree: true });
  if (activeCard) new MutationObserver(updateRuntimeMetrics).observe(activeCard, { attributes: true, attributeFilter: ['class'] });
  window.clearInterval(progressRuntime.timer);
  progressRuntime.timer = window.setInterval(updateRuntimeMetrics, 1000);
  updateRuntimeMetrics();
}

function enhanceCopyFeedback() {
  const button = webuiEnhancementQs('#copy-summary');
  if (!button) return;
  button.addEventListener('click', () => {
    window.setTimeout(() => showToast('Copied to clipboard'), 50);
  });
}

function markLoadedContainers() {
  for (const selector of ['#test-catalog', '#job-history', '#startup-check-list', '#startup-action-list', '#startup-config-list']) {
    const element = webuiEnhancementQs(selector);
    if (!element) continue;
    const observer = new MutationObserver(() => {
      if (element.children.length || element.textContent.trim()) element.setAttribute('aria-busy', 'false');
    });
    observer.observe(element, { childList: true, subtree: true, characterData: true });
  }
}

function installDebouncedFilter(inputSelector, busySelector, updateFilter, render) {
  const input = webuiEnhancementQs(inputSelector);
  const busy = webuiEnhancementQs(busySelector);
  if (!input || typeof updateFilter !== 'function' || typeof render !== 'function') return;
  const run = enhancementDebounce((value) => {
    updateFilter(value);
    render();
    busy?.setAttribute('aria-busy', 'false');
  });
  input.addEventListener('input', (event) => {
    event.stopImmediatePropagation();
    busy?.setAttribute('aria-busy', 'true');
    run(event.target.value);
  }, { capture: true });
}

function enhanceDebouncedFilters() {
  installDebouncedFilter('#catalog-search', '#test-catalog', (value) => {
    state.filters.catalogSearch = enhancementNormalise(value);
  }, renderTestCatalog);
  installDebouncedFilter('#history-search', '#job-history', (value) => {
    state.filters.historySearch = enhancementNormalise(value);
  }, renderJobHistory);
}

function initWebUiEnhancements() {
  applyTheme(preferredTheme());
  webuiEnhancementQs('#theme-toggle')?.addEventListener('click', toggleTheme);
  mirrorInlineFormMessage();
  enhanceStartButtonState();
  enhanceProgressBarA11y();
  enhanceRuntimeMetrics();
  enhanceDebouncedFilters();
  enhanceCopyFeedback();
  markLoadedContainers();
}

initWebUiEnhancements();
