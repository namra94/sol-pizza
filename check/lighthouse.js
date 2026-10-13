// Lighthouse on a phone (Lighthouse's mobile defaults), cookies rejected, against the
// budgets in the brief: Performance 90+, Accessibility 100, Best Practices 95+, SEO 100,
// LCP 2.5 s or less, CLS under 0.1, TBT 200 ms or less.
//   node lighthouse.js <base URL> [path …]     default paths: / /menu/ /booking/
// Run it against a Preview URL or sol.pizza: the local server has no compression,
// HTTP/2 or early hints, so its scores aren't the site's. Reports go to out/.
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path'), os = require('os');

const BUDGET = {performance: 90, accessibility: 100, 'best-practices': 95, seo: 100};
const LIMITS = {'largest-contentful-paint': 2500, 'total-blocking-time': 200, 'cumulative-layout-shift': 0.1};

(async () => {
  const {default: lighthouse} = await import('lighthouse');
  const base = (process.argv[2] || '').replace(/\/$/, '');
  if (!base) throw new Error('usage: node lighthouse.js <base URL> [path …]');
  const paths = process.argv.slice(3).length ? process.argv.slice(3) : ['/', '/menu/', '/booking/'];
  const out = path.join(__dirname, 'out', 'lighthouse');
  fs.mkdirSync(out, {recursive: true});
  const port = 9300 + Math.floor(Math.random() * 500);
  // A persistent context is the browser's default one, where Lighthouse opens its tab,
  // so the cookie choice set here is the one it sees.
  const ctx = await chromium.launchPersistentContext(fs.mkdtempSync(path.join(os.tmpdir(), 'sol-lh-')), {
    headless: true, args: ['--remote-debugging-port=' + port],
    executablePath: process.env.CHROME_PATH || undefined,
  });
  const setup = await ctx.newPage();
  await setup.goto(base + '/robots.txt');
  await setup.evaluate(() => localStorage.setItem('sol-consent', JSON.stringify(
    {v: 1, t: new Date().toISOString(), analytics: false, ads: false})));
  await setup.close();
  let failed = 0;
  for (const p of paths) {
    const r = await lighthouse(base + p, {port, output: 'html', logLevel: 'error', disableStorageReset: true,
      onlyCategories: Object.keys(BUDGET)});
    const lhr = r.lhr;
    fs.writeFileSync(path.join(out, (p.replace(/\W+/g, '_') || '_') + '.html'), r.report);
    const scores = Object.fromEntries(Object.keys(BUDGET).map(k => [k, Math.round(lhr.categories[k].score * 100)]));
    const metrics = Object.fromEntries(Object.keys(LIMITS).map(k => [k, lhr.audits[k].numericValue]));
    const misses = Object.keys(BUDGET).filter(k => scores[k] < BUDGET[k]).map(k => k + ' ' + scores[k])
      .concat(Object.keys(LIMITS).filter(k => metrics[k] > LIMITS[k] || (k === 'cumulative-layout-shift' && metrics[k] >= LIMITS[k]))
        .map(k => k + ' ' + metrics[k]));
    console.log('%s  perf %d · a11y %d · best practices %d · SEO %d · LCP %s s · TBT %d ms · CLS %s%s', p,
      scores.performance, scores.accessibility, scores['best-practices'], scores.seo,
      (metrics['largest-contentful-paint'] / 1000).toFixed(2), Math.round(metrics['total-blocking-time']),
      metrics['cumulative-layout-shift'].toFixed(3), misses.length ? '   OVER BUDGET: ' + misses.join(', ') : '');
    for (const k of Object.keys(BUDGET)) {
      if (scores[k] === 100) continue;
      for (const a of lhr.categories[k].auditRefs) {
        const audit = lhr.audits[a.id];
        if (a.weight > 0 && audit.score !== null && audit.score < 1) console.log('     %s: %s (%s)', k, audit.id, audit.displayValue || audit.score);
      }
    }
    if (misses.length) failed++;
  }
  await ctx.close();
  console.log(failed ? failed + ' page(s) over budget' : 'all within budget');
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
