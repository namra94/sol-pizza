// Accessibility: axe-core (WCAG 2.2 A and AA) on every page in dist/, in both
// languages, at a phone's width and a laptop's, with the cookie banner open (a first
// visit) and after a choice, plus the nav sheet open on a phone. Best-practice
// findings are listed but don't fail the check.
//   node axe.js                 the local build (../dist)
//   node axe.js <base URL>      a Preview URL or sol.pizza (the same pages)
const {chromium} = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;
const fs = require('fs'), path = require('path');
const serve = require('./serve.js');
const consent = require('./consent.js');

const DIST = path.resolve(__dirname, '..', 'dist');
const WCAG = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];
// What's inside the booking frame is ResDiary's markup, not ours: its findings go to ResDiary
// and don't fail this check. In axe's terms: the head and body inside that frame, so the
// <iframe> element stays in and its title is still checked (a plain '.book-widget iframe'
// would leave out the element too, and 'html' on its own excludes nothing: axe's starting
// point wins over an exclusion of the same element).
const RESDIARY_FRAME_CONTENT = ['.book-widget iframe', 'html > *'];

function pages() {
  const out = [];
  (function walk(dir) {
    for (const f of fs.readdirSync(dir).sort()) {
      const p = path.join(dir, f);
      if (fs.statSync(p).isDirectory()) walk(p);
      else if (f.endsWith('.html')) {
        const rel = '/' + path.relative(DIST, p).split(path.sep).join('/');
        out.push(rel.endsWith('/index.html') ? rel.slice(0, -10) : rel === '/index.html' ? '/' : rel.replace(/\.html$/, ''));
      }
    }
  })(DIST);
  return out.map(p => p === '' ? '/' : p).filter(p => !/^\/(vi\/)?404$/.test(p)).concat(['/no-such-page', '/vi/no-such-page']);
}

(async () => {
  let base = process.argv[2], server = null;
  if (!base) { server = await serve(DIST, 8898); base = 'http://localhost:8898'; }
  base = base.replace(/\/$/, '');
  const V = await consent.versionAt(base);
  const browser = await chromium.launch(process.env.CHROME_PATH ? {executablePath: process.env.CHROME_PATH} : {});
  const list = pages();
  let violations = 0, practice = 0, runs = 0;
  const seen = new Map();
  for (const [label, viewport, choice] of [['phone, first visit', {width: 390, height: 844}, null],
                                            ['laptop, after a choice', {width: 1280, height: 900}, 'none']]) {
    const ctx = await browser.newContext({viewport});
    await ctx.route(/googletagmanager|google-analytics|facebook|typekit/, r => r.fulfill({status: 204, body: ''}));
    if (choice) await ctx.addInitScript(consent.store, consent.choice({}, V));
    const page = await ctx.newPage();
    for (const p of list) {
      // A ResDiary that never answers holds up the booking pages' load event, not their content
      await page.goto(base + p, {waitUntil: 'load'}).catch(async e => {
        if (!(await page.$('.book-widget iframe'))) throw e;
        console.log('(%s: the booking frame has not finished loading)', p);
      });
      const states = [['', null]];
      if (!choice && viewport.width < 1024 && (await page.$('[data-sheet-open]'))) states.push(['nav sheet open', '[data-sheet-open]']);
      for (const [state, click] of states) {
        if (click) { await page.click(click); await page.waitForTimeout(100); }
        const r = await new AxeBuilder({page}).withTags(WCAG.concat(['best-practice'])).exclude(RESDIARY_FRAME_CONTENT).analyze();
        runs++;
        for (const v of r.violations) {
          const wcag = v.tags.some(t => WCAG.includes(t));
          const key = v.id + ' ' + p + ' ' + label + ' ' + state;
          if (seen.has(key)) continue;
          seen.set(key, 1);
          if (wcag) violations++; else practice++;
          console.log('%s %s on %s (%s%s): %s', wcag ? 'VIOLATION' : 'best practice', v.id, p, label,
                      state ? ', ' + state : '', v.nodes.slice(0, 3).map(n => n.target.join(' ')).join(' | '));
        }
        if (click) await page.keyboard.press('Escape');
      }
    }
    await ctx.close();
  }
  await browser.close();
  if (server) server.close();
  console.log('axe: %d pages, %d runs, %d WCAG violations, %d best-practice notes', list.length, runs, violations, practice);
  process.exit(violations ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
