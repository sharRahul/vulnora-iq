const { test, expect } = require('@playwright/test');

async function csrfToken(request) {
  const response = await request.get('/api/csrf-token');
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.csrf_token).toBeTruthy();
  return data.csrf_token;
}

test('hosted server serves the console and creates a demo scan job', async ({ page, request }) => {
  // The hosted server now serves the React SecOps console at /.
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await expect(page).toHaveTitle(/VulnorAIQ/i);
  await expect(page.locator('#root')).toBeAttached();

  const token = await csrfToken(request);
  const response = await request.post('/api/scans', {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': token,
    },
    data: {
      target: 'demo',
      profile: 'baseline',
      authorised: false,
    },
  });

  expect(response.status()).toBe(202);
  const job = await response.json();
  expect(job.id).toBeTruthy();
  expect(job.target).toBe('demo');
  expect(job.profile).toBe('baseline');
  expect(['queued', 'running', 'completed']).toContain(job.status);
});
