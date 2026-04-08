// Headless validation of the Kanban board artifacts produced by the
// 5-node mesh. Loads each index.html via file://, exercises the core
// user flows, and asserts state persists across reload.
//
// Usage:  node validate.mjs <path/to/index.html> [label]

import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const htmlPath = process.argv[2];
const label = process.argv[3] || 'unlabeled';
if (!htmlPath) {
  console.error('usage: node validate.mjs <path/to/index.html> [label]');
  process.exit(2);
}

const fileUrl = pathToFileURL(resolve(htmlPath)).href;
const results = { label, path: htmlPath, checks: [] };

function check(name, ok, detail) {
  results.checks.push({ name, ok: !!ok, detail: detail ?? null });
  if (!ok) console.log(`  FAIL ${name}${detail ? ' — ' + detail : ''}`);
  else console.log(`   OK  ${name}`);
}

const browser = await chromium.launch({ headless: true });
try {
  const ctx = await browser.newContext();

  // Capture JS errors as a hard failure signal
  const errors = [];
  ctx.on('weberror', (e) => errors.push(e.error().message));

  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(e.message));

  await page.goto(fileUrl);
  await page.waitForLoadState('domcontentloaded');

  check('page loaded without errors', errors.length === 0,
        errors.length ? errors.join('; ') : null);

  // Clear any prior localStorage and reload
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.waitForLoadState('domcontentloaded');

  // --- Feature: 3 columns present ---
  const columnCount = await page.evaluate(() => {
    const candidates = document.querySelectorAll(
      '.column, [data-column], [class*="column"], [class*="list"]'
    );
    return candidates.length;
  });
  check('at least 3 columns rendered', columnCount >= 3,
        `found ${columnCount} candidates`);

  // --- Feature: add a card via the text input ---
  // Strategy: fill every text input on the page with a marker,
  // then trigger Enter + click every button with add-like text.
  const marker1 = 'MESH_TEST_CARD_A_' + Date.now();
  const marker2 = 'MESH_TEST_CARD_B_' + Date.now();

  // Re-query between interactions because re-rendering detaches handles.
  {
    const inp = await page.$('input[type="text"], input:not([type])');
    if (inp) {
      await inp.fill(marker1);
      await inp.press('Enter');
      await page.waitForTimeout(200);
    }
  }
  {
    const inp = await page.$('input[type="text"], input:not([type])');
    if (inp) {
      await inp.fill(marker2);
      const addBtn = await page.$('button:has-text("Add"), .btn-add');
      if (addBtn) await addBtn.click();
      else await inp.press('Enter');
    }
  }

  await page.waitForTimeout(200);
  const cardAPresent = await page.evaluate((m) => document.body.innerText.includes(m), marker1);
  check('added card A visible in DOM', cardAPresent);

  // --- Feature: persistence across reload ---
  await page.reload();
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(200);
  const cardAAfterReload = await page.evaluate((m) => document.body.innerText.includes(m), marker1);
  check('card A persists across reload', cardAAfterReload);

  // --- Feature: move a card between columns ---
  // Look for a button on a card that moves it (Next / → / move-right).
  const moveClicked = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const candidates = btns.filter(b => /next|→|>|right|move/i.test(b.textContent));
    if (candidates.length === 0) return false;
    candidates[0].click();
    return true;
  });
  check('move-card button exists and clicked', moveClicked);

  // --- Feature: delete a card ---
  const deleteClicked = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const cand = btns.filter(b => /delete|remove|×|✕|x|trash/i.test(b.textContent));
    if (cand.length === 0) return false;
    cand[0].click();
    return true;
  });
  check('delete button exists and clicked', deleteClicked);

  // --- Feature: kanbanAPI global exists (evidence of FE/BE wiring) ---
  const apiShape = await page.evaluate(() => {
    if (!window.kanbanAPI) return null;
    return Object.keys(window.kanbanAPI).sort();
  });
  check('window.kanbanAPI global present', apiShape !== null,
        apiShape ? `keys=${apiShape.join(',')}` : 'undefined');

  // Final: still no JS errors after interactions
  check('no JS errors after interactions', errors.length === 0,
        errors.join('; ') || null);

  const total = results.checks.length;
  const passed = results.checks.filter(c => c.ok).length;
  results.passed = passed;
  results.total = total;
  results.success = passed === total;
  console.log(`\n[${label}] ${passed}/${total} checks passed`);
  console.log(JSON.stringify(results));
} finally {
  await browser.close();
}
