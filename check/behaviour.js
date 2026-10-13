// What the guest pages do, in a real browser: the language addresses and the EN · VI
// choice, the cookie banner (and that nothing optional loads before a yes), the
// header, the phone bar, the events, and that the kitchen has none of it.
//   node behaviour.js                 the local build (../dist), served by serve.js
//   node behaviour.js <base URL>      a Preview URL or sol.pizza
const {chromium} = require('playwright');
const path = require('path');
const serve = require('./serve.js');

const TOOLS = /googletagmanager\.com|google-analytics\.com|connect\.facebook\.net|facebook\.com\/tr/;
let failures = 0;
function ok(cond, what) {
  console.log((cond ? '  ok   ' : '  FAIL ') + what);
  if (!cond) failures++;
}

async function main() {
  let base = process.argv[2];
  let server = null;
  if (!base) {
    server = await serve(path.resolve(__dirname, '..', 'dist'), 8899);
    base = 'http://localhost:8899';
  }
  base = base.replace(/\/$/, '');
  const browser = await chromium.launch(process.env.CHROME_PATH ? {executablePath: process.env.CHROME_PATH} : {});

  // A fresh visitor: records every request to an analytics or advertising host,
  // and answers them with nothing (no data leaves this check).
  async function visitor(viewport) {
    const ctx = await browser.newContext({viewport: viewport || {width: 1280, height: 900}});
    const tools = [];
    await ctx.route(TOOLS, r => { tools.push(r.request().url()); r.fulfill({status: 204, body: ''}); });
    await ctx.route(/typekit\.net/, r => r.fulfill({status: 200, contentType: 'text/css', body: ''}));
    const page = await ctx.newPage();
    return {ctx, page, tools};
  }
  const html = p => p.evaluate(() => ({lang: document.documentElement.lang, cls: document.documentElement.className,
                                         path: location.pathname + location.search + location.hash}));

  console.log('Languages');
  {
    const {ctx, page} = await visitor();
    await page.goto(base + '/?lang=vi');
    let h = await html(page);
    ok(h.path === '/vi/' && h.lang === 'vi', 'an old /?lang=vi link opens /vi/ in Vietnamese (' + h.path + ')');
    await page.goto(base + '/about/?lang=vi&utm_source=test#main');
    h = await html(page);
    ok(h.path === '/vi/about/?utm_source=test#main', '?lang=vi keeps the other parameters and the hash (' + h.path + ')');
    await page.goto(base + '/privacy/#vi');
    h = await html(page);
    ok(h.path === '/vi/privacy/' && h.lang === 'vi', '/privacy/#vi opens /vi/privacy/ (' + h.path + ')');
    await page.goto(base + '/story/?lang=vi');
    h = await html(page);
    ok(h.path === '/vi/about/', 'an old address with ?lang=vi lands on its /vi/ page (' + h.path + ')');
    await ctx.close();
  }
  {
    const {ctx, page} = await visitor();
    await page.goto(base + '/menu/');
    await page.click('.sitebar [data-lang-link="vi"]');
    await page.waitForURL(/\/vi\/menu\/$/);
    ok(await page.evaluate(() => localStorage.getItem('sol-lang')) === 'vi', 'VI on /menu/ goes to /vi/menu/ and is remembered');
    await page.goto(base + '/');
    let h = await html(page);
    ok(h.path === '/vi/', 'the home page then opens in Vietnamese (' + h.path + ')');
    await page.goto(base + '/menu/wine/');
    h = await html(page);
    ok(h.path === '/menu/wine/' && h.lang === 'en', 'a link to an English page still opens in English (' + h.path + ')');
    await page.goto(base + '/vi/');
    await page.click('.sitebar [data-lang-link="en"]');
    await page.waitForURL(u => new URL(u).pathname === '/');
    await page.goto(base + '/');
    h = await html(page);
    ok(h.path === '/' && h.lang === 'en', 'EN is remembered too (' + h.path + ')');
    await ctx.close();
  }
  {
    const {ctx, page} = await visitor();
    let r = await page.goto(base + '/vi/no-such-page/');
    let h = await html(page);
    ok(r.status() === 404 && h.lang === 'vi', 'a missing /vi/ address: the Vietnamese 404 (' + r.status() + ', ' + h.lang + ')');
    r = await page.goto(base + '/no-such-page/');
    h = await html(page);
    ok(r.status() === 404 && h.lang === 'en', 'a missing address: the English 404');
    await ctx.close();
  }

  console.log('Cookies');
  {
    const {ctx, page, tools} = await visitor({width: 390, height: 844});
    await page.goto(base + '/', {waitUntil: 'load'});
    await page.waitForTimeout(1500);
    ok(await page.isVisible('#consent'), 'the banner shows to a first visitor');
    ok(tools.length === 0, 'nothing optional loads before a choice (' + tools.length + ' requests)');
    ok(!(await page.isVisible('.actionbar')), 'the phone bar waits behind the banner');
    const sizes = await page.$$eval('#consent [data-consent="all"], #consent [data-consent="none"], #consent [data-consent="settings"]',
      bs => bs.map(b => [b.className, Math.round(b.getBoundingClientRect().height)].join(' ')));
    ok(new Set(sizes).size === 1, 'Accept all, Reject all and Settings look alike (' + sizes.join(' | ') + ')');
    await page.click('[data-consent="none"]');
    ok(!(await page.isVisible('#consent')), 'Reject all closes the banner');
    ok(await page.isVisible('.actionbar'), 'the phone bar appears');
    await page.reload({waitUntil: 'load'});
    await page.waitForTimeout(1500);
    ok(!(await page.isVisible('#consent')) && tools.length === 0, 'after Reject all: no banner, still nothing loaded');
    await page.click('.site-footer [data-consent-open]');
    ok(await page.isVisible('#consent-settings'), 'Cookie settings in the footer reopens it, with the choices');
    ok(!(await page.isChecked('#consent [name="analytics"]')) && !(await page.isChecked('#consent [name="ads"]')),
       'the choices start unticked');
    await page.check('#consent [name="analytics"]');
    await page.click('[data-consent="save"]');
    await page.waitForTimeout(1500);
    ok(tools.some(u => /googletagmanager/.test(u)) && !tools.some(u => /facebook/.test(u)),
       'a yes to Analytics alone loads Google Analytics and not the Meta Pixel');
    tools.length = 0;
    await page.click('.site-footer [data-consent-open]');
    await page.uncheck('#consent [name="analytics"]');
    await Promise.all([page.waitForNavigation(), page.click('[data-consent="save"]')]);
    await page.waitForTimeout(1500);
    ok(tools.length === 0, 'taking the yes back: the page reloads without it');
    await page.click('.site-footer [data-consent-open]');
    await page.click('[data-consent="all"]');
    await page.waitForTimeout(1500);
    ok(tools.some(u => /googletagmanager/.test(u)) && tools.some(u => /connect\.facebook\.net/.test(u)),
       'Accept all loads both');
    await ctx.close();
  }
  {
    const {ctx, page, tools} = await visitor();
    await page.goto(base + '/dough/login/', {waitUntil: 'load'});
    await page.waitForTimeout(1000);
    ok((await page.$('#consent')) === null && (await page.$('.actionbar')) === null && (await page.$('.sitebar')) === null,
       'the kitchen: no banner, phone bar or new header');
    ok(tools.length === 0, 'the kitchen: no analytics');
    await ctx.close();
  }

  console.log('Header and phone bar');
  {
    const {ctx, page} = await visitor();
    await ctx.addInitScript(() => localStorage.setItem('sol-consent', JSON.stringify({v: 1, t: new Date().toISOString(), analytics: false, ads: false})));
    await page.goto(base + '/about/');
    ok(!(await page.isVisible('.sitebar-logo img')), 'the bar has no small logo at the top of the page');
    await page.mouse.wheel(0, 900);
    await page.waitForTimeout(600);
    ok(await page.isVisible('.sitebar-logo img') && (await page.$eval('.sitebar', b => b.getBoundingClientRect().top)) === 0,
       'scrolled: the bar stays at the top with the small logo');
    ok(await page.isVisible('.sitebar .btn-red'), 'scrolled: Book is still there');
    await page.hover('.sitebar [data-menu-link]');
    ok(await page.isVisible('.sitebar .subnav-drop'), 'Food / Wine / Bar open under Menu');
    await ctx.close();
  }
  {
    const {ctx, page} = await visitor({width: 390, height: 844});
    await ctx.addInitScript(() => localStorage.setItem('sol-consent', JSON.stringify({v: 1, t: new Date().toISOString(), analytics: false, ads: false})));
    await page.goto(base + '/vi/menu/');
    ok(await page.isVisible('.actionbar') && (await page.textContent('.actionbar .btn-red')).trim() === 'Đặt bàn',
       'phones: the Vietnamese phone bar with Đặt bàn');
    ok((await page.getAttribute('.actionbar .btn-red', 'href')) === '/vi/booking/#book', '…which books in Vietnamese');
    await page.click('[data-sheet-open]');
    ok(await page.isVisible('#navsheet'), 'the menu button opens the nav sheet');
    await page.keyboard.press('Escape');
    ok(!(await page.isVisible('#navsheet')), 'Escape closes it');
    await page.goto(base + '/vi/booking/');
    ok((await page.$('.actionbar')) === null, 'no phone bar on the booking page');
    await page.goto(base + '/jobs/host/');
    ok((await page.$('.actionbar')) === null, 'no phone bar on a role page (it has the Apply bar)');
    await ctx.close();
  }

  console.log('Events');
  {
    const {ctx, page} = await visitor();
    await ctx.addInitScript(() => localStorage.setItem('sol-consent', JSON.stringify({v: 1, t: new Date().toISOString(), analytics: true, ads: true})));
    await page.goto(base + '/menu/wine/', {waitUntil: 'load'});
    await page.waitForTimeout(500);
    const events = () => page.evaluate(() => (window.dataLayer || []).filter(e => e[0] === 'event').map(e => e[1]));
    ok((await events()).includes('menu_view'), 'menu_view on a menu page');
    await page.evaluate(() => document.addEventListener('click', e => e.preventDefault()));
    await page.click('.sitebar .btn-red');
    ok((await events()).includes('book_click'), 'book_click from the Book button');
    await page.click('.site-footer a[href^="tel:"]');
    ok((await events()).includes('call_click'), 'call_click from a phone number');
    await page.click('.site-footer a[href^="mailto:"]');
    ok((await events()).includes('email_click'), 'email_click from an email address');
    await page.click('.site-footer a[href*="google.com/maps"]');
    ok((await events()).includes('directions_click'), 'directions_click from a map link');
    await ctx.close();
  }

  await browser.close();
  if (server) server.close();
  console.log(failures ? failures + ' failed' : 'all passed');
  process.exit(failures ? 1 : 0);
}
main().catch(e => { console.error(e); process.exit(1); });
