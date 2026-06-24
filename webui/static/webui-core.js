window.VulnoraIQWebUI = window.VulnoraIQWebUI || {};

(function registerCore(namespace) {
  function qs(selector, root = document) {
    return root.querySelector(selector);
  }

  function qsa(selector, root = document) {
    return Array.from(root.querySelectorAll(selector));
  }

  function debounce(fn, delay = 180) {
    let timer = null;
    return (...args) => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => fn(...args), delay);
    };
  }

  function createStore(initialState = {}) {
    let state = { ...initialState };
    const subscribers = new Set();
    return {
      get state() {
        return state;
      },
      setState(nextState) {
        const previous = state;
        state = { ...state, ...nextState };
        subscribers.forEach((subscriber) => subscriber(state, previous));
      },
      subscribe(subscriber) {
        subscribers.add(subscriber);
        return () => subscribers.delete(subscriber);
      },
    };
  }

  function normalizeApiError(error, fallback = 'Unexpected WebUI error') {
    if (!error) return { ok: false, status: 0, message: fallback, details: {} };
    if (typeof error === 'string') return { ok: false, status: 0, message: error, details: {} };
    return {
      ok: false,
      status: Number(error.status || 0),
      message: String(error.message || fallback),
      details: error.details || {},
    };
  }

  function announce(message, politeness = 'polite') {
    let region = qs('#webui-announcer');
    if (!region) {
      region = document.createElement('div');
      region.id = 'webui-announcer';
      region.className = 'sr-only';
      region.setAttribute('aria-live', politeness);
      region.setAttribute('aria-atomic', 'true');
      document.body.appendChild(region);
    }
    region.setAttribute('aria-live', politeness);
    region.textContent = '';
    window.setTimeout(() => {
      region.textContent = message;
    }, 20);
  }

  function setBusy(target, busy) {
    const element = typeof target === 'string' ? qs(target) : target;
    if (element) element.setAttribute('aria-busy', busy ? 'true' : 'false');
  }

  function safeStorage(storage) {
    return {
      get(key) {
        try {
          return storage?.getItem(key) || '';
        } catch (error) {
          return '';
        }
      },
      set(key, value) {
        try {
          if (value) storage?.setItem(key, value);
          else storage?.removeItem(key);
        } catch (error) {
          /* storage unavailable */
        }
      },
    };
  }

  function tokenStorage(strategy = 'session') {
    if (strategy === 'local') return safeStorage(window.localStorage);
    if (strategy === 'memory') {
      const memory = new Map();
      return {
        get(key) {
          return memory.get(key) || '';
        },
        set(key, value) {
          if (value) memory.set(key, value);
          else memory.delete(key);
        },
      };
    }
    return safeStorage(window.sessionStorage);
  }

  namespace.core = {
    qs,
    qsa,
    debounce,
    createStore,
    normalizeApiError,
    announce,
    setBusy,
    tokenStorage,
  };
})(window.VulnoraIQWebUI);
