const THEME_STORAGE_KEY = 'vulnoraiq.theme';
const ENHANCED_START_LABEL = 'Start selected assessment';

function webuiEnhancementQs(selector) {
  return document.querySelector(selector);
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

function mirrorInlineFormMessage() {
  const message = webuiEnhancementQs('#form-message');
  if (!message) return;
  const observer = new MutationObserver(() => {
    const text = message.textContent.trim();
    if (!text) {
      setGlobalStatus('', 'info');
      return;
    }
    const kind = /fail|error|interrupted|required|permission|forbidden|invalid|unable/i.test(text) ? 'error' : 'info';
    setGlobalStatus(text, kind);
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

function initWebUiEnhancements() {
  applyTheme(preferredTheme());
  webuiEnhancementQs('#theme-toggle')?.addEventListener('click', toggleTheme);
  mirrorInlineFormMessage();
  enhanceStartButtonState();
  enhanceProgressBarA11y();
  enhanceCopyFeedback();
  markLoadedContainers();
}

initWebUiEnhancements();
