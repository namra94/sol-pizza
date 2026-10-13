// Lighthouse on a phone (Lighthouse's mobile defaults), cookies rejected, against the
// budgets in the brief: Performance 90+, Accessibility 100, Best Practices 95+, SEO 100,
// LCP 2.5 s or less, CLS under 0.1, TBT 200 ms or less. Each page runs three times
// (LH_RUNS to change it) and the budgets apply to the median of each score and timing,
// as Lighthouse advises: one run can be off by half a second either way.
//   node lighthouse.js <base URL> [path …]     default paths: / /menu/ /booking/
// Run it against a Preview URL or sol.pizza: the local server has no compression,
// HTTP/2 or early hints, so its scores aren't the site's. Reports go to out/ (the run
// nearest the median).
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const consent = require('./consent.js');

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
  const choice = consent.choice({}, await consent.versionAt(base));
  const setup = await ctx.newPage();
  await setup.goto(base + '/robots.txt');
  await setup.evaluate(consent.store, choice);
  await setup.close();
  // Previews answer with "x-robots-tag: noindex" (on purpose: they're not for search), which
  // costs SEO its crawlable audit; only sol.pizza is held to that one.
  const live = new URL(base).hostname === 'sol.pizza';
  if (!live) console.log('(not sol.pizza: SEO leaves out "is-crawlable", as previews are kept out of search on purpose)');
  const RUNS = Math.max(1, Number(process.env.LH_RUNS) || 3);
  const median = xs => { const v = xs.slice().sort((a, b) => a - b); return v[(v.length - 1) >> 1]; };
  let failed = 0;
  for (const p of paths) {
    const runs = [];
    for (let i = 0; i < RUNS; i++) {
      // each run a guest's first page: Lighthouse empties the browser's cache (its storage
      // reset leaves localStorage, where the cookie choice is), and no cookies (on
      // sol.pizza, Cloudflare's bot script runs until its cookie is set)
      await ctx.clearCookies();
      runs.push(await lighthouse(base + p, {port, output: 'html', logLevel: 'error',
        onlyCategories: Object.keys(BUDGET), skipAudits: live ? [] : ['is-crawlable']}));
    }
    const score = (r, k) => Math.round(r.lhr.categories[k].score * 100);
    const scores = Object.fromEntries(Object.keys(BUDGET).map(k => [k, median(runs.map(r => score(r, k)))]));
    const metrics = Object.fromEntries(Object.keys(LIMITS).map(k => [k, median(runs.map(r => r.lhr.audits[k].numericValue))]));
    // the report to keep: the run whose performance score is the median
    const kept = runs.find(r => score(r, 'performance') === scores.performance) || runs[0];
    const lhr = kept.lhr;
    fs.writeFileSync(path.join(out, (p.replace(/\W+/g, '_') || '_') + '.html'), kept.report);
    const misses = Object.keys(BUDGET).filter(k => scores[k] < BUDGET[k]).map(k => k + ' ' + scores[k])
      .concat(Object.keys(LIMITS).filter(k => metrics[k] > LIMITS[k] || (k === 'cumulative-layout-shift' && metrics[k] >= LIMITS[k]))
        .map(k => k + ' ' + metrics[k]));
    const range = k => { const v = runs.map(r => r.lhr.audits[k].numericValue / 1000); return Math.min(...v).toFixed(2) + '–' + Math.max(...v).toFixed(2); };
    console.log('%s  perf %d · a11y %d · best practices %d · SEO %d · LCP %s s · TBT %d ms · CLS %s%s%s', p,
      scores.performance, scores.accessibility, scores['best-practices'], scores.seo,
      (metrics['largest-contentful-paint'] / 1000).toFixed(2), Math.round(metrics['total-blocking-time']),
      metrics['cumulative-layout-shift'].toFixed(3),
      RUNS > 1 ? '   (median of ' + RUNS + '; perf ' + runs.map(r => score(r, 'performance')).join('/') + ', LCP ' +
        range('largest-contentful-paint') + ' s)' : '',
      misses.length ? '   OVER BUDGET: ' + misses.join(', ') : '');
    for (const k of Object.keys(BUDGET)) {
      if (scores[k] === 100) continue;
      for (const a of lhr.categories[k].auditRefs) {
        const audit = lhr.audits[a.id];
        if (a.weight > 0 && audit.score !== null && audit.score < 1) console.log('     %s: %s (%s)', k, audit.id, audit.displayValue || audit.score);
      }
    }
    const botScript = JSON.stringify(lhr.audits.deprecations.details || {}).includes('/cdn-cgi/challenge-platform/');
    if (misses.length && botScript) console.log('     (Cloudflare\'s bot script, on sol.pizza only: LAUNCH-CHECKLIST.md §6)');
    if (misses.length) failed++;
  }
  await ctx.close();
  console.log(failed ? failed + ' page(s) over budget' : 'all within budget');
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
