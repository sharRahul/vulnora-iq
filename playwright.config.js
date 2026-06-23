const { defineConfig, devices } = require('@playwright/test');

const port = process.env.VULNORAIQ_TEST_PORT || '8787';

module.exports = defineConfig({
  testDir: './tests/webui',
  timeout: 60_000,
  expect: { timeout: 15_000 },
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: `python scripts/webui_test_server.py --host 127.0.0.1 --port ${port} --skip-production-checks`,
    url: `http://127.0.0.1:${port}/healthz`,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
    env: {
      ...process.env,
      VULNORAIQ_AUTH_ENABLED: 'false',
      VULNORAIQ_WEB_OUTPUT_ROOT: 'reports/output/webui-playwright',
      VULNORAIQ_JOB_STORE_PATH: 'reports/output/webui-playwright/jobs.db',
    },
  },
});
