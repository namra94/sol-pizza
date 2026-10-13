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
    await page.goto(base + '/vi/jobs/sous-chef');
    ok(await page.$eval('.vi-note', el => el.closest('[lang]').getAttribute('lang')) === 'vi',
       'a filled role: its Vietnamese note is marked Vietnamese inside the English description');
    await page.goto(base + '/vi//example.com/#en');
    await page.waitForTimeout(300);
    ok(new URL(page.url()).origin === new URL(base).origin,
       '/vi//example.com/#en stays on this site (' + page.url() + ')');
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
    // A visitor from before the banner (or with a yes that has run out) still has the
    // tools' cookies: a no removes them.
    const {ctx, page} = await visitor({width: 1280, height: 800});
    const host = new URL(base).hostname;
    await ctx.addCookies(['_ga', '_ga_SLBWDVH550', '_fbp'].map(name => ({name, value: 'GA1.1.123.456', domain: host, path: '/'})));
    await page.goto(base + '/about/', {waitUntil: 'load'});
    // the banner never hides what has the focus: the footer's last control, focused,
    // sits clear of it
    await page.focus('.site-footer [data-consent-open]');
    await page.waitForTimeout(200);
    const gap = await page.evaluate(() => document.querySelector('#consent').getBoundingClientRect().top -
                                          document.querySelector('.site-footer [data-consent-open]').getBoundingClientRect().bottom);
    ok(gap >= 0, 'the banner never covers the focus: Cookie settings sits ' + Math.round(gap) + 'px above it');
    await page.click('[data-consent="none"]');
    await page.waitForTimeout(300);
    const left = (await ctx.cookies()).map(c => c.name).filter(n => /^_ga|^_fbp/.test(n));
    ok(left.length === 0, 'Reject all removes cookies from before the banner (' + (left.join(', ') || 'none left') + ')');
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
    await page.click('.footer-cols a[href^="mailto:"]');
    ok((await events()).includes('email_click'), 'email_click from an email address');
    await page.click('.site-footer a[href*="google.com/maps"]');
    ok((await events()).includes('directions_click'), 'directions_click from a map link');
    await ctx.close();
  }

  console.log('Enquiry forms and the newsletter');
  {
    const {ctx, page} = await visitor({width: 390, height: 844});
    await ctx.addInitScript(() => localStorage.setItem('sol-consent', JSON.stringify({v: 1, t: new Date().toISOString(), analytics: true, ads: false})));
    const events = () => page.evaluate(() => (window.dataLayer || []).filter(e => e[0] === 'event').map(e => [e[1], e[2] || {}]));
    await page.goto(base + '/vi/private-dining/', {waitUntil: 'load'});
    if (!(await page.$('#enquire form'))) {
      console.log('  (no /private-dining/ in this build: its form is not checked)');
    } else {
      await page.click('#enquire [type="submit"]');
      ok(!(await page.isVisible('#enquire .mailform-done')), 'a form with empty required fields stays put');
      const soon = new Date(Date.now() + 14 * 864e5).toISOString().slice(0, 10);
      await page.fill('#f-private-dining-name', 'Lan');
      await page.fill('#f-private-dining-phone', '0900000000');
      await page.fill('#f-private-dining-date', soon);
      await page.fill('#f-private-dining-guests', '12');
      await page.fill('#f-private-dining-notes', 'Sinh nhật');
      await page.click('#enquire [type="submit"]');
      await page.waitForTimeout(300);
      const text = await page.inputValue('#enquire .mailform-done textarea');
      ok(/^Gửi tới: hello@sol\.pizza\nTiêu đề: Private dining — Lan\n/.test(text),
         'the email: to the enquiries inbox, the subject in English with the name (the labels in Vietnamese)');
      ok(/Họ tên: Lan/.test(text) && /Số khách: 12/.test(text) && /Thông tin thêm: Sinh nhật/.test(text) && !/Email:/.test(text),
         'the details in Vietnamese, the empty ones left out');
      ok(await page.evaluate(() => document.querySelector('#enquire .mailform-done').contains(document.activeElement)),
         'after Send the focus moves to what happened, and the copy');
      await page.click('#enquire [type="submit"]');
      const sent = (await events()).filter(e => e[0] === 'enquiry_submit');
      ok(sent.length === 1 && sent[0][1].content_category === 'Private dining',
         'enquiry_submit once per form, as Private dining (' + sent.length + ')');
      await page.evaluate(() => document.addEventListener('click', e => e.preventDefault()));
      await page.click('.footer-news .btn');
      ok((await events()).some(e => e[0] === 'newsletter_signup'), 'newsletter_signup from the footer');
      ok(/^mailto:hello@sol\.pizza\?subject=Newsletter&body=Vui/.test(await page.getAttribute('.footer-news .btn', 'href')),
         'the newsletter email asks, in Vietnamese, to be added');
    }
    await page.goto(base + '/booking/');
    const live = await page.evaluate(() => !!document.querySelector('.book-widget') || document.documentElement.classList.contains('is-open'));
    if (live) console.log('  (online booking or opening day: no opening-week form to check)');
    else ok(await page.isVisible('#f-opening-week-name'), 'before online booking: the opening-week form on /booking/');
    const group = await page.$('.offer-note a');
    ok(!group || (await group.getAttribute('href')) === '/private-dining/#enquire', 'seven or more: the group enquiry');
    await ctx.close();
  }

  console.log('Pages: events, the home page, 404');
  {
    const {ctx, page} = await visitor({width: 1280, height: 900});
    await ctx.addInitScript(() => localStorage.setItem('sol-consent', JSON.stringify({v: 1, t: new Date().toISOString(), analytics: false, ads: false})));
    const r = await page.goto(base + '/events/', {waitUntil: 'load'});
    if (r.status() !== 200) {
      console.log('  (no /events/ in this build: not checked)');
    } else {
      // Each edition in the list carries its last night; the check moves the clock past it
      const eds = await page.$$eval('.ev-up[data-ev]', els => els.map(e => e.getAttribute('data-ev')));
      const upNow = await page.$$eval('.ev-up[data-ev]', els => els.filter(e => e.offsetParent).length);
      ok(eds.length === 0 || upNow === eds.length, 'events: what is coming up shows under Coming up (' + upNow + ')');
      if (eds.length) {
        const ctx2 = await browser.newContext({viewport: {width: 1280, height: 900}});
        await ctx2.route(/googletagmanager|google-analytics|facebook|typekit/, x => x.fulfill({status: 204, body: ''}));
        const later = await ctx2.newPage();
        await later.clock.setFixedTime(new Date('2031-01-01T00:00:00+07:00'));
        await later.goto(base + '/events/', {waitUntil: 'load'});
        const state = await later.evaluate(() => ({
          up: [...document.querySelectorAll('.ev-up[data-ev]')].filter(e => e.offsetParent).length,
          past: [...document.querySelectorAll('.ev-past[data-ev]')].filter(e => e.offsetParent).length,
          none: !!document.querySelector('.ev-none-msg') && !!document.querySelector('.ev-none-msg').offsetParent}));
        ok(state.up === 0 && state.past >= eds.length && state.none,
           'events: once over, an edition moves to Past by itself, and "nothing announced" shows (' + JSON.stringify(state) + ')');
        await later.goto(base + '/', {waitUntil: 'load'});
        ok(!(await later.isVisible('.next-ev')), 'the home page drops the next Eclipse once it is over');
        await ctx2.close();
      }
    }
    await page.goto(base + '/', {waitUntil: 'load'});
    const cards = await page.$$eval('.home-paths .card a', as => as.map(a => a.getAttribute('href')));
    ok(cards.length === 3, 'home: three ways in (' + cards.join(' ') + ')');
    ok(await page.isVisible('.today'), 'home: the opening date or today\'s hours under the buttons');
    await page.goto(base + '/no-such-page/');
    const paths = await page.$$eval('.paths-404 a', as => as.map(a => a.getAttribute('href')));
    ok(paths.length >= 3 && paths.includes('/'), '404: the main pages to go to (' + paths.join(' ') + ')');
    await ctx.close();
  }

  await browser.close();
  if (server) server.close();
  console.log(failures ? failures + ' failed' : 'all passed');
  process.exit(failures ? 1 : 0);
}
main().catch(e => { console.error(e); process.exit(1); });
