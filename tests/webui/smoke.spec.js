const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { test, expect } = require('@playwright/test');

test('loads the console shell from static assets', async ({ page }) => {
  const url = pathToFileURL(path.resolve('webui/static/index.html')).href;
  await page.goto(url);
  await expect(page.getByRole('heading', { name: 'VulnoraIQ', exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Choose tests and run scan' })).toBeVisible();
});
