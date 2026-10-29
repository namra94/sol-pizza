/* Sol — the purchase request (/backoffice/purchase/). No dependencies; load with `defer`.
   build/gen.py (build_purchase) writes the page, every line in both languages, and
   #p-item, the template for an item's row. This loads the Order Guide (GET
   /api/backoffice/guide, worker/backoffice.js) and fills the lists from it: the staff
   for Requested by (the last name picked is remembered on the phone), the suppliers by
   status (Active, then Quoting, then Not used yet; Stopped ones left out), and each
   supplier's items, found as you type in English or Vietnamese, with or without the
   accents. Anything not on a list can be typed: an item that isn't in the Order Guide
   goes without a price, and a supplier that isn't needs Arman's ✅. Without a guide
   everything is typed.
   As it's filled the summary keeps up: the estimate before VAT, who approves, and
   whether Arman's ✅ is needed, by the Order Sheet's rules. That's a guide for the
   sender: the Worker works it all out again from the Order Guide when it posts.
   Preview asks the Worker for the exact message (POST /api/backoffice/purchase with
   preview: true); Send posts it with an id made here, kept until the request has gone
   through, so a second tap or a retry never posts it twice. Nothing typed is lost on
   an error. */
(function () {
  'use strict';
  var form = document.getElementById('purchase');
  var tpl = document.getElementById('p-item');
  var done = document.getElementById('p-done');
  if (!form || !tpl || !done) return;
  var root = document.documentElement;
  var OTHER = '\n';                     // the lists' "Other…" (no name has a line break)
  var MAX_ROWS = 30, MAX_QTY = 100000, MAX_NAME = 60;
  var LIMIT = 5000000;                  // as the Worker's, if the Order Sheet has none
  var NAME_KEY = 'sol-office-name';     // who asked last on this phone (localStorage)
  var STATUSES = [['Active', 'Active', 'Đang dùng'], ['Quoting', 'Quoting', 'Đang báo giá'],
                  ['Not used yet', 'Not used yet', 'Chưa dùng']];
  // the accents, taken off to search: the combining marks U+0300 to U+036F
  var MARKS = new RegExp('[' + String.fromCharCode(0x300) + '-' + String.fromCharCode(0x36f) + ']', 'g');

  var els = {
    who: form.elements.who, whoOther: form.elements.who_other,
    supplier: form.elements.supplier, supplierOther: form.elements.supplier_other,
    facts: document.getElementById('p-facts'), seg: form.querySelector('.dough-seg'),
    day: form.elements.day, time: form.elements.time, note: form.elements.note,
    list: document.getElementById('p-items'), add: form.querySelector('[data-add]'),
    previewBox: document.getElementById('p-preview-box'), message: document.getElementById('p-preview'),
    preview: form.querySelector('[data-preview]'), send: form.querySelector('[data-send]')
  };
  var guide = null, bySupplier = {}, itemsOf = {}, asOf = null;
  var rows = [], counter = 0;
  var requestId = null;                 // made at the first Send, kept until it has gone through
  var previewed = null;                 // the request the preview shows (body(), as JSON)
  var busy = false, tried = false, sentRows = [];

  /* Words and numbers in the page's language --------------------------------- */
  function vi() { return root.lang === 'vi'; }
  function L(en, viText) { return vi() ? viText : en; }
  var formats = {};
  function fmt(x, digits) {                 // 1,250,000 / 1.250.000; 1.5 / 1,5
    var lang = vi() ? 'vi-VN' : 'en-GB', key = lang + digits;
    if (!formats[key]) formats[key] = new Intl.NumberFormat(lang, { maximumFractionDigits: digits });
    return formats[key].format(x + 0);
  }
  function vnd(x) { return fmt(Math.round(x), 0) + 'đ'; }
  function hhmm(iso) {                      // 20:30, Hanoi time
    return new Intl.DateTimeFormat(vi() ? 'vi-VN' : 'en-GB', {
      hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Ho_Chi_Minh'
    }).format(new Date(iso));
  }
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

  /* The page's lines ------------------------------------------------------- */
  function show(cond, on) {
    document.querySelectorAll('[data-if="' + cond + '"]').forEach(function (el) { el.hidden = !on; });
  }
  function out(key, text) {
    document.querySelectorAll('[data-out="' + key + '"]').forEach(function (el) { el.textContent = text; });
  }
  // One line of a group at a time (data-guide, data-send-line); null hides them all
  function only(attr, key) {
    document.querySelectorAll('[' + attr + ']').forEach(function (el) { el.hidden = el.getAttribute(attr) !== key; });
  }
  var line = null;                      // the line under Preview and Send that's showing
  function sendLine(key) {
    line = key;
    only('data-send-line', key);
  }
  function option(value, text) {
    var o = document.createElement('option');
    o.value = value;
    o.textContent = text;
    return o;
  }
  function mark(el, on) {
    el.setAttribute('aria-invalid', String(on));
    el.parentNode.classList.toggle('is-invalid', on);
  }

  /* The Order Guide -------------------------------------------------------- */
  function hasStaff() { return !!(guide && guide.staff.length); }
  function hasSuppliers() { return !!(guide && guide.suppliers.some(function (s) { return s.status !== 'Stopped'; })); }
  function index() {
    bySupplier = Object.create(null);   // by name, whatever the names are
    itemsOf = Object.create(null);
    guide.suppliers.forEach(function (s) { bySupplier[s.name] = s; itemsOf[s.name] = []; });
    guide.items.forEach(function (it) { if (itemsOf[it.supplier]) itemsOf[it.supplier].push(it); });
  }

  // The supplier as the Worker will see it: picked, or typed (a typed name that's in
  // the Order Sheet is that supplier)
  function supplier() {
    var v = els.supplier.value;
    var name = hasSuppliers() && v !== OTHER ? v : clean(els.supplierOther.value);
    return { name: name, s: guide && name && Object.prototype.hasOwnProperty.call(bySupplier, name) ? bySupplier[name] : null };
  }
  function offered() {
    var s = supplier().s;
    return s ? itemsOf[s.name] : [];
  }
  function who() {
    return hasStaff() && els.who.value !== OTHER ? els.who.value : clean(els.whoOther.value);
  }

  /* Requested by and the supplier ------------------------------------------ */
  function fillWho() {
    var sel = els.who, keep = sel.value;
    sel.textContent = '';
    sel.appendChild(option('', L('Choose your name', 'Chọn tên của bạn')));
    (guide ? guide.staff : []).forEach(function (n) { sel.appendChild(option(n, n)); });
    sel.appendChild(option(OTHER, L('Other…', 'Người khác…')));
    sel.value = keep;
    if (sel.value !== keep) sel.value = '';
  }

  function whoShown() {
    var typed = !hasStaff() || els.who.value === OTHER;
    show('who-list', hasStaff());
    show('who-nolist', !hasStaff());
    show('who-typed', typed);
  }

  function remember() {
    try { localStorage.setItem(NAME_KEY, who()); } catch (e) { /* private mode */ }
  }
  function recall() {
    var saved = '';
    try { saved = localStorage.getItem(NAME_KEY) || ''; } catch (e) { /* private mode */ }
    if (!saved) return;
    if (hasStaff() && guide.staff.indexOf(saved) >= 0) {
      els.who.value = saved;
    } else {
      if (hasStaff()) els.who.value = OTHER;
      els.whoOther.value = saved;
    }
  }

  function statusName(status) {
    for (var i = 0; i < STATUSES.length; i++) if (STATUSES[i][0] === status) return L(STATUSES[i][1], STATUSES[i][2]);
    return status || L('No status', 'Chưa có trạng thái');
  }

  function fillSuppliers() {
    var sel = els.supplier, keep = sel.value;
    var shown = guide ? guide.suppliers.filter(function (s) { return s.status !== 'Stopped'; }) : [];
    var order = STATUSES.map(function (s) { return s[0]; });
    shown.forEach(function (s) { if (order.indexOf(s.status) < 0) order.push(s.status); });   // any other status, after
    sel.textContent = '';
    sel.appendChild(option('', L('Choose a supplier', 'Chọn nhà cung cấp')));
    order.forEach(function (status) {
      var group = shown.filter(function (s) { return s.status === status; });
      if (!group.length) return;
      var g = document.createElement('optgroup');
      g.label = statusName(status);
      group.forEach(function (s) { g.appendChild(option(s.name, s.name + (s.supplies ? ' — ' + s.supplies : ''))); });
      sel.appendChild(g);
    });
    sel.appendChild(option(OTHER, L('Other supplier…', 'Nhà cung cấp khác…')));
    sel.value = keep;
    if (sel.value !== keep) sel.value = '';
  }

  function supplierShown() {
    show('sup-list', hasSuppliers());
    show('sup-nolist', !hasSuppliers());
    show('sup-typed', !hasSuppliers() || els.supplier.value === OTHER);
  }

  // What the Order Sheet says about it: who orders, the days, the cut-off…
  function fillFacts() {
    var s = supplier().s, f = els.facts;
    f.textContent = '';
    if (s) {
      [['owner', 'Ordered by', 'Người đặt hàng'], ['order_days', 'Order days', 'Ngày đặt hàng'],
       ['cutoff', 'Cut-off', 'Hạn chót'], ['delivery', 'Delivery', 'Giao hàng'],
       ['min_order', 'Minimum order', 'Đơn tối thiểu']].forEach(function (x) {
        if (!s[x[0]]) return;
        var li = document.createElement('li'), name = document.createElement('span');
        name.className = 'label';
        name.textContent = L(x[1], x[2]);
        li.appendChild(name);
        li.appendChild(document.createTextNode(s[x[0]]));
        f.appendChild(li);
      });
    }
    f.hidden = !f.firstChild;
  }

  // A new supplier: its station, its facts, and every row's item looked up again
  function supplierChanged() {
    supplierShown();
    fillFacts();
    var s = supplier().s;
    if (s && s.station) {
      form.querySelectorAll('input[name="station"]').forEach(function (r) { r.checked = r.value === s.station; });
    }
    rows.forEach(function (row) { combo(row); resolve(row); });
    update();
  }

  /* An item's row ---------------------------------------------------------- */
  function addRow(focus) {
    if (rows.length >= MAX_ROWS) return;
    var el = tpl.content.firstElementChild.cloneNode(true);
    var n = ++counter;
    // row.input, .qty, .unit and .note are its boxes; row.item the Order Guide's item it names
    var row = { el: el, item: null, active: -1, shown: [], list: el.querySelector('[role="listbox"]'),
                price: el.querySelector('.p-price') };
    var boxes = { item: 'input', qty: 'qty', unit: 'unit', note: 'note' };
    Object.keys(boxes).forEach(function (key) {
      var input = el.querySelector('[data-name="' + key + '"]'), lab = el.querySelector('[data-for="' + key + '"]');
      input.id = 'p-i' + n + '-' + key;
      lab.htmlFor = input.id;
      lab.id = input.id + '-l';
      row[boxes[key]] = input;
    });
    row.list.id = 'p-i' + n + '-list';
    row.list.setAttribute('aria-labelledby', row.input.id + '-l');
    wire(row);
    rows.push(row);
    els.list.appendChild(el);
    combo(row);
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

  // The item's box is a list to search while the supplier has items, else plain text
  function combo(row) {
    var on = offered().length > 0, input = row.input;
    if (on) {
      input.setAttribute('role', 'combobox');
      input.setAttribute('aria-autocomplete', 'list');
      input.setAttribute('aria-expanded', 'false');
      input.setAttribute('aria-controls', row.list.id);
    } else {
      ['role', 'aria-autocomplete', 'aria-expanded', 'aria-controls', 'aria-activedescendant'].forEach(function (a) {
        input.removeAttribute(a);
      });
    }
    closeList(row);
  }

  // The supplier's item the box names, by its name or its Vietnamese name, whatever
  // the accents and capitals; then its unit, which can't be changed
  function resolve(row) {
    var key = norm(row.input.value), found = null;
    if (key) {
      offered().some(function (it) {
        if (norm(it.name) === key || (it.vn && norm(it.vn) === key)) found = it;
        return !!found;
      });
    }
    setItem(row, found);
  }

  function setItem(row, it) {
    row.item = it;
    var fixed = !!(it && it.unit);
    if (fixed) row.unit.value = it.unit;
    row.unit.readOnly = fixed;
    row.unit.parentNode.classList.toggle('is-readonly', fixed);
  }

  function optionText(it) {
    var parts = [it.name];
    if (it.vn && it.vn !== it.name) parts.push(it.vn);
    if (it.pack) parts.push(it.pack);
    return parts.join(' · ');
  }

  // The list under the box: the supplier's items that have every word typed, or all of
  // them when coming back to a box that names one already (to pick another)
  function openList(row, all) {
    var items = offered();
    if (!items.length) return;
    var words = all ? [] : norm(row.input.value).split(' ').filter(Boolean);
    row.shown = items.filter(function (it) {
      var hay = norm([it.name, it.vn, it.pack, it.code, it.category].join(' '));
      return words.every(function (w) { return hay.indexOf(w) >= 0; });
    }).slice(0, 60);
    row.list.textContent = '';
    row.active = -1;
    row.shown.forEach(function (it, i) {
      var li = document.createElement('li');
      li.id = row.list.id + '-' + i;
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', 'false');
      li.textContent = optionText(it);
      li.addEventListener('mousedown', function (e) { e.preventDefault(); });   // the box keeps the focus
      li.addEventListener('click', function () { pick(row, it); });
      row.list.appendChild(li);
    });
    row.list.hidden = !row.shown.length;
    row.input.setAttribute('aria-expanded', String(!row.list.hidden));
    row.input.removeAttribute('aria-activedescendant');
  }

  function closeList(row) {
    row.list.hidden = true;
    row.active = -1;
    if (row.input.hasAttribute('role')) row.input.setAttribute('aria-expanded', 'false');
    row.input.removeAttribute('aria-activedescendant');
    priceLine(row);
  }

  function move(row, by) {
    if (row.list.hidden) openList(row, false);
    if (!row.shown.length) return;
    var opts = row.list.children;
    if (row.active >= 0) opts[row.active].setAttribute('aria-selected', 'false');
    row.active = row.active < 0 ? (by > 0 ? 0 : row.shown.length - 1)
      : (row.active + by + row.shown.length) % row.shown.length;
    var opt = opts[row.active];
    opt.setAttribute('aria-selected', 'true');
    row.input.setAttribute('aria-activedescendant', opt.id);
    if (opt.scrollIntoView) opt.scrollIntoView({ block: 'nearest' });
  }

  // An item picked from the list: its name in the box, its unit, then the quantity
  function pick(row, it) {
    row.input.value = it.name;
    setItem(row, it);
    closeList(row);
    update();
    row.qty.focus();
  }

  function wire(row) {
    var input = row.input;
    input.addEventListener('input', function () {
      resolve(row);
      openList(row, false);
    });
    input.addEventListener('focus', function () { openList(row, !!row.item); });
    input.addEventListener('blur', function () {
      if (row.item) input.value = row.item.name;
      setTimeout(function () { if (document.activeElement !== input) closeList(row); }, 150);
    });
    input.addEventListener('keydown', function (e) {
      if (!input.hasAttribute('role')) return;
      var key = e.key;
      if (key === 'ArrowDown' || key === 'Down') { e.preventDefault(); move(row, 1); }
      else if (key === 'ArrowUp' || key === 'Up') { e.preventDefault(); move(row, -1); }
      else if (key === 'Enter' && !row.list.hidden && row.active >= 0) { e.preventDefault(); pick(row, row.shown[row.active]); }
      else if ((key === 'Escape' || key === 'Esc') && !row.list.hidden) { e.preventDefault(); closeList(row); }
    });
    row.el.querySelector('[data-remove]').addEventListener('click', function () { removeRow(row); });
  }

  // Under each item: its price and the line's estimate, or that it has none
  function priceLine(row) {
    var it = row.item, q = parse(row.qty.value), text = '';
    if (it && it.price !== null) {
      var unit = vi() && it.unit_vn ? it.unit_vn : it.unit;
      text = vnd(it.price) + (unit ? ' / ' + unit : '') + (q > 0 ? ' · ~' + vnd(q * it.price) : '') +
        (it.notes ? ' · ' + it.notes : '');
    } else if (it) {
      text = L('No price in the Order Guide', 'Chưa có giá trong danh mục');
    } else if (guide && clean(row.input.value) && row.list.hidden) {     // not while the list offers some
      text = L('Not in the Order Guide — no price', 'Chưa có trong danh mục — chưa có giá');
    }
    row.price.textContent = text;
    row.price.hidden = !text;
    row.price.classList.toggle('is-unpriced', !!text && !(it && it.price !== null));
  }

  /* The summary ------------------------------------------------------------ */
  function summary() {
    var sup = supplier(), set = guide ? guide.settings : {}, total = 0, priced = 0, unpriced = 0;
    rows.forEach(function (row) {
      if (!clean(row.input.value)) return;
      var q = parse(row.qty.value);
      if (row.item && row.item.price !== null) {
        priced++;
        if (q > 0) total += q * row.item.price;
      } else {
        unpriced++;
      }
    });
    total = Math.round(total);
    out('estimate', priced ? '~' + vnd(total) : '—');
    var sub = !priced && !unpriced ? L('Add the items to see it.', 'Thêm mặt hàng để xem ước tính.')
      : !priced ? L('No item here has a price in the Order Guide.', 'Chưa mặt hàng nào có giá trong danh mục.')
      : unpriced ? L(unpriced + (unpriced === 1 ? ' item has no price and isn’t in it.' : ' items have no price and aren’t in it.'),
                     unpriced + ' mặt hàng chưa có giá, không được tính.') : '';
    out('unpriced', sub);
    show('unpriced', !!sub);

    var station = (form.querySelector('input[name="station"]:checked') || {}).value;
    var approver = station === 'Kitchen' ? set.kitchen_approver || L('the Kitchen approver', 'người duyệt của Bếp')
      : station ? set.barfoh_approver || L('the Bar & FOH approver', 'người duyệt của Bar và Sảnh') : '';
    out('approver', approver ? L('Approves in Slack: ', 'Người duyệt trên Slack: ') + approver
      : L('Choose the station to see who approves.', 'Chọn bộ phận để biết ai duyệt.'));

    // Arman too, above the limit or for a supplier that isn't Active (the Order Sheet's rule)
    var limit = set.limit === undefined ? LIMIT : set.limit, why = [];
    if (total > limit) why.push(L('over ' + vnd(limit) + ' before VAT', 'trên ' + vnd(limit) + ' chưa VAT'));
    if (sup.name && !sup.s) why.push(L('supplier not in the Order Sheet', 'nhà cung cấp chưa có trong Order Sheet'));
    else if (sup.s && sup.s.status !== 'Active') why.push(L('supplier not Active yet', 'nhà cung cấp chưa Active'));
    var owner = set.owner || 'Arman';
    out('owner', why.length ? L(owner + '’s ✅ needed: ', 'Cần anh ' + owner + ' duyệt: ') + why.join(', ') : '');
    show('owner', why.length > 0);
  }

  // After any change: the prices and the summary again, the marks once a send has been
  // tried, and the preview hidden once the request is no longer what it shows
  function update() {
    rows.forEach(priceLine);
    summary();
    if (tried && !problem() && line === 'invalid') sendLine(null);
    if (!els.previewBox.hidden && JSON.stringify(body()) !== previewed) {
      els.previewBox.hidden = true;
      sendLine(null);
    }
  }

  /* Checking and sending --------------------------------------------------- */
  // Marks what isn't right and returns the first box to fix, or null. A row left
  // empty is left out.
  function problem() {
    var first = null;
    function need(el, ok) { mark(el, !ok); if (!ok && !first) first = el; }
    var name = who(), sup = supplier();
    need(hasStaff() && els.who.value !== OTHER ? els.who : els.whoOther, !!name && name.length <= MAX_NAME);
    need(hasSuppliers() && els.supplier.value !== OTHER ? els.supplier : els.supplierOther,
         !!sup.name && (!!sup.s || sup.name.length <= MAX_NAME));
    var station = form.querySelector('input[name="station"]:checked');
    els.seg.classList.toggle('is-invalid', !station);
    if (!station && !first) first = form.querySelector('input[name="station"]');
    need(els.day, !!els.day.value && els.day.value >= hanoiToday());
    need(els.time, !els.time.value || /^\d\d:\d\d$/.test(els.time.value));
    var any = false;
    rows.forEach(function (row) {
      var name = clean(row.input.value), q = parse(row.qty.value);
      if (!name && !row.qty.value.trim() && !row.note.value.trim()) { mark(row.input, false); mark(row.qty, false); return; }
      any = true;
      need(row.input, !!name && (!!row.item || name.length <= MAX_NAME));
      need(row.qty, q > 0 && q <= MAX_QTY);
    });
    if (!any && rows.length) need(rows[0].input, false);
    return first;
  }

  // The request as the Worker takes it; the rows it sends, in order, for its answer
  function body() {
    var sup = supplier(), b = {
      requested_by: who(), supplier: sup.s ? sup.s.name : sup.name,
      station: (form.querySelector('input[name="station"]:checked') || {}).value,
      needed_by: els.day.value, needed_time: els.time.value.slice(0, 5), note: els.note.value.trim(), items: []
    };
    sentRows = [];
    rows.forEach(function (row) {
      var name = clean(row.input.value);
      if (!name) return;
      sentRows.push(row);
      b.items.push({ item: row.item ? row.item.name : name, qty: parse(row.qty.value), unit: clean(row.unit.value),
                     note: clean(row.note.value) });
    });
    return b;
  }

  // The box the Worker says is wrong (field: requested_by, items.2.qty…)
  function markField(field) {
    var m = /^items\.(\d+)\.(\w+)$/.exec(field), el = null;
    if (m && sentRows[+m[1]]) el = sentRows[+m[1]][m[2] === 'qty' ? 'qty' : m[2] === 'item' ? 'input' : m[2]];
    else if (field === 'requested_by') el = hasStaff() && els.who.value !== OTHER ? els.who : els.whoOther;
    else if (field === 'supplier') el = hasSuppliers() && els.supplier.value !== OTHER ? els.supplier : els.supplierOther;
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
        els.message.textContent = r.data.message;
        previewed = shown;
        sendLine(null);
        els.previewBox.hidden = false;
        els.previewBox.focus();
      } else if (!preview && r.status === 200 && r.data && r.data.ok) {
        sent(r.data);
      } else {
        failed(r);
      }
    }).then(function () {
      busy = false;
      els.preview.disabled = els.send.disabled = false;
    });
  }

  function sent(d) {
    out('ref', d.ref);
    out('sent_message', d.message);
    show('sent', !d.dry_run);
    show('dry', !!d.dry_run);
    requestId = null;
    sendLine(null);
    form.hidden = true;
    done.hidden = false;
    done.focus();
  }

  // New request: an empty form, Requested by kept
  function reset() {
    els.supplier.value = '';
    els.supplierOther.value = '';
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
    addRow(false);
    supplierChanged();
  }

  /* Changes ---------------------------------------------------------------- */
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  form.addEventListener('input', function (e) {
    if (e.target === els.supplierOther) supplierChanged();
    else update();
  });
  form.addEventListener('change', function (e) {
    var el = e.target;
    if (el === els.who) {
      whoShown();
      if (el.value === OTHER) els.whoOther.focus();
      remember();
    } else if (el === els.whoOther) {
      remember();
    } else if (el === els.supplier) {
      supplierChanged();
      if (el.value === OTHER) els.supplierOther.focus();
    } else {
      update();
    }
  });
  els.add.addEventListener('click', function () { addRow(true); });
  els.preview.addEventListener('click', function () { go(true); });
  els.send.addEventListener('click', function () { go(false); });
  done.querySelector('[data-new]').addEventListener('click', function () {
    reset();
    done.hidden = true;
    form.hidden = false;
    (hasSuppliers() ? els.supplier : els.supplierOther).focus();
  });

  // EN / VI: the lists, the prices and the summary follow the page's language (the
  // message doesn't: it's the same in both)
  function relabel() {
    if (asOf) out('as_of', hhmm(asOf));
    if (form.hidden && done.hidden) return;
    fillWho();
    fillSuppliers();
    fillFacts();
    renumber();
    rows.forEach(priceLine);
    summary();
  }
  if (window.MutationObserver) {
    new MutationObserver(relabel).observe(root, { attributes: true, attributeFilter: ['lang'] });
  }

  /* Loading ---------------------------------------------------------------- */
  function start() {
    fillWho();
    recall();
    whoShown();
    fillSuppliers();
    els.day.min = hanoiToday();
    form.hidden = false;
    addRow(false);
    supplierChanged();
  }

  // Signed out or no database: just the line that says so. The guide not loading:
  // the form, with everything typed by hand.
  only('data-guide', 'loading');
  fetch('/api/backoffice/guide', { credentials: 'same-origin', headers: { Accept: 'application/json' } }).then(function (res) {
    if (res.status === 401 || res.status === 503) return res.status;
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
  }).then(function (d) {
    if (d === 401 || d === 503) {
      only('data-guide', d === 401 ? 'signed-out' : 'off');
      return;
    }
    guide = d && d.guide && Array.isArray(d.guide.suppliers) ? d.guide : null;
    if (guide) index();
    asOf = guide && d.stale && d.as_of ? d.as_of : null;
    if (asOf) out('as_of', hhmm(asOf));
    only('data-guide', !guide ? 'none' : asOf ? 'stale' : null);
    show('dry-run', !!d.dry_run);
    start();
  }, function () {
    only('data-guide', 'failed');
    start();
  });
})();
