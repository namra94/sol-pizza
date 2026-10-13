/* Sol — the guest pages' script (every page but the kitchen's). No dependencies;
   loaded with defer. The head script (build/gen.py, _head_script()) has already
   set <html> classes before first paint: consent-ask (no cookie choice yet),
   is-open (from opening day), ann-<id> (an announcement showing), js.
   1. The header: on a wide screen (1024px and up), Food / Wine / Bar under Menu
      and the bar's small logo once the big one has scrolled away; narrower, the
      nav sheet behind the menu button.
   2. EN · VI: links to the page in the other language; the choice is remembered
      (localStorage sol-lang), and the home page opens in it next time.
   3. Cookies: the banner, the choice (localStorage sol-consent), and the tools it
      allows. Nothing optional loads before a choice: Google Analytics (gtag.js,
      consent mode in its basic form) only after a yes to Analytics, the Meta Pixel
      (and pixel.js, the careers events) only after a yes to Advertising.
   4. Events: what guests do (book, call, directions, menus, enquiries…), to GA4
      and, with the Advertising yes, to Meta. ?debug_analytics=1 logs every one to
      the console (and turns on GA4 DebugView); ?debug_analytics=0 stops it. And the
      enquiry forms, which write an email (4b).
   5. Announcements: closing one keeps it closed (localStorage sol-ann-<id>).
   6. Slow fades for .reveal, never for anyone who asks for less motion. */
(function () {
  'use strict';
  var root = document.documentElement;
  var store = null;
  try { store = window.localStorage; } catch (e) { /* blocked */ }
  function get(k) { try { return store.getItem(k); } catch (e) { return null; } }
  function put(k, v) { try { store.setItem(k, v); } catch (e) { /* private mode */ } }
  function drop(k) { try { store.removeItem(k); } catch (e) { /* private mode */ } }
  var wide = window.matchMedia('(min-width: 1024px)');

  /* 1. The header ------------------------------------------------------- */
  var bar = document.querySelector('[data-sitebar]');
  if (bar) {
    var trigger = bar.querySelector('[data-menu-link]');
    var timer = 0;
    var openTabs = function () { clearTimeout(timer); bar.classList.add('is-open'); };
    var closeTabs = function () { clearTimeout(timer); bar.classList.remove('is-open'); };
    var closeSoon = function () { clearTimeout(timer); timer = setTimeout(closeTabs, 250); };
    if (trigger) {
      trigger.addEventListener('mouseenter', function () { if (wide.matches) openTabs(); });
      trigger.addEventListener('focus', function () { if (wide.matches) openTabs(); });
      bar.addEventListener('mouseleave', closeSoon);
      // Pointing at or tabbing to anything else in the bar closes the tabs. (Keyboard
      // users reach Food / Wine / Bar through the Menu link: /menu/ always shows them.)
      bar.querySelectorAll('.sitebar-in a, .sitebar-in button').forEach(function (el) {
        if (el === trigger) return;
        el.addEventListener('mouseenter', closeSoon);
        el.addEventListener('focus', closeTabs);
      });
      bar.querySelectorAll('.subnav').forEach(function (el) {
        el.addEventListener('mouseenter', function () { clearTimeout(timer); });
      });
      bar.addEventListener('focusout', function (e) { if (!bar.contains(e.relatedTarget)) closeTabs(); });
      document.addEventListener('keydown', function (e) {
        if (e.key !== 'Escape' || !bar.classList.contains('is-open')) return;
        if (bar.contains(document.activeElement) && document.activeElement !== trigger) trigger.focus();
        closeTabs();
      });
    }
    // The small logo appears once the masthead has scrolled out of sight
    var mark = document.querySelector('.sitebar-mark');
    if (mark && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        bar.classList.toggle('is-stuck', !entries[entries.length - 1].isIntersecting);
      }).observe(mark);
    }
  }

  var sheet = document.getElementById('navsheet');
  var burger = document.querySelector('[data-sheet-open]');
  if (sheet && burger) {
    var closeBtn = sheet.querySelector('[data-sheet-close]');
    var openSheet = function () {
      sheet.hidden = false;
      burger.setAttribute('aria-expanded', 'true');
      root.classList.add('sheet-open');
      (closeBtn || sheet).focus();
    };
    var closeSheet = function (returnFocus) {
      if (sheet.hidden) return;
      sheet.hidden = true;
      burger.setAttribute('aria-expanded', 'false');
      root.classList.remove('sheet-open');
      if (returnFocus !== false) burger.focus();
    };
    burger.addEventListener('click', openSheet);
    if (closeBtn) closeBtn.addEventListener('click', function () { closeSheet(); });
    // Listen on the document: a tap on empty space inside the sheet moves focus to <body>.
    document.addEventListener('keydown', function (e) {
      if (sheet.hidden) return;
      if (e.key === 'Escape') { closeSheet(); return; }
      if (e.key !== 'Tab') return;
      var items = sheet.querySelectorAll('a[href], button:not([disabled])');
      var first = items[0], last = items[items.length - 1];
      var inside = sheet.contains(document.activeElement) && document.activeElement !== sheet;
      if (!inside) { (e.shiftKey ? last : first).focus(); e.preventDefault(); }
      else if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
    });
    // Following a link (including one to the page it's on) closes the sheet.
    sheet.querySelectorAll('a[href]').forEach(function (a) {
      a.addEventListener('click', function () { closeSheet(false); });
    });
    var onResize = function (mq) { if (mq.matches) closeSheet(false); };
    if (wide.addEventListener) wide.addEventListener('change', onResize);
    else if (wide.addListener) wide.addListener(onResize);
  }

  /* 2. EN · VI ---------------------------------------------------------- */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('[data-lang-link]');
    if (a) put('sol-lang', a.getAttribute('data-lang-link'));
  });

  /* 3. Cookies ---------------------------------------------------------- */
  var CONSENT_VERSION = 1;            // build/gen.py CONSENT_VERSION: the head script checks it too
  var GA = '__GA_ID__', PIXEL = '__FB_PIXEL__';
  var debugParam = /[?&]debug_analytics=([01])(?:&|$)/.exec(location.search);
  if (debugParam) { if (debugParam[1] === '1') put('sol-debug', '1'); else drop('sol-debug'); }
  var debug = get('sol-debug') === '1';

  function readConsent() {
    try {
      var c = JSON.parse(get('sol-consent'));
      if (c && c.v === CONSENT_VERSION && Date.now() - Date.parse(c.t) < 31536e6) return c;
    } catch (e) { /* none, or unreadable */ }
    return null;
  }
  var consent = readConsent();
  var started = {};
  var pending = [];

  function addScript(src) {
    var s = document.createElement('script');
    s.async = true;
    s.src = src;
    document.head.appendChild(s);
  }

  // The tools' queues start straight away, so nothing a guest does is lost; their
  // scripts load once the page has finished loading, out of the way of the page.
  function startAnalytics() {
    if (started.ga) return;
    started.ga = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    var ads = consent.ads ? 'granted' : 'denied';
    window.gtag('consent', 'default', {analytics_storage: 'granted', ad_storage: ads, ad_user_data: ads,
                                       ad_personalization: ads});
    window.gtag('js', new Date());
    window.gtag('config', GA, debug ? {debug_mode: true} : {});
    whenLoaded(function () { addScript('https://www.googletagmanager.com/gtag/js?id=' + GA); });
  }

  function startPixel() {
    if (started.px) return;
    started.px = true;
    // Meta's base code, its script loaded once the page has
    var n = window.fbq = function () {
      if (n.callMethod) n.callMethod.apply(n, arguments); else n.queue.push(arguments);
    };
    if (!window._fbq) window._fbq = n;
    n.push = n; n.loaded = true; n.version = '2.0'; n.queue = [];
    window.fbq('init', PIXEL);
    window.fbq('track', 'PageView');
    whenLoaded(function () {
      addScript('https://connect.facebook.net/en_US/fbevents.js');
      addScript('/pixel.js');             // the careers events (ViewContent, ExpandJD, Lead)
    });
  }

  function whenLoaded(fn) {
    if (document.readyState === 'complete') setTimeout(fn, 0);
    else window.addEventListener('load', function () { setTimeout(fn, 0); });
  }

  function startTools() {
    if (!consent) return;
    if (consent.analytics) startAnalytics();
    if (consent.ads) startPixel();
    var queued = pending;
    pending = [];
    queued.forEach(function (e) { send(e[0], e[1]); });
  }

  // Taking a yes back: remove what the tool left in the browser, then reload without it.
  function forget(analytics, ads) {
    var names = document.cookie.split(';').map(function (c) { return c.split('=')[0].trim(); });
    var host = location.hostname.split('.');
    names.forEach(function (name) {
      var mine = (analytics && /^(_ga|_gid|_gat|_gcl_)/.test(name)) || (ads && /^(_fbp|_fbc)$/.test(name));
      if (!mine) return;
      for (var i = 0; i < host.length - 1; i++) {
        var domain = host.slice(i).join('.');
        document.cookie = name + '=; Max-Age=0; path=/; domain=' + domain;
        document.cookie = name + '=; Max-Age=0; path=/; domain=.' + domain;
      }
      document.cookie = name + '=; Max-Age=0; path=/';
    });
    if (ads) { drop('lastExternalReferrer'); drop('lastExternalReferrerTime'); }
  }

  var banner = document.getElementById('consent');
  var settings = document.getElementById('consent-settings');
  var opener = null;

  function showSettings(show) {
    if (!banner || !settings) return;
    settings.hidden = !show;
    var toggle = banner.querySelector('[data-consent="settings"]');
    var saveBtn = banner.querySelector('[data-consent="save"]');
    if (toggle) toggle.setAttribute('aria-expanded', String(show));
    if (saveBtn) saveBtn.hidden = !show;
    if (show) {
      settings.querySelector('[name="analytics"]').checked = !!(consent && consent.analytics);
      settings.querySelector('[name="ads"]').checked = !!(consent && consent.ads);
    }
  }

  function choose(analytics, ads) {
    var before = consent;
    consent = {v: CONSENT_VERSION, t: new Date().toISOString(), analytics: !!analytics, ads: !!ads};
    put('sol-consent', JSON.stringify(consent));
    var hadFocus = banner && banner.contains(document.activeElement);
    root.classList.remove('consent-ask', 'consent-open');
    showSettings(false);
    if (debug) console.log('[sol] cookie choice', JSON.stringify(consent));
    var withdrawn = before && ((before.analytics && !consent.analytics) || (before.ads && !consent.ads));
    if (withdrawn) {
      forget(before.analytics && !consent.analytics, before.ads && !consent.ads);
      location.reload();
      return;
    }
    startTools();
    if (hadFocus) {
      if (opener && document.contains(opener)) opener.focus();
      else {
        var main = document.getElementById('main');
        if (main) { main.setAttribute('tabindex', '-1'); main.focus({preventScroll: true}); }
      }
    }
    opener = null;
  }

  if (banner) {
    banner.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('[data-consent]');
      if (!b) return;
      var what = b.getAttribute('data-consent');
      if (what === 'all') choose(true, true);
      else if (what === 'none') choose(false, false);
      else if (what === 'settings') showSettings(settings.hidden);
      else if (what === 'save') {
        choose(settings.querySelector('[name="analytics"]').checked, settings.querySelector('[name="ads"]').checked);
      }
    });
  }
  // Cookie settings (the footer, the cookie notice): the banner again, its choices open
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-consent-open]');
    if (!b || !banner) return;
    opener = b;
    root.classList.add('consent-open');
    showSettings(true);
    var first = banner.querySelector('input, button');
    if (first) first.focus();
  });
  if (consent) startTools();

  /* 4. Events ----------------------------------------------------------- */
  // GA4 event name: the Meta event it maps to, with the Advertising yes only.
  var META = {
    book_click: ['trackCustom', 'BookClick'],
    booking_complete: ['track', 'Schedule'],
    call_click: ['track', 'Contact', {contact_method: 'call'}],
    zalo_click: ['track', 'Contact', {contact_method: 'zalo'}],
    whatsapp_click: ['track', 'Contact', {contact_method: 'whatsapp'}],
    email_click: ['track', 'Contact', {contact_method: 'email'}],
    directions_click: ['track', 'FindLocation'],
    menu_view: ['track', 'ViewContent', {content_type: 'menu'}],
    newsletter_signup: ['track', 'Lead', {content_category: 'Newsletter'}],
    enquiry_submit: ['track', 'Lead', {content_category: 'Private dining'}]
  };

  function send(name, params) {
    if (consent.analytics && window.gtag) window.gtag('event', name, params);
    var m = META[name];
    // A click on the jobs inbox is pixel.js's Lead already
    if (consent.ads && window.fbq && m && params.address !== 'jobs@sol.pizza') {
      var data = {};
      [m[2] || {}, params].forEach(function (o) { for (var k in o) data[k] = o[k]; });
      window.fbq(m[0], m[1], data);
    }
  }

  // Events wait on this page until there is a choice, and go nowhere without a yes.
  function track(name, params) {
    params = params || {};
    if (debug) {
      console.log('[sol] event', name, JSON.stringify(params),
                  !consent ? '(waiting for a cookie choice)' :
                  (consent.analytics ? 'GA4 ' : '') + (consent.ads ? 'Meta' : '') ||
                  '(not sent: no to both)');
    }
    if (!consent) { pending.push([name, params]); return; }
    send(name, params);
  }
  window.solTrack = track;

  function where(el) {
    if (el.closest('.actionbar')) return 'phone_bar';
    if (el.closest('.sitebar, .site-top, .navsheet')) return 'header';
    if (el.closest('.site-footer')) return 'footer';
    if (el.closest('.ann')) return 'announcement';
    return 'page';
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href], [data-track]');
    if (!a) return;
    var name = a.getAttribute('data-track');
    var href = a.getAttribute('href') || '';
    if (!name) {
      if (/^tel:/.test(href)) name = 'call_click';
      else if (/^mailto:/.test(href)) name = 'email_click';
      else if (/^https:\/\/zalo\.me\//.test(href)) name = 'zalo_click';
      else if (/^https:\/\/wa\.me\//.test(href)) name = 'whatsapp_click';
      else if (/^https:\/\/(www\.)?google\.[a-z.]+\/maps|^https:\/\/maps\.app\.goo\.gl\//.test(href)) name = 'directions_click';
      else if (/^(\/vi)?\/booking\/(#|$)/.test(href)) name = 'book_click';
    }
    if (!name) return;
    var params = {link_location: where(a)};
    if (name === 'email_click') params.address = href.replace(/^mailto:/, '').split('?')[0];
    track(name, params);
  }, true);

  var section = document.body.getAttribute('data-menu');
  if (section) track('menu_view', {menu_section: section});

  /* 4b. Enquiry forms --------------------------------------------------- */
  // A form that writes an email (gen.py, mailform()): the guest's email app opens with
  // the details in the page's language and the subject in English (the inbox is sorted
  // by it). Nothing is stored or sent from here. The message also appears on the page,
  // to copy, in case no email app opens.
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form.matches || !form.matches('form[data-mailform]')) return;
    e.preventDefault();
    var lines = [];
    form.querySelectorAll('input, textarea, select').forEach(function (el) {
      var value = (el.value || '').trim();
      if (!el.name || !value) return;
      var label = form.querySelector('label[for="' + el.id + '"] .field-name');
      lines.push((label ? label.textContent.trim() : el.name) + ': ' + value);
    });
    var who = form.querySelector('[name="name"]');
    var to = form.getAttribute('data-to');
    var subject = form.getAttribute('data-subject') + (who && who.value.trim() ? who.value.trim() : '');
    var body = lines.join('\n');
    track('enquiry_submit', {enquiry_type: form.getAttribute('data-mailform')});
    var done = form.querySelector('.mailform-done');
    if (done) {
      var copy = done.querySelector('textarea');
      copy.rows = Math.min(10, lines.length + 3);
      copy.value = 'To: ' + to + '\nSubject: ' + subject + '\n\n' + body;
      done.hidden = false;
    }
    window.location.href = 'mailto:' + to + '?subject=' + encodeURIComponent(subject) +
      '&body=' + encodeURIComponent(body.replace(/\n/g, '\r\n'));
  });

  /* 5. Announcements ---------------------------------------------------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-ann-close]');
    if (!b) return;
    var id = b.getAttribute('data-ann-close');
    put('sol-ann-' + id, '1');
    root.classList.remove('ann-' + id);
  });

  /* 6. Slow fades ------------------------------------------------------- */
  var fades = document.querySelectorAll('.reveal');
  if (fades.length && 'IntersectionObserver' in window &&
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); seen.unobserve(e.target); }
      });
    }, {rootMargin: '0px 0px -8% 0px'});
    fades.forEach(function (el) { seen.observe(el); });
  } else {
    fades.forEach(function (el) { el.classList.add('is-in'); });
  }
})();
