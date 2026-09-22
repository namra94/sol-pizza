/* ==========================================================================
   SOL — sol.pizza
   Language switch + mobile nav. No dependencies.
   ========================================================================== */
(function () {
  'use strict';

  var STORE = 'sol-lang';
  var root = document.documentElement;

  function apply(lang) {
    lang = (lang === 'vi') ? 'vi' : 'en';
    root.setAttribute('data-lang', lang);
    root.setAttribute('lang', lang);
    var btns = document.querySelectorAll('.langswitch button');
    for (var i = 0; i < btns.length; i++) {
      btns[i].setAttribute('aria-pressed', String(btns[i].dataset.lang === lang));
    }
    // Keep <title> and meta description in step with the chosen language.
    var t = document.querySelector('meta[data-title-' + lang + ']');
    if (t) document.title = t.getAttribute('data-title-' + lang);
    try { localStorage.setItem(STORE, lang); } catch (e) {}
  }

  // --- language buttons ----------------------------------------------------
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('.langswitch button') : null;
    if (!b) return;
    apply(b.dataset.lang);
    // Reflect the choice in the URL without adding a history entry.
    try {
      var u = new URL(window.location.href);
      if (b.dataset.lang === 'vi') { u.searchParams.set('lang', 'vi'); }
      else { u.searchParams.delete('lang'); }
      window.history.replaceState({}, '', u);
    } catch (err) {}
  });

  // Sync the buttons on load (the <html> attribute is already set by the
  // inline head script, so there is no flash of the wrong language).
  apply(root.getAttribute('data-lang'));

  // --- mobile nav ----------------------------------------------------------
  var toggle = document.querySelector('.navtoggle');
  var nav = document.querySelector('nav.site');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }
})();
