// Full-site comparison: live imoves.com vs the copy, at desktop and phone widths.
// Serves jQuery/matchHeight locally (CDNs are blocked here) so both sides run their JS.
// Blocks the same third-party hosts on both sides so analytics/widgets don't add noise.
// Usage: node compare-all.js <paths-file> <out-dir>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const [,, listFile, outDir] = process.argv;
const paths = fs.readFileSync(listFile, 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
const LIVE = process.env.BASE_A || 'http://127.0.0.1:8766/imoves-website/version-a';
const COPY = process.env.LOCAL || 'http://127.0.0.1:8766/imoves-website';
const LIBS = { 'jquery.min.js': fs.readFileSync(path.join(__dirname, 'libs/jquery.min.js')),
               'jquery.matchHeight-min.js': fs.readFileSync(path.join(__dirname, 'libs/jquery.matchHeight-min.js')) };
const BLOCK = /googletagmanager|google-analytics|facebook|hotjar|doubleclick|leadconnectorhq|instant\.page|wistia|justreview|paddle|gstatic\.com\/recaptcha/;
fs.mkdirSync(outDir, { recursive: true });
const name = p => p === '/' ? 'home' : p.replace(/^\//, '').replace(/\//g, '__');

async function shoot(ctx, base, p, label, w) {
  const page = await ctx.newPage();
  const issues = [];
  await page.route('**/*', route => {
    const u = route.request().url();
    const m = u.match(/(jquery\.min\.js|jquery\.matchHeight-min\.js)/);
    if (m) return route.fulfill({ status: 200, contentType: 'application/javascript', body: LIBS[m[1]] });
    if (BLOCK.test(u)) return route.abort();
    return route.continue();
  });
  page.on('pageerror', e => issues.push('js: ' + e.message.slice(0, 120)));
  page.on('response', r => { const u = r.url(); if (r.status() >= 400 && !BLOCK.test(u)) issues.push(r.status() + ' ' + u.replace(LIVE, '').replace(COPY, '').slice(0, 140)); });
  page.on('requestfailed', r => { const u = r.url(); if (!BLOCK.test(u)) issues.push('failed ' + u.replace(LIVE, '').replace(COPY, '').slice(0, 140)); });
  try { await page.goto(base + p + (p !== '/' ? '/' : ''), { waitUntil: 'load', timeout: 60000 }); } catch (e) { issues.push('goto: ' + e.message.slice(0, 100)); }
  await page.waitForTimeout(1500);
  // settle lazy images
  await page.evaluate(async () => { window.scrollTo(0, document.body.scrollHeight); await new Promise(r => setTimeout(r, 400)); window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 400)); });
  const info = await page.evaluate(() => {
    const text = document.body.innerText.replace(/\s+/g, ' ').trim();
    const links = [...document.querySelectorAll('a[href]')].map(a => { try { const u = new URL(a.href); return (u.hostname.endsWith('imoves.com') && !u.hostname.startsWith('platform') && !u.hostname.startsWith('aac') ? '' : u.origin) + u.pathname.replace(/\/$/, '') + u.search; } catch (e) { return a.getAttribute('href'); } });
    const imgs = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src')).map(i => i.getAttribute('src').split('/').pop());
    const fonts = [...new Set([...document.querySelectorAll('h1,h2,h3,p,a,li,span')].slice(0, 400).map(e => getComputedStyle(e).fontFamily))];
    return { h: document.documentElement.scrollHeight, text, links, brokenImgs: imgs, fonts, title: document.title };
  });
  const buf = await page.screenshot({ fullPage: true });
  fs.writeFileSync(path.join(outDir, `${name(p)}@${w}-${label}.png`), buf);
  await page.close();
  return { ...info, textHash: crypto.createHash('md5').update(info.text).digest('hex').slice(0, 10), issues };
}

(async () => {
  const browser = await chromium.launch();
  const results = [];
  for (const w of [1366, 390]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: w > 500 ? 900 : 844 }, deviceScaleFactor: 1, isMobile: w < 500, hasTouch: w < 500 });
    // concurrency 3
    const queue = [...paths];
    const workers = Array.from({ length: 3 }, async () => {
      while (queue.length) {
        const p = queue.shift();
        try {
          const [live, copy] = await Promise.all([shoot(ctx, LIVE, p, 'live', w), shoot(ctx, COPY, p, 'copy', w)]);
          const row = { path: p, w, sameText: live.textHash === copy.textHash, hLive: live.h, hCopy: copy.h, title: [live.title, copy.title],
            linksDiff: JSON.stringify(live.links) === JSON.stringify(copy.links) ? 0 : live.links.filter((x, i) => x !== copy.links[i]).length,
            linkSample: live.links.map((x, i) => [x, copy.links[i]]).filter(([a, b]) => a !== b).slice(0, 3),
            fontsSame: JSON.stringify(live.fonts.sort()) === JSON.stringify(copy.fonts.sort()), fontsLive: live.fonts, fontsCopy: copy.fonts,
            brokenImgsCopy: copy.brokenImgs, issuesCopy: copy.issues, issuesLive: live.issues };
          if (!row.sameText) { const a = live.text, b = copy.text; let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++; row.firstDiff = { live: a.slice(Math.max(0, i - 40), i + 80), copy: b.slice(Math.max(0, i - 40), i + 80) }; }
          results.push(row);
          console.log(`${w} ${p} text:${row.sameText ? 'ok' : 'DIFF'} h:${live.h}/${copy.h} links:${row.linksDiff} fonts:${row.fontsSame ? 'ok' : 'DIFF'} copyIssues:${copy.issues.length}`);
        } catch (e) { results.push({ path: p, w, error: e.message }); console.log(w, p, 'ERROR', e.message.slice(0, 100)); }
      }
    });
    await Promise.all(workers);
    await ctx.close();
  }
  fs.writeFileSync(path.join(outDir, 'results.json'), JSON.stringify(results, null, 1));
  await browser.close();
})();
