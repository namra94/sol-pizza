// Screenshots of the guest pages at the widths people use (360, 390, 768, 1,024 and
// 1,440 px), in English and Vietnamese, whole pages, cookies already chosen (so the
// banner doesn't cover them), slow fades finished. To look over a pull request, or to
// compare before and after. They go to out/screens/ (never committed), with an index
// page to scroll through.
//   node screens.js                   the local build (../dist)
//   node screens.js <base URL>        a Preview URL or sol.pizza
//   node screens.js <base URL> /menu/ /booking/     just these pages
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path');
const serve = require('./serve.js');
const consent = require('./consent.js');

const WIDTHS = [360, 390, 768, 1024, 1440];
const PAGES = ['/', '/menu/', '/menu/wine/', '/menu/bar/', '/about/', '/events/', '/private-dining/', '/visit-us/',
               '/booking/', '/press/', '/jobs/', '/jobs/host/', '/privacy/', '/privacy/cookies/', '/no-such-page/'];

(async () => {
  let base = process.argv[2], server = null;
  if (!base || base.startsWith('/')) { server = await serve(path.resolve(__dirname, '..', 'dist'), 8893); base = 'http://localhost:8893'; }
  base = base.replace(/\/$/, '');
  const V = await consent.versionAt(base);
  const asked = process.argv.slice(2).filter(a => a.startsWith('/'));
  const pages = asked.length ? asked : PAGES;
  const out = path.join(__dirname, 'out', 'screens');
  fs.rmSync(out, {recursive: true, force: true});
  fs.mkdirSync(out, {recursive: true});
  const browser = await chromium.launch(process.env.CHROME_PATH ? {executablePath: process.env.CHROME_PATH} : {});
  const shots = [];
  for (const width of WIDTHS) {
    const ctx = await browser.newContext({viewport: {width, height: 900}, deviceScaleFactor: 1});
    await ctx.route(/googletagmanager|google-analytics|facebook|typekit/, r => r.fulfill({status: 204, body: ''}));
    await ctx.addInitScript(consent.store, consent.choice({}, V));
    const page = await ctx.newPage();
    for (const lang of ['en', 'vi']) {
      for (const p of pages) {
        const url = base + (lang === 'vi' ? '/vi' + p : p);
        await page.goto(url, {waitUntil: 'load'});
        await page.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-in')));
        await page.waitForTimeout(250);
        const wide = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
        const file = `${lang}-${width}-${p.replace(/\W+/g, '-').replace(/^-|-$/g, '') || 'home'}.png`;
        await page.screenshot({path: path.join(out, file), fullPage: true});
        shots.push({file, url, p, width, lang, wide});
        if (wide) console.log('SIDEWAYS SCROLL  %s at %d px', url, width);
      }
    }
    await ctx.close();
  }
  await browser.close();
  if (server) server.close();
  fs.writeFileSync(path.join(out, 'index.html'), '<!doctype html><meta charset="utf-8"><title>sol.pizza screenshots</title>' +
    '<style>body{font:14px system-ui;margin:20px}section{margin:30px 0}img{max-width:100%;border:1px solid #ccc}' +
    '.row{display:flex;gap:16px;align-items:flex-start;overflow-x:auto}</style>' +
    '<p>Whole pages, 900 px of window at a time. The bar fixed to the foot of the window on phones ' +
    '(Book · Directions) shows where the first window ends, not at the foot of the page.</p>' +
    pages.map(p => '<section><h2>' + p + '</h2>' + ['en', 'vi'].map(lang => '<div class="row">' + shots
      .filter(s => s.lang === lang && s.p === p).map(s =>
        '<figure><figcaption>' + lang.toUpperCase() + ' ' + s.width + ' px</figcaption><img src="' + s.file +
        '" width="' + Math.min(s.width, 360) + '" loading="lazy"></figure>').join('') + '</div>').join('') +
      '</section>').join(''));
  const sideways = shots.filter(s => s.wide).length;
  console.log('screens: %d screenshots in check/out/screens/ (open index.html)%s', shots.length,
              sideways ? '; ' + sideways + ' scroll sideways' : '; none scrolls sideways');
  process.exit(sideways ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
