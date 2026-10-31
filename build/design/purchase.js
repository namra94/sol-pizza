/* Sol — the purchase request (/backoffice/purchase/). No dependencies; load with `defer`.
   build/gen.py (build_purchase) writes the page, every line in both languages, and
   #p-item, the template for an item's row. Staff ask for items only: who's asking,
   the station, when it's needed, and each item, how much, in what unit, with a note.
   Management chooses the supplier and the brand when they order, so nothing here
   names either, and there are no prices.
   To help, the boxes suggest what earlier requests said (GET /api/backoffice/form,
   worker/backoffice.js): the names for Requested by (the last one used is remembered
   on the phone), and for an item the ones asked for before at the station picked
   (with none picked yet, at any station), most-asked first, found as you type in
   English or Vietnamese, with or without the accents. Picking one fills in its usual
   unit, unless one has been chosen already. If they don't load, the form works the
   same without them, and says nothing.
   Preview asks the Worker for the exact message (POST /api/backoffice/purchase with
   preview: true) and shows it as Slack will; Send posts it with an id made here, kept
   until the request has gone through, so a second tap or a retry never posts it
   twice. Nothing typed is lost on an error. */
(function () {
  'use strict';
  var form = document.getElementById('purchase');
  var tpl = document.getElementById('p-item');
  var done = document.getElementById('p-done');
  if (!form || !tpl || !done) return;
  var root = document.documentElement;
  var OTHER = 'other';                  // the unit list's "Other…"
  var MAX_ROWS = 30, MAX_QTY = 100000, MAX_NAME = 60, MAX_ITEM = 80, MAX_UNIT = 20;
  var SHOWN = 60;                       // suggestions in a list at most
  var NAME_KEY = 'sol-office-name';     // who asked last on this phone (localStorage)
  // the accents, taken off to search: the combining marks U+0300 to U+036F
  var MARKS = new RegExp('[' + String.fromCharCode(0x300) + '-' + String.fromCharCode(0x36f) + ']', 'g');

  var els = {
    who: form.elements.who, whoList: document.getElementById('p-who-list'), seg: form.querySelector('.dough-seg'),
    day: form.elements.day, time: form.elements.time, note: form.elements.note,
    list: document.getElementById('p-items'), add: form.querySelector('[data-add]'),
    previewBox: document.getElementById('p-preview-box'), message: document.getElementById('p-preview'),
    sentMessage: done.querySelector('[data-out="sent_message"]'),
    preview: form.querySelector('[data-preview]'), send: form.querySelector('[data-send]')
  };
  var people = [], asked = [];          // from earlier requests: names; items, as {station, item, unit, count}
  var whoBox = null, rows = [], counter = 0;
  var requestId = null;                 // made at the first Send, kept until it has gone through
  var previewed = null;                 // the request the preview shows (body(), as JSON)
  var messages = {};                    // the messages showing, as the Worker wrote them: {text, station}
  var busy = false, tried = false, sentRows = [];

  /* Words and numbers in the page's language --------------------------------- */
  function vi() { return root.lang === 'vi'; }
  function L(en, viText) { return vi() ? viText : en; }
  function hanoiToday() { return new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10); }

  // "2,5", "2.5" and " 2.5 " are all 2.5; anything else is NaN
  function parse(s) {
    s = String(s).replace(/\s+/g, '').replace(',', '.');
    return /^(\d+\.?\d*|\.\d+)$/.test(s) ? parseFloat(s) : NaN;
  }
  // A name as the Worker reads it: one line, spaces tidied, Vietnamese in one form
  function clean(s) {
    s = String(s).replace(/\s+/g, ' ').trim();
    return s.normalize ? s.normalize('NFC') : s;
  }
  // To search: no accents, no capitals, đ as d
  function norm(s) {
    s = clean(s).toLowerCase();
    if (s.normalize) s = s.normalize('NFD').replace(MARKS, '');
    return s.replace(/đ/g, 'd');
  }
  // One item however it's spelt, as the Worker counts them: whatever the capitals
  // and spaces, but not the accents (bơ is butter, bò is beef)
  function key(s) { return clean(s).toLowerCase(); }

  // The unit list's names, by code (from the template's options): [English, Vietnamese]
  var unitNames = {};
  tpl.content.querySelectorAll('option[data-vi]').forEach(function (o) {
    if (o.value && o.value !== OTHER) unitNames[o.value] = [o.getAttribute('data-en'), o.getAttribute('data-vi')];
  });
  function listed(u) { return Object.prototype.hasOwnProperty.call(unitNames, u); }
  function unitName(u) { return listed(u) ? L(unitNames[u][0], unitNames[u][1]) : u; }

  // An <option> and a placeholder can't hold the page's two languages: theirs are in
  // data-en and data-vi (data-placeholder-en and -vi), and swapped here
  function words(scope) {
    scope.querySelectorAll('option[data-vi]').forEach(function (o) {
      o.textContent = o.getAttribute(vi() ? 'data-vi' : 'data-en');
    });
    scope.querySelectorAll('[data-placeholder-vi]').forEach(function (el) {
      el.placeholder = el.getAttribute(vi() ? 'data-placeholder-vi' : 'data-placeholder-en');
    });
  }

  // A message as Slack shows it: the approver's mention as @ and the role (Slack shows
  // their name), and &amp;, &lt; and &gt; as the characters they stand for
  function slackShown(m) {
    var role = m.station === 'Kitchen' ? L('Kitchen approver', 'người duyệt của Bếp')
      : L('Bar & FOH approver', 'người duyệt của Bar và Sảnh');
    return m.text.replace(/<@[UW][A-Z0-9]+>/g, function () { return '@' + role; })
      .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
  }
  function showMessages() {
    if (messages.preview) els.message.textContent = slackShown(messages.preview);
    if (messages.sent) els.sentMessage.textContent = slackShown(messages.sent);
  }

  /* The page's lines ------------------------------------------------------- */
  function show(cond, on) {
    document.querySelectorAll('[data-if="' + cond + '"]').forEach(function (el) { el.hidden = !on; });
  }
  function out(name, text) {
    document.querySelectorAll('[data-out="' + name + '"]').forEach(function (el) { el.textContent = text; });
  }
  // One line of a group at a time (data-state, data-send-line); null hides them all
  function only(attr, name) {
    document.querySelectorAll('[' + attr + ']').forEach(function (el) { el.hidden = el.getAttribute(attr) !== name; });
  }
  var line = null;                      // the line under Preview and Send that's showing
  function sendLine(name) {
    line = name;
    only('data-send-line', name);
  }
  function mark(el, on) {
    el.setAttribute('aria-invalid', String(on));
    el.parentNode.classList.toggle('is-invalid', on);
  }
  function station() { return (form.querySelector('input[name="station"]:checked') || {}).value; }

  /* Suggestions ------------------------------------------------------------ */
  // A box that suggests as it's typed in: its list (ul[role=listbox]) right under it,
  // what to suggest from choices() ({text}, and the unit for an item), and picked(c)
  // once one is picked. While there's nothing to suggest it's a plain text box.
  function suggest(input, list, choices, picked) {
    var box = { input: input, list: list, choices: choices, picked: picked, shown: [], active: -1 };
    input.addEventListener('input', function () { open(box, false); });
    input.addEventListener('focus', function () { open(box, true); });
    input.addEventListener('blur', function () {
      setTimeout(function () { if (document.activeElement !== input) close(box); }, 150);
    });
    input.addEventListener('keydown', function (e) {
      if (!input.hasAttribute('role')) return;
      var k = e.key;
      if (k === 'ArrowDown' || k === 'Down') { e.preventDefault(); move(box, 1); }
      else if (k === 'ArrowUp' || k === 'Up') { e.preventDefault(); move(box, -1); }
      else if (k === 'Enter' && !list.hidden && box.active >= 0) { e.preventDefault(); choose(box, box.shown[box.active]); }
      else if ((k === 'Escape' || k === 'Esc') && !list.hidden) { e.preventDefault(); close(box); }
    });
    arm(box);
    return box;
  }

  // A list to pick from while there's something to suggest, else a plain text box
  function arm(box) {
    var input = box.input;
    if (box.choices().length) {
      input.setAttribute('role', 'combobox');
      input.setAttribute('aria-autocomplete', 'list');
      input.setAttribute('aria-expanded', 'false');
      input.setAttribute('aria-controls', box.list.id);
    } else {
      ['role', 'aria-autocomplete', 'aria-expanded', 'aria-controls', 'aria-activedescendant'].forEach(function (a) {
        input.removeAttribute(a);
      });
    }
    close(box);
  }

  // The list under the box: what has every word typed, whatever the accents and
  // capitals; or everything, when coming back to a box that holds one already (to
  // pick another)
  function open(box, again) {
    var all = box.choices(), typed = norm(box.input.value);
    if (!all.length) return;
    var whole = again && typed && all.some(function (c) { return norm(c.text) === typed; });
    var want = whole ? [] : typed.split(' ').filter(Boolean);
    box.shown = all.filter(function (c) {
      var hay = norm(c.text);
      return want.every(function (w) { return hay.indexOf(w) >= 0; });
    }).slice(0, SHOWN);
    var list = box.list;
    list.textContent = '';
    box.active = -1;
    box.shown.forEach(function (c, i) {
      var li = document.createElement('li');
      li.id = list.id + '-' + i;
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', 'false');
      li.textContent = c.text;
      if (c.unit) {
        var u = document.createElement('span');
        u.className = 'p-option-unit';
        u.textContent = ' · ' + unitName(c.unit);
        li.appendChild(u);
      }
      li.addEventListener('mousedown', function (e) { e.preventDefault(); });   // the box keeps the focus
      li.addEventListener('click', function () { choose(box, c); });
      list.appendChild(li);
    });
    list.hidden = !box.shown.length;
    box.input.setAttribute('aria-expanded', String(!list.hidden));
    box.input.removeAttribute('aria-activedescendant');
  }

  function close(box) {
    box.list.hidden = true;
    box.active = -1;
    if (box.input.hasAttribute('role')) box.input.setAttribute('aria-expanded', 'false');
    box.input.removeAttribute('aria-activedescendant');
  }

  function move(box, by) {
    if (box.list.hidden) open(box, false);
    if (!box.shown.length) return;
    var opts = box.list.children;
    if (box.active >= 0) opts[box.active].setAttribute('aria-selected', 'false');
    box.active = box.active < 0 ? (by > 0 ? 0 : box.shown.length - 1)
      : (box.active + by + box.shown.length) % box.shown.length;
    var opt = opts[box.active];
    opt.setAttribute('aria-selected', 'true');
    box.input.setAttribute('aria-activedescendant', opt.id);
    if (opt.scrollIntoView) opt.scrollIntoView({ block: 'nearest' });
  }

  function choose(box, c) {
    box.input.value = c.text;
    close(box);
    box.picked(c);
  }

  function nameChoices() { return people.map(function (n) { return { text: n }; }); }

  // The items asked for before: at the station picked, most-asked first; with none
  // picked yet, at every station, each item once
  function itemChoices() {
    var st = station(), seen = Object.create(null), all = [];
    asked.forEach(function (x) {
      if (st && x.station !== st) return;
      var k = key(x.item);
      if (seen[k]) { seen[k].count += x.count; return; }
      all.push(seen[k] = { text: x.item, unit: x.unit, count: x.count });
    });
    if (!st) all.sort(function (a, b) { return b.count - a.count; });
    return all;
  }

  /* Requested by ----------------------------------------------------------- */
  function remember() {
    try { localStorage.setItem(NAME_KEY, clean(els.who.value)); } catch (e) { /* private mode */ }
  }
  function recall() {
    try { els.who.value = localStorage.getItem(NAME_KEY) || ''; } catch (e) { /* private mode */ }
  }

  /* An item's row ---------------------------------------------------------- */
  function addRow(focus) {
    if (rows.length >= MAX_ROWS) return;
    var el = tpl.content.firstElementChild.cloneNode(true);
    var n = ++counter;
    // row.input, .qty, .unit, .unitOther and .note are its boxes; unitChosen: the unit
    // was picked or typed here, not filled in by a suggestion
    var row = { el: el, other: el.querySelector('[data-unit-other]'), unitChosen: false };
    var boxes = { item: 'input', qty: 'qty', unit: 'unit', unit_other: 'unitOther', note: 'note' };
    Object.keys(boxes).forEach(function (name) {
      var input = el.querySelector('[data-name="' + name + '"]'), lab = el.querySelector('[data-for="' + name + '"]');
      input.id = 'p-i' + n + '-' + name;
      lab.htmlFor = input.id;
      lab.id = input.id + '-l';
      row[boxes[name]] = input;
    });
    var list = el.querySelector('[role="listbox"]');
    list.id = 'p-i' + n + '-list';
    list.setAttribute('aria-labelledby', row.input.id + '-l');
    words(el);
    row.box = suggest(row.input, list, itemChoices, function (c) { picked(row, c); });
    row.unit.addEventListener('change', function () {
      row.unitChosen = true;
      otherShown(row);
      if (row.unit.value === OTHER) row.unitOther.focus();
    });
    row.unitOther.addEventListener('input', function () { row.unitChosen = true; });
    el.querySelector('[data-remove]').addEventListener('click', function () { removeRow(row); });
    rows.push(row);
    els.list.appendChild(el);
    renumber();
    update();
    if (focus) row.input.focus();
  }

  function removeRow(row) {
    var at = rows.indexOf(row);
    rows.splice(at, 1);
    row.el.parentNode.removeChild(row.el);
    renumber();
    update();
    var before = rows[Math.max(0, at - 1)];
    (before ? before.input : els.add).focus();
  }

  // Each row's number, and Remove only while there's more than one
  function renumber() {
    rows.forEach(function (row, i) {
      row.el.querySelectorAll('[data-out="n"]').forEach(function (s) { s.textContent = String(i + 1); });
      var rm = row.el.querySelector('[data-remove]');
      rm.hidden = rows.length < 2;
      rm.setAttribute('data-aria-en', 'Remove item ' + (i + 1));
      rm.setAttribute('data-aria-vi', 'Xóa hàng ' + (i + 1));
      rm.setAttribute('aria-label', L('Remove item ' + (i + 1), 'Xóa hàng ' + (i + 1)));
    });
    els.add.hidden = rows.length >= MAX_ROWS;
    show('items-full', rows.length >= MAX_ROWS);
  }

  // An item picked from the list: its usual unit, unless one was chosen already;
  // then the quantity
  function picked(row, c) {
    if (!row.unitChosen) setUnit(row, c.unit);
    update();
    row.qty.focus();
  }

  // A unit from the list, or one typed before, under Other…
  function setUnit(row, u) {
    if (!u) return;
    row.unit.value = listed(u) ? u : OTHER;
    row.unitOther.value = listed(u) ? '' : u;
    otherShown(row);
  }
  function otherShown(row) { row.other.hidden = row.unit.value !== OTHER; }
  function unitOf(row) { return row.unit.value === OTHER ? clean(row.unitOther.value) : row.unit.value; }

  // A row left empty is left out
  function blank(row) {
    return !clean(row.input.value) && !row.qty.value.trim() && !row.unit.value && !row.note.value.trim();
  }

  // After any change: the marks again once a send has been tried, and the preview
  // hidden once the request is no longer what it shows
  function update() {
    if (tried && !problem() && line === 'invalid') sendLine(null);
    if (!els.previewBox.hidden && JSON.stringify(body()) !== previewed) {
      els.previewBox.hidden = true;
      sendLine(null);
    }
  }

  /* Checking and sending --------------------------------------------------- */
  // Marks what isn't right and returns the first box to fix, or null
  function problem() {
    var first = null;
    function need(el, ok) { mark(el, !ok); if (!ok && !first) first = el; }
    var name = clean(els.who.value);
    need(els.who, !!name && name.length <= MAX_NAME);
    var st = station();
    els.seg.classList.toggle('is-invalid', !st);
    if (!st && !first) first = form.querySelector('input[name="station"]');
    need(els.day, !!els.day.value && els.day.value >= hanoiToday());
    need(els.time, !els.time.value || /^\d\d:\d\d$/.test(els.time.value));
    var any = false;
    rows.forEach(function (row) {
      if (blank(row)) {
        [row.input, row.qty, row.unit, row.unitOther].forEach(function (el) { mark(el, false); });
        return;
      }
      any = true;
      var item = clean(row.input.value), q = parse(row.qty.value), u = unitOf(row);
      need(row.input, !!item && item.length <= MAX_ITEM);
      need(row.qty, q > 0 && q <= MAX_QTY);
      mark(row.unit.value === OTHER ? row.unit : row.unitOther, false);
      need(row.unit.value === OTHER ? row.unitOther : row.unit, !!u && u.length <= MAX_UNIT);
    });
    if (!any && rows.length) need(rows[0].input, false);
    return first;
  }

  // The request as the Worker takes it; the rows it sends, in order, for its answer
  function body() {
    var b = {
      requested_by: clean(els.who.value), station: station(),
      needed_by: els.day.value, needed_time: els.time.value.slice(0, 5), note: els.note.value.trim(), items: []
    };
    sentRows = [];
    rows.forEach(function (row) {
      if (blank(row)) return;
      sentRows.push(row);
      b.items.push({ item: clean(row.input.value), qty: parse(row.qty.value), unit: unitOf(row),
                     note: clean(row.note.value) });
    });
    return b;
  }

  // The box the Worker says is wrong (field: requested_by, items.2.qty…)
  function markField(field) {
    var m = /^items\.(\d+)\.(\w+)$/.exec(field), row = m && sentRows[+m[1]], el = null;
    if (row) {
      el = m[2] === 'qty' ? row.qty : m[2] === 'note' ? row.note : m[2] !== 'unit' ? row.input
        : row.unit.value === OTHER ? row.unitOther : row.unit;
    }
    else if (field === 'requested_by') el = els.who;
    else if (field === 'needed_by') el = els.day;
    else if (field === 'needed_time') el = els.time;
    else if (field === 'note') el = els.note;
    else if (field === 'station') { els.seg.classList.add('is-invalid'); el = form.querySelector('input[name="station"]'); }
    else if (rows.length) el = rows[0].input;
    if (el && el.parentNode.classList.contains('dough-box')) mark(el, true);
    if (el) el.focus();
  }

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    var b = new Uint8Array(16);
    crypto.getRandomValues(b);
    b[6] = (b[6] & 15) | 64;
    b[8] = (b[8] & 63) | 128;
    var h = Array.prototype.map.call(b, function (x) { return (x + 256).toString(16).slice(1); }).join('');
    return h.slice(0, 8) + '-' + h.slice(8, 12) + '-' + h.slice(12, 16) + '-' + h.slice(16, 20) + '-' + h.slice(20);
  }

  // POST to the Worker: { status, data }; status 0 when it couldn't be reached
  function request(b) {
    return fetch('/api/backoffice/purchase', {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(b)
    }).then(function (res) {
      return res.json().then(function (data) { return { status: res.status, data: data }; },
                             function () { return { status: res.status, data: null }; });
    }, function () { return { status: 0, data: null }; });
  }

  function failed(r) {
    var d = r.data || {};
    if (r.status === 401) sendLine('signed-out');
    else if (r.status === 503) sendLine('off');
    else if (r.status === 400 && d.field) { sendLine('invalid'); markField(d.field); }
    else if (r.status === 502 && d.error === 'slack') { out('slack_error', d.detail || 'Slack'); sendLine('slack-failed'); }
    else if (r.status === 409) sendLine('busy');
    else sendLine('failed');
  }

  // A tap on Preview or Send: checked first, one at a time
  function go(preview) {
    if (busy) return;
    tried = true;
    var bad = problem();
    if (bad) {
      sendLine('invalid');
      bad.focus();
      return;
    }
    busy = true;
    els.preview.disabled = els.send.disabled = true;
    if (!preview && !requestId) requestId = uuid();
    var b = body(), shown = JSON.stringify(b);
    if (preview) b.preview = true;
    if (requestId) b.request_id = requestId;    // a preview after a failed send shows its ref
    sendLine(preview ? 'previewing' : 'sending');
    request(b).then(function (r) {
      if (preview && r.status === 200 && r.data && r.data.preview) {
        messages.preview = { text: r.data.message, station: b.station };
        showMessages();
        previewed = shown;
        sendLine(null);
        els.previewBox.hidden = false;
        els.previewBox.focus();
      } else if (!preview && r.status === 200 && r.data && r.data.ok) {
        sent(r.data, b.station);
      } else {
        failed(r);
      }
    }).then(function () {
      busy = false;
      els.preview.disabled = els.send.disabled = false;
    });
  }

  function sent(d, at) {
    out('ref', d.ref);
    messages.sent = { text: d.message, station: at };
    showMessages();
    show('sent', !d.dry_run);
    show('dry', !!d.dry_run);
    requestId = null;
    remember();
    sendLine(null);
    form.hidden = true;
    done.hidden = false;
    done.focus();
    load(false);                        // the next request suggests this one's items too
  }

  // New request: an empty form, Requested by kept
  function reset() {
    form.querySelectorAll('input[name="station"]').forEach(function (r) { r.checked = false; });
    els.day.value = '';
    els.time.value = '';
    els.note.value = '';
    rows.slice().forEach(function (row) { row.el.parentNode.removeChild(row.el); });
    rows = [];
    tried = false;
    requestId = null;
    form.querySelectorAll('[aria-invalid="true"]').forEach(function (el) { mark(el, false); });
    els.seg.classList.remove('is-invalid');
    els.previewBox.hidden = true;
    addRow(false);
  }

  /* Changes ---------------------------------------------------------------- */
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  form.addEventListener('input', update);
  form.addEventListener('change', function (e) {
    if (e.target === els.who) remember();
    if (e.target.name === 'station') rows.forEach(function (row) { arm(row.box); });   // that station's items
    update();
  });
  els.add.addEventListener('click', function () { addRow(true); });
  els.preview.addEventListener('click', function () { go(true); });
  els.send.addEventListener('click', function () { go(false); });
  done.querySelector('[data-new]').addEventListener('click', function () {
    reset();
    done.hidden = true;
    form.hidden = false;
    form.querySelector('input[name="station"]').focus();
  });

  // EN / VI: the units, the note's placeholder and the messages' approver follow the
  // page's language (the message itself doesn't: it's the same in both)
  if (window.MutationObserver) {
    new MutationObserver(function () {
      words(form);
      renumber();
      showMessages();
    }).observe(root, { attributes: true, attributeFilter: ['lang'] });
  }

  /* Loading ---------------------------------------------------------------- */
  // The suggestions. At the start, signed out or no database: just the line that says
  // so, no form. Not loading: the form as it is, without them.
  function load(first) {
    fetch('/api/backoffice/form', { credentials: 'same-origin', headers: { Accept: 'application/json' } }).then(function (res) {
      if (first && (res.status === 401 || res.status === 503)) {
        form.hidden = true;
        only('data-state', res.status === 401 ? 'signed-out' : 'off');
        return null;
      }
      return res.ok ? res.json() : null;
    }).then(function (d) {
      if (!d) return;
      people = Array.isArray(d.people) ? d.people : [];
      asked = Array.isArray(d.items) ? d.items : [];
      show('dry-run', !!d.dry_run);
      [whoBox].concat(rows.map(function (row) { return row.box; })).forEach(function (box) {
        arm(box);
        if (document.activeElement === box.input) open(box, true);
      });
    }).catch(function () { /* no suggestions this time */ });
  }

  words(form);
  recall();
  whoBox = suggest(els.who, els.whoList, nameChoices, function () { remember(); update(); });
  els.day.min = hanoiToday();
  form.hidden = false;
  addRow(false);
  load(true);
})();
