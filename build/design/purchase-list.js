/* Sol — the recent purchase requests (/backoffice/purchases/). No dependencies; load
   with `defer`. Fetches the last 30 (GET /api/backoffice/purchases, worker/backoffice.js)
   and fills a copy of #request for each, newest first: its ref, who sent it and when,
   the supplier, the station, the items, the estimate, and whether it reached Slack.
   build/gen.py (build_purchase_list) writes the template, every line in both
   languages; this fills the dates and numbers in the page's language and redraws them
   when EN / VI switches it. */
(function () {
  'use strict';
  var list = document.getElementById('request-list');
  var tpl = document.getElementById('request');
  if (!list || !tpl) return;
  var root = document.documentElement;
  var requests = [];

  function vi() { return root.lang === 'vi'; }
  function L(en, viText) { return vi() ? viText : en; }
  function vnd(x) { return new Intl.NumberFormat(vi() ? 'vi-VN' : 'en-GB').format(Math.round(x)) + 'đ'; }
  function sent(iso) {                       // Thu 5 Nov, 21:43 / Th 5, 5 thg 11, 21:43 (Hanoi time)
    return new Intl.DateTimeFormat(vi() ? 'vi-VN' : 'en-GB', {
      weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
      timeZone: 'Asia/Ho_Chi_Minh'
    }).format(new Date(iso));
  }
  function needed(when) {                    // YYYY-MM-DD, with HH:MM after it if a time was given
    var day = when.slice(0, 10), time = when.slice(11, 16);
    return new Intl.DateTimeFormat(vi() ? 'vi-VN' : 'en-GB', {
      weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC'
    }).format(new Date(day + 'T00:00:00Z')) + (time ? ', ' + time : '');
  }
  function station(s) { return s === 'Kitchen' ? L('Kitchen', 'Bếp') : s === 'FOH' ? L('FOH', 'Sảnh') : s; }

  // The page's own lines (loading, empty, failed…): data-state, one at a time
  function state(key) {
    document.querySelectorAll('[data-state]').forEach(function (el) {
      el.hidden = el.getAttribute('data-state') !== key;
    });
  }

  function card(r) {
    var el = tpl.content.firstElementChild.cloneNode(true);
    function slot(key, text) {
      el.querySelectorAll('[data-slot="' + key + '"]').forEach(function (s) { s.textContent = text; });
    }
    function cond(key, on) {
      el.querySelectorAll('[data-if="' + key + '"]').forEach(function (s) { s.hidden = !on; });
    }
    slot('ref', r.ref);
    slot('requested_by', r.requested_by);
    slot('time', sent(r.created_at));
    slot('supplier', r.supplier);
    slot('station', station(r.station));
    slot('needed_by', needed(r.needed_by));
    slot('items', String(r.items));
    cond('one', r.items === 1);
    cond('many', r.items !== 1);
    slot('estimate', vnd(r.estimate));
    cond('estimate', r.estimate > 0);
    cond('owner', r.owner_needed);
    ['sent', 'failed', 'sending'].forEach(function (s) { cond(s, r.status === s); });
    cond('dry', r.status === 'dry_run');
    el.classList.toggle('is-failed', r.status === 'failed');
    return el;
  }

  function render() {
    list.textContent = '';
    requests.forEach(function (r) { list.appendChild(card(r)); });
  }

  state('loading');
  fetch('/api/backoffice/purchases', { credentials: 'same-origin', headers: { Accept: 'application/json' } })
    .then(function (res) {
      if (!res.ok) {
        state(res.status === 401 ? 'signed-out' : res.status === 503 ? 'off' : 'failed');
        return;
      }
      return res.json().then(function (d) {
        requests = d.requests || [];
        state(requests.length ? null : 'empty');
        render();
      });
    }).catch(function () { state('failed'); });

  // EN / VI: the dates and numbers follow the page's language.
  if (window.MutationObserver) {
    new MutationObserver(render).observe(root, { attributes: true, attributeFilter: ['lang'] });
  }
})();
