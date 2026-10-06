/* Sol — the dough log (/dough/log/). No dependencies; load with `defer`.
   Fetches the log from the Worker (GET /api/dough/log, newest first, a page at a
   time) and fills a copy of #log-entry for each batch, under a heading for each
   day. build/gen.py (build_dough_log) writes the template, every line in both
   languages; this fills the numbers in the page's language and redraws them
   when EN / VI switches it. Delete asks first, then DELETE /api/dough/log/<id>. */
(function () {
  'use strict';
  var list = document.getElementById('log-list');
  var tpl = document.getElementById('log-entry');
  if (!list || !tpl) return;
  var root = document.documentElement;
  var more = document.querySelector('[data-more]');
  var entries = [], cursor = '', loading = false;

  function vi() { return root.lang === 'vi'; }
  var formats = {};
  function fmt(x, digits) {                  // 6,301 / 6.301; 2.8 / 2,8
    var lang = vi() ? 'vi-VN' : 'en-GB', key = lang + digits;
    if (!formats[key]) formats[key] = new Intl.NumberFormat(lang, { maximumFractionDigits: digits });
    return formats[key].format(x + 0);
  }
  function grams(x) { return fmt(x, x < 100 ? 1 : 0); }
  function dayName(day) {                    // Tuesday 6 October 2026 / Thứ Ba, 6 tháng 10, 2026
    return new Intl.DateTimeFormat(vi() ? 'vi-VN' : 'en-GB', {
      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'
    }).format(new Date(day + 'T00:00:00Z'));
  }
  function time(iso) {                       // 14:32, Hanoi time
    return new Intl.DateTimeFormat(vi() ? 'vi-VN' : 'en-GB', {
      hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Ho_Chi_Minh'
    }).format(new Date(iso));
  }

  // The page's own lines (loading, empty, failed…): data-state, one at a time
  function state(key) {
    document.querySelectorAll('[data-state]').forEach(function (el) {
      el.hidden = el.getAttribute('data-state') !== key;
    });
  }

  /* One batch -------------------------------------------------------------- */
  function card(e) {
    var el = tpl.content.firstElementChild.cloneNode(true);
    var b = e.batch || {}, w = e.weights || {};
    function slot(key, text) {
      el.querySelectorAll('[data-slot="' + key + '"]').forEach(function (s) { s.textContent = text; });
    }
    function cond(key, on) {
      el.querySelectorAll('[data-if="' + key + '"]').forEach(function (s) { s.hidden = !on; });
    }
    var ww = b.whole_wheat || 0, rye = b.rye || 0, pf = b.preferment && b.preferment !== 'none';
    slot('balls', fmt(e.balls, 0));
    slot('ball', fmt(e.ball_g, 1));
    slot('dough_kg', fmt(e.dough_g / 1000, 1));
    slot('made_by', e.made_by);
    slot('time', time(e.logged_at));
    slot('pizza_pct', fmt(100 - ww - rye, 1));
    slot('ww_pct', fmt(ww, 1));
    slot('rye_pct', fmt(rye, 1));
    cond('ww', ww > 0);
    cond('rye', rye > 0);
    ['hydration', 'salt', 'yeast', 'oil', 'sugar', 'pf_flour', 'pf_hydration', 'pf_yeast'].forEach(function (k) {
      slot(k, fmt(b[k] || 0, 3));
    });
    cond('oil', b.oil > 0);
    cond('sugar', b.sugar > 0);
    cond('pf', pf);
    slot('pf_name', pf ? b.preferment.charAt(0).toUpperCase() + b.preferment.slice(1) : '');
    slot('kitchen_c', fmt(e.kitchen_c, 1));
    slot('humidity', fmt(e.humidity, 1));
    cond('water', w.water_c !== undefined);
    slot('water_c', w.water_c !== undefined ? fmt(Math.round(w.water_c), 0) : '');
    cond('ice', w.ice > 0);
    slot('ice', grams(w.ice || 0));
    cond('dough_c', e.dough_c !== null && e.dough_c !== undefined);
    slot('dough_c', e.dough_c !== null && e.dough_c !== undefined ? fmt(e.dough_c, 1) : '');
    cond('target', b.t_dough !== undefined);
    slot('t_dough', b.t_dough !== undefined ? fmt(b.t_dough, 1) : '');
    slot('pizza_g', grams(w.pizza || 0));
    slot('ww_g', grams(w.whole_wheat || 0));
    slot('rye_g', grams(w.rye || 0));
    slot('water_g', grams(w.water || 0));
    slot('salt_g', grams(w.salt || 0));
    slot('yeast_g', grams(w.yeast || 0));
    slot('oil_g', grams(w.oil || 0));
    slot('sugar_g', grams(w.sugar || 0));
    cond('notes', !!e.notes);
    slot('notes', e.notes || '');
    var del = el.querySelector('[data-delete]');
    del.addEventListener('click', function () { remove(e, del); });
    return el;
  }

  /* The list, a heading per day -------------------------------------------- */
  function render() {
    list.textContent = '';
    var day = null, group = null;
    entries.forEach(function (e) {
      if (e.day !== day) {
        day = e.day;
        group = document.createElement('section');
        group.className = 'log-day';
        var h = document.createElement('h2');
        h.className = 'log-day-h';
        h.textContent = dayName(day);
        group.appendChild(h);
        list.appendChild(group);
      }
      group.appendChild(card(e));
    });
  }

  function failed(res) {
    state(res && res.status === 401 ? 'signed-out' : res && res.status === 503 ? 'off' : 'failed');
  }

  function load() {
    if (loading) return;
    loading = true;
    more.disabled = true;
    if (!entries.length) state('loading');
    fetch('/api/dough/log' + (cursor ? '?before=' + encodeURIComponent(cursor) : ''), {
      credentials: 'same-origin', headers: { Accept: 'application/json' }
    }).then(function (res) {
      if (!res.ok) { failed(res); return; }
      return res.json().then(function (page) {
        entries = entries.concat(page.entries);
        var last = entries[entries.length - 1];
        cursor = page.more && last ? last.day + '.' + last.id : '';
        more.hidden = !page.more;
        state(entries.length ? null : 'empty');
        render();
      });
    }, function () { failed(null); }).then(function () {
      loading = false;
      more.disabled = false;
    });
  }

  function remove(e, button) {
    if (!window.confirm(button.getAttribute(vi() ? 'data-confirm-vi' : 'data-confirm-en'))) return;
    button.disabled = true;
    fetch('/api/dough/log/' + e.id, { method: 'DELETE', credentials: 'same-origin' }).then(function (res) {
      if (!res.ok) {
        button.disabled = false;
        if (res.status === 401) state('signed-out');
        else state('delete-failed');
        return;
      }
      entries = entries.filter(function (x) { return x.id !== e.id; });
      state(entries.length ? null : 'empty');
      render();
    }, function () {
      button.disabled = false;
      state('delete-failed');
    });
  }

  more.addEventListener('click', load);

  // EN / VI: the dates and numbers follow the page's language.
  if (window.MutationObserver) {
    new MutationObserver(render).observe(root, { attributes: true, attributeFilter: ['lang'] });
  }

  load();
})();
