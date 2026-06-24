const { test, expect } = require('@playwright/test');

async function selectPreferredOption(page, selector, preferredValue) {
  await page.waitForFunction((selectSelector) => {
    const select = document.querySelector(selectSelector);
    return select && select.options.length > 0;
  }, selector);
  const values = await page.locator(`${selector} option`).evaluateAll((options) => options.map((option) => option.value));
  const selected = values.includes(preferredValue) ? preferredValue : values[0];
  await page.locator(selector).selectOption(selected);
  return selected;
}

test('runs a hosted demo scan through the WebUI', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'VulnoraIQ', exact: true })).toBeVisible();

  await selectPreferredOption(page, '#target-select', 'demo');
  await selectPreferredOption(page, '#profile-select', 'baseline');

  await expect(page.locator('#active-scan-elapsed')).toBeVisible();
  await expect(page.locator('#active-scan-eta')).toBeVisible();

  await page.getByRole('button', { name: 'Start selected assessment' }).click();

  await expect(page.locator('#active-scan-card')).not.toHaveClass(/idle/);
  await expect(page.locator('#dashboard')).toBeVisible({ timeout: 90_000 });
  await expect(page.locator('#summary-target')).not.toHaveText('-', { timeout: 10_000 });
  await expect(page.locator('#artifact-links')).not.toHaveText(/No report artifacts available/i);
});
