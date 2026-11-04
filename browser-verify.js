// Optional Playwright CLI verification. Run against `python spikes.py serve`.
// No @playwright/test dependency; all pages and requests stay on loopback.
async (page) => {
  const checks = [];
  function check(name, passed) {
    if (!passed) throw new Error(name);
    checks.push({ name, passed });
  }
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('http://127.0.0.1:8765/repro');
  await page.getByRole('status').first().filter({ hasText: '1 mug(s)' }).waitFor();
  await page.getByLabel('Quantity', { exact: true }).fill('2');
  await page.getByRole('button', { name: 'Update cart' }).click();
  await page.getByRole('status').first().filter({ hasText: '2 mug(s)' }).waitFor();
  check('Cart bug visible after quantity change',
    await page.locator('#cart').textContent() === '2 mug(s) · Total $12.00');
  await page.getByRole('button', { name: 'Run reproduction' }).click();
  await page.locator('#verdict').filter({ hasText: 'Bug reproduced.' }).waitFor();
  check('Report produced expected $24 versus actual $12',
    await page.locator('#verdict').textContent() === 'Bug reproduced. Expected $24.00 · Observed $12.00');
  const defaultEvidence = JSON.parse(await page.locator('#evidence').textContent());
  check('Two executed HTTP 200 responses',
    defaultEvidence.steps.length === 2 && defaultEvidence.steps.every(step => step.status === 200));
  await page.screenshot({ path: 'output/playwright/repro-desktop.png', fullPage: true });

  await page.getByLabel('Bug report', { exact: true }).fill('The price of three mugs is wrong');
  await page.getByRole('button', { name: 'Run reproduction' }).click();
  await page.locator('#verdict').filter({ hasText: 'Expected $36.00' }).waitFor();
  check('Changing report changes executed case',
    JSON.parse(await page.locator('#evidence').textContent()).steps[1].body.quantity === 3);
  await page.getByLabel('Bug report', { exact: true }).fill('login is slow');
  await page.getByRole('button', { name: 'Run reproduction' }).click();
  await page.locator('#verdict').filter({ hasText: 'Unsupported report' }).waitFor();
  check('Unsupported report clears previous evidence',
    await page.locator('#evidence').textContent() === 'No reproduction evidence generated.');

  await page.getByRole('link', { name: 'BLASTLAB', exact: true }).click();
  await page.locator('#total').filter({ hasText: '$72.00' }).waitFor();
  check('Restored mission result rendered',
    await page.locator('#summary').textContent() === 'Mission completed from the restored checkpoint.');
  check('Reset and outside-child sentinel rendered',
    await page.locator('#checks').textContent() === 'Reset hashes verified · Outside-child sentinel unchanged');
  const allEvidence = JSON.parse(await page.locator('#evidence').textContent());
  const events = allEvidence.blastlab.events;
  check('All actual timeline events rendered', await page.locator('#timeline .event').count() === events.length);
  check('Three denied hostile actions rendered', await page.locator('#timeline .fail').count() === 3);
  check('Mission completion comes after reset and fresh resume',
    events.findIndex(e => e.event === 'containment_reset') < events.findIndex(e => e.event === 'mission_resumed')
    && events.at(-1).event === 'mission_completed');
  await page.screenshot({ path: 'output/playwright/blastlab-desktop.png', fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  check('BLASTLAB fits mobile width', await page.evaluate(() =>
    document.documentElement.scrollWidth <= window.innerWidth));
  await page.screenshot({ path: 'output/playwright/blastlab-mobile.png', fullPage: true });
  await page.getByRole('link', { name: 'REPRO', exact: true }).click();
  await page.getByRole('button', { name: 'Run reproduction' }).click();
  await page.locator('#verdict').filter({ hasText: 'Bug reproduced.' }).waitFor();
  check('REPRO fits mobile width', await page.evaluate(() =>
    document.documentElement.scrollWidth <= window.innerWidth));
  await page.screenshot({ path: 'output/playwright/repro-mobile.png', fullPage: true });
  check('No JavaScript runtime errors', errors.length === 0);
  return { checked_at: new Date().toISOString(), run_id: allEvidence.run_id,
    checks, default_repro_evidence: defaultEvidence, javascript_errors: errors };
}
