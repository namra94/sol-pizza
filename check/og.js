// Renders the share cards: build/og/html/*.html (written by `npm run build`) to
// build/og/png/*.png at 1200 × 630, in the site's own fonts, and notes in
// build/og/cards.json what each was rendered from; `npm run pack-assets` then adds
// the hash of the PNG that ships. The build checks both.
//   npm run build && npm run og && npm run pack-assets      (from the repo's root)
// The cards load http://localhost:8897/assets/fonts.css; this answers that address
// from build/ itself (build/fonts.css, build/fonts/, build/brand/), so no server runs.
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path'), crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const OG = path.join(ROOT, 'build', 'og');
const FONTS = {'/assets/fonts.css': path.join(ROOT, 'build', 'fonts.css'),
               '/assets/fonts/bn-arora-400-normal.woff2': path.join(ROOT, 'build', 'brand', 'BNArora-Regular.woff2')};

function fontFile(p) {
  if (FONTS[p]) return FONTS[p];
  if (p.startsWith('/assets/fonts/')) return path.join(ROOT, 'build', 'fonts', path.basename(p));
  return null;
}

(async () => {
  const dir = path.join(OG, 'html');
  if (!fs.existsSync(dir)) throw new Error('No build/og/html/: run `npm run build` first (from the repo root).');
  const cards = fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort();
  fs.mkdirSync(path.join(OG, 'png'), {recursive: true});
  const record = {};
  const browser = await chromium.launch(process.env.CHROME_PATH ? {executablePath: process.env.CHROME_PATH} : {});
  const ctx = await browser.newContext({viewport: {width: 1200, height: 630}, deviceScaleFactor: 1});
  await ctx.route('http://localhost:8897/**', route => {
    const f = fontFile(new URL(route.request().url()).pathname);
    if (!f || !fs.existsSync(f)) return route.fulfill({status: 404, body: ''});
    route.fulfill({status: 200, body: fs.readFileSync(f),
                   contentType: f.endsWith('.css') ? 'text/css' : 'font/woff2'});
  });
  const page = await ctx.newPage();
  for (const card of cards) {
    const file = path.join(dir, card);
    const html = fs.readFileSync(file);
    await page.goto('file://' + file, {waitUntil: 'networkidle'});
    await page.evaluate(() => document.fonts.ready);
    const missing = await page.evaluate(() => {
      const want = getComputedStyle(document.querySelector('h1')).fontFamily.split(',')[0].replace(/"/g, '').trim();
      return document.fonts.check('86px "' + want + '"') ? null : want;
    });
    if (missing) throw new Error(card + ': the font ' + missing + ' did not load (run `npm ci` and `npm run build` first)');
    const png = card.replace(/\.html$/, '.png');
    await page.screenshot({path: path.join(OG, 'png', png)});
    record[png] = {from: crypto.createHash('sha1').update(html).digest('hex')};   // pack-assets adds png
    console.log('rendered', png);
  }
  await browser.close();
  fs.writeFileSync(path.join(OG, 'cards.json'), JSON.stringify(record, null, 1) + '\n');
  console.log('wrote build/og/cards.json; now `npm run pack-assets` and commit build/assets.b64.json and build/og/cards.json');
})().catch(e => { console.error(e.message || e); process.exit(1); });
