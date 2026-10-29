// Screenshot live vs mirrored pages and report console/network errors on the mirror.
const { chromium } = require('playwright');
const fs = require('fs');
const paths = process.argv.slice(2);
const LOCAL = process.env.LOCAL || 'http://127.0.0.1:8765';
const LIVE = 'https://imoves.com';
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 900 }, deviceScaleFactor: 1 });
  fs.mkdirSync('shots', { recursive: true });
  const report = [];
  for (const p of paths) {
    const name = p === '/' ? 'home' : p.replace(/^\//, '').replace(/\//g, '__');
    const row = { path: p };
    for (const [label, base] of [['live', LIVE], ['copy', LOCAL]]) {
      const page = await ctx.newPage();
      const bad = [];
      page.on('console', m => { if (m.type() === 'error') bad.push('console: ' + m.text().slice(0, 160)); });
      page.on('requestfailed', r => bad.push('failed: ' + r.url().slice(0, 160)));
      page.on('response', r => { if (r.status() >= 400 && !/justreview|paddle|googletag|leadconnector|facebook|wistia/.test(r.url())) bad.push(r.status() + ' ' + r.url().slice(0, 160)); });
      try {
        await page.goto(base + p, { waitUntil: 'networkidle', timeout: 60000 });
      } catch (e) { bad.push('goto: ' + e.message.slice(0, 120)); }
      await page.waitForTimeout(1500);
      const h = await page.evaluate(() => document.documentElement.scrollHeight);
      const text = await page.evaluate(() => document.body.innerText.replace(/\s+/g, ' ').trim());
      await page.screenshot({ path: `shots/${name}-${label}.png`, fullPage: true });
      row[label] = { height: h, textLen: text.length, textHash: require('crypto').createHash('md5').update(text).digest('hex').slice(0, 8), issues: bad };
      row[label + 'Text'] = text;
      await page.close();
    }
    row.sameText = row.live.textHash === row.copy.textHash;
    if (!row.sameText) {
      // find first differing position
      const a = row.liveText, b = row.copyText; let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++;
      row.firstDiff = { live: a.slice(Math.max(0, i - 40), i + 80), copy: b.slice(Math.max(0, i - 40), i + 80) };
    }
    delete row.liveText; delete row.copyText;
    report.push(row);
    console.log(p, row.sameText ? 'TEXT MATCH' : 'TEXT DIFF', 'h', row.live.height, 'vs', row.copy.height, 'copy issues:', row.copy.issues.length);
  }
  fs.writeFileSync('compare-report.json', JSON.stringify(report, null, 1));
  await browser.close();
})();
