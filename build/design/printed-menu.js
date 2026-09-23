/* Sol — "Printed menu" header behaviour. No dependencies; load with `defer`.
   1. Desktop: pointing at (or tabbing to) "Menu" shows the Food / Wine / Bar tabs
      under the nav bar. On menu pages (<body class="section-menu">) the tabs are
      always shown and this does nothing.
   2. Mobile (below 761px): the burger opens a full-screen nav sheet.
   3. EN / VI buttons set <html lang>, swap the page's title, description and
      aria-labels, and remember the choice (localStorage "sol-lang"). */
(function () {
  'use strict';
  var root = document.documentElement;
  var header = document.querySelector('[data-site-header]');
  if (!header) return;

  /* 1. Menu tabs --------------------------------------------------------- */
  var trigger = header.querySelector('[data-menu-link]');
  var onMenuPage = document.body.classList.contains('section-menu');
  var desktop = window.matchMedia('(min-width: 761px)');
  var closeTimer = 0;

  function openTabs() {
    clearTimeout(closeTimer);
    header.classList.add('is-open');
  }
  function closeTabs() {
    clearTimeout(closeTimer);
    header.classList.remove('is-open');
  }
  function closeSoon() {
    clearTimeout(closeTimer);
    closeTimer = setTimeout(closeTabs, 250);
  }

  if (trigger && !onMenuPage) {
    trigger.addEventListener('mouseenter', function () { if (desktop.matches) openTabs(); });
    trigger.addEventListener('focus', function () { if (desktop.matches) openTabs(); });
    header.addEventListener('mouseleave', closeSoon);
    // Pointing at or tabbing to any other item in the bar closes the tabs.
    // (Keyboard users reach Food / Wine / Bar through the Menu link: /menu/ always shows them.)
    header.querySelectorAll('.navbar a, .navbar button').forEach(function (el) {
      if (el === trigger) return;
      el.addEventListener('mouseenter', closeSoon);
      el.addEventListener('focus', closeTabs);
    });
    header.querySelectorAll('.subnav').forEach(function (el) {
      el.addEventListener('mouseenter', function () { clearTimeout(closeTimer); });
    });
    header.addEventListener('focusout', function (e) {
      if (!header.contains(e.relatedTarget)) closeTabs();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' || !header.classList.contains('is-open')) return;
      // Move focus first (its focus handler reopens the tabs), then close.
      if (header.contains(document.activeElement) && document.activeElement !== trigger) trigger.focus();
      closeTabs();
    });
  }

  /* 2. Mobile nav sheet -------------------------------------------------- */
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
      var first = items[0];
      var last = items[items.length - 1];
      var inside = sheet.contains(document.activeElement) && document.activeElement !== sheet;
      if (!inside) { (e.shiftKey ? last : first).focus(); e.preventDefault(); }
      else if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
    });

    // Following a link (including /visit/#book on the same page) closes the sheet.
    sheet.querySelectorAll('a[href]').forEach(function (a) {
      a.addEventListener('click', function () { closeSheet(false); });
    });

    var onResize = function (mq) { if (mq.matches) closeSheet(false); };
    if (desktop.addEventListener) desktop.addEventListener('change', onResize);
    else if (desktop.addListener) desktop.addListener(onResize);
  }

  /* 3. EN / VI ----------------------------------------------------------- */
  // Every translated line is in the page twice (data-l="en" / data-l="vi") and
  // site.css shows the one <html lang> asks for. The inline head script applies
  // the saved choice (or a ?lang=vi link) before first paint; this keeps the
  // buttons, <title>, the meta description and every aria-label in step.
  var KEY = 'sol-lang';
  var buttons = document.querySelectorAll('[data-set-lang]');
  var title = document.querySelector('title[data-vi]');
  var desc = document.querySelector('meta[name="description"][data-vi]');

  function setLang(lang, remember) {
    root.lang = lang;
    buttons.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-set-lang') === lang));
    });
    if (title) document.title = title.getAttribute('data-' + lang);
    if (desc) desc.setAttribute('content', desc.getAttribute('data-' + lang));
    document.querySelectorAll('[data-aria-' + lang + ']').forEach(function (el) {
      el.setAttribute('aria-label', el.getAttribute('data-aria-' + lang));
    });
    if (!remember) return;
    try { localStorage.setItem(KEY, lang); } catch (e) { /* private mode */ }
    // A ?lang= or #vi / #en left in the address would undo this choice on reload.
    try {
      var url = new URL(location.href), changed = false;
      if (url.searchParams.has('lang')) { url.searchParams.delete('lang'); changed = true; }
      if (/^#(en|vi)\b/.test(url.hash)) { url.hash = ''; changed = true; }
      if (changed) history.replaceState(history.state, '', url);
    } catch (e) { /* old browser: harmless */ }
  }

  buttons.forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.getAttribute('data-set-lang'), true); });
  });

  setLang(root.lang === 'vi' ? 'vi' : 'en', false);

  // A page restored by Back / Forward keeps the language it was left in; catch up.
  window.addEventListener('pageshow', function (e) {
    if (!e.persisted || /^#(en|vi)\b/.test(location.hash)) return;   // #vi / #en: this page only
    var saved = null;
    try { saved = localStorage.getItem(KEY); } catch (err) { /* private mode */ }
    if ((saved === 'vi' || saved === 'en') && saved !== root.lang) setLang(saved, false);
  });
})();
