const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/webui',
  testMatch: /smoke.*\.spec\.js/,
  timeout: 30_000,
  expect: { timeout: 10_000 },
  use: {
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
