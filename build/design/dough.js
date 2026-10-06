/* Sol — the dough calculator (/dough/). No dependencies; load with `defer`.
   build/gen.py (build_dough) writes the page, every line in both languages, and
   the house spec as JSON (#dough-spec); this reads the boxes, fills in the
   weights and logs the batch (POST /api/dough/log, worker/index.js).
   Baker's percentages: every ingredient is a percentage of all the flour, so the
   flour is the dough's weight ÷ (1 + the other percentages ÷ 100). The blend
   splits the flour: whole wheat and rye, and pizza flour the rest. A preferment
   is made with pizza flour: it takes its share of the flour and its water out of
   the final mix, and adds its own yeast. The yeast is fresh yeast.
   Water temperature, the bakers' rule: water = 3 × the dough you want − flour −
   kitchen − mixer friction (with a preferment, 4 × and minus the preferment too).
   Colder than your water: swap some of it for ice, which soaks up 80 °C's worth
   of heat per gram as it melts, so ice = water × (yours − needed) ÷ (yours + 80).
   The address keeps whatever of the batch differs from the house spec
   (?n=60&h=68), so a link sends a batch; "Back to the house spec" clears it. The
   kitchen's temperature and humidity and the log's boxes stay out of it: they're
   about today. */
(function () {
  'use strict';
  var form = document.getElementById('dough');
  var specEl = document.getElementById('dough-spec');
  if (!form || !specEl) return;
  var data = JSON.parse(specEl.textContent);
  var SPEC = data.spec, PREFERMENTS = data.preferments;
  var root = document.documentElement;
  var DASH = '—';

  // The batch's boxes and choice by name, and their keys in the address
  var KEYS = {
    balls: 'n', ball: 'w', waste: 'x',
    hydration: 'h', salt: 's', yeast: 'y', oil: 'o', sugar: 'su', whole_wheat: 'ww', rye: 'ry',
    preferment: 'pf', pf_flour: 'pff', pf_hydration: 'pfh', pf_yeast: 'pfy',
    t_dough: 'td', t_flour: 'tf', t_pf: 'tp', t_friction: 'tm', t_water: 'tw'
  };
  var TEMP_OPEN = 't';                  // the address key for an open Water temperature
  var PF_BOXES = ['pf_flour', 'pf_hydration', 'pf_yeast'];
  var KITCHEN = ['kitchen_c', 'humidity'];   // measured each time; the log needs both
  var OUTS = ['balls', 'ball', 'dough_kg', 'waste', 'pf_flour', 'pf_water', 'pf_yeast', 'pizza', 'ww', 'rye',
              'water', 'pf', 'salt', 'yeast', 'oil', 'sugar', 'dough_g', 'w_tap', 'ice', 'w_final', 'tw',
              't_dough', 't_water'];
  var LOG_STATES = ['log-kitchen', 'log-who', 'log-check', 'log-saving', 'log-saved', 'log-failed',
                    'log-signed-out', 'log-off'];
  var NAME_KEY = 'sol-dough-name';      // who mixed last on this phone (localStorage)

  var boxes = {};                       // every number box: the batch's, the kitchen's, the log's
  form.querySelectorAll('input[data-min]').forEach(function (el) { boxes[el.name] = el; });
  var temp = form.querySelector('.dough-temp');
  var shareBtn = form.querySelector('[data-share]');
  var resetBtn = form.querySelector('[data-reset]');
  var logBtn = form.querySelector('[data-log]');
  var dayBox = form.elements.day, whoBox = form.elements.made_by, notesBox = form.elements.notes;
  var logTried = false;                 // after a try at logging, empty kitchen boxes are marked
  var urlTimer = 0, copiedTimer = 0;

  function has(obj, key) { return Object.prototype.hasOwnProperty.call(obj, key); }
  function round(x, places) { var f = Math.pow(10, places); return Math.round(x * f) / f; }
  function hanoiToday() { return new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10); }

  /* Numbers in the page's language: 6,254.5 in English, 6.254,5 in Vietnamese */
  var formats = {};
  function fmt(x, min, max, grouping) {
    var lang = root.lang === 'vi' ? 'vi-VN' : 'en-GB', key = [lang, min, max, grouping].join();
    if (!formats[key]) {
      formats[key] = new Intl.NumberFormat(lang, {
        minimumFractionDigits: min, maximumFractionDigits: max, useGrouping: grouping
      });
    }
    return formats[key].format(x + 0);  // + 0: never "-0"
  }
  function num(x) { return fmt(x, 0, 3, false); }          // a box's value: 2.8, or 2,8
  function grams(x) {                                       // 6,301 g, 17.6 g, 0.35 g
    var d = x < 1 ? 2 : x < 100 ? 1 : 0;
    return fmt(x, d, d, true);
  }
  function degrees(x) { return fmt(Math.round(x), 0, 0, false); }

  // "2,8", "2.8" and " 2.8 " are all 2.8; anything else is NaN
  function parse(s) {
    s = String(s).replace(/\s+/g, '').replace(',', '.');
    return /^-?(\d+\.?\d*|\.\d+)$/.test(s) ? parseFloat(s) : NaN;
  }

  /* The page's state ------------------------------------------------------- */
  function choice(name) {
    var r = form.querySelector('input[name="' + name + '"]:checked');
    return r ? r.value : SPEC[name];
  }
  function check(name, value) {
    form.querySelectorAll('input[name="' + name + '"]').forEach(function (r) { r.checked = r.value === value; });
  }

  // The house spec with this preferment (with none, the first one's numbers sit in
  // its hidden boxes)
  function defaults(pf) {
    var d = {}, p = PREFERMENTS[pf] || PREFERMENTS[Object.keys(PREFERMENTS)[0]];
    Object.keys(SPEC).forEach(function (k) { d[k] = SPEC[k]; });
    Object.keys(p).forEach(function (k) { d[k] = p[k]; });
    d.preferment = pf;
    return d;
  }

  // The batch's boxes; the kitchen's and the log's are left as they are
  function fill(d) {
    Object.keys(boxes).forEach(function (name) { if (has(d, name)) boxes[name].value = num(d[name]); });
    check('preferment', d.preferment);
  }

  function markBox(el, on) {
    el.setAttribute('aria-invalid', String(on));
    el.parentNode.classList.toggle('is-invalid', on);
  }

  // Every box, checked against its range. A box someone has just emptied to retype
  // isn't marked until they leave it. The kitchen's boxes may stay empty until
  // someone tries to log the batch.
  function read() {
    var v = { preferment: choice('preferment'), temp: temp.open, bad: false, badTemp: false, badLog: false,
              marked: false };
    var pf = v.preferment !== 'none';
    Object.keys(boxes).forEach(function (name) {
      var el = boxes[name], raw = el.value.trim(), x = parse(raw), empty = raw === '';
      var ok = !isNaN(x) && x >= +el.getAttribute('data-min') && x <= +el.getAttribute('data-max') &&
               (!el.hasAttribute('data-int') || x === Math.round(x));
      var optional = el.hasAttribute('data-optional');
      var bad = optional ? (!empty && !ok) || (empty && logTried && KITCHEN.indexOf(name) >= 0) : !ok;
      var mark = bad && !(el === document.activeElement && empty);
      var group = name.indexOf('t_') === 0 ? 'temp' : optional ? 'log' : 'main';
      var used = (PF_BOXES.indexOf(name) < 0 && name !== 't_pf') || pf;
      if (group === 'temp') used = used && v.temp;
      markBox(el, mark);
      v[name] = ok ? x : NaN;
      if (bad && used) {
        if (group === 'main') v.bad = true;
        else if (group === 'temp') v.badTemp = true;
        else v.badLog = true;
        if (mark && group !== 'log') v.marked = true;
      }
    });
    // The blend: pizza flour is what whole wheat and rye leave
    v.pizza = 100 - v.whole_wheat - v.rye;
    if (v.pizza < 0) {
      v.bad = v.blendOver = v.marked = true;
      markBox(boxes.whole_wheat, true);
      markBox(boxes.rye, true);
    }
    // After a try at logging: the day and who mixed it, marked until they're filled in
    if (logTried) {
      markBox(dayBox, !dayBox.value);
      markBox(whoBox, !whoBox.value.trim());
    }
    // The water needs the kitchen's temperature
    if (v.temp) {
      if (!boxes.kitchen_c.value.trim()) v.needKitchen = true;
      else if (isNaN(v.kitchen_c)) v.badTemp = true;
    }
    return v;
  }

  /* The arithmetic --------------------------------------------------------- */
  function compute(v) {
    var pf = v.preferment !== 'none', share = pf ? v.pf_flour / 100 : 0;
    var dough = v.balls * v.ball * (1 + v.waste / 100);
    var flour = dough / (1 + (v.hydration + v.salt + v.yeast + v.oil + v.sugar) / 100 + share * v.pf_yeast / 100);
    var r = {
      dough: dough, flour: flour,
      pizza: flour * v.pizza / 100, ww: flour * v.whole_wheat / 100, rye: flour * v.rye / 100,
      water: flour * v.hydration / 100, salt: flour * v.salt / 100, yeast: flour * v.yeast / 100,
      oil: flour * v.oil / 100, sugar: flour * v.sugar / 100, pfFlour: flour * share
    };
    r.pfWater = pf ? r.pfFlour * v.pf_hydration / 100 : 0;
    r.pfYeast = pf ? r.pfFlour * v.pf_yeast / 100 : 0;
    r.pf = r.pfFlour + r.pfWater + r.pfYeast;
    r.finalPizza = r.pizza - r.pfFlour;   // the preferment is made with pizza flour
    r.finalWater = r.water - r.pfWater;
    if (v.temp && !v.needKitchen && !v.badTemp) {
      r.tw = (pf ? 4 : 3) * v.t_dough - v.t_flour - v.kitchen_c - (pf ? v.t_pf : 0) - v.t_friction;
      r.ice = r.tw < v.t_water ? r.finalWater * (v.t_water - r.tw) / (v.t_water + 80) : 0;
    }
    return r;
  }

  /* The page --------------------------------------------------------------- */
  function out(key, text) {
    form.querySelectorAll('[data-out="' + key + '"]').forEach(function (el) { el.textContent = text; });
  }
  function show(cond, on) {
    form.querySelectorAll('[data-if="' + cond + '"]').forEach(function (el) { el.hidden = !on; });
  }

  // Renders the page and returns what it read and worked out ({v, r}; r is null
  // while a box needs fixing)
  function render() {
    var v = read(), pf = v.preferment !== 'none';
    show('pf', pf);
    Object.keys(PREFERMENTS).forEach(function (k) { show('pf-' + k, v.preferment === k); });
    show('temp', v.temp);
    show('warn-invalid', v.marked);
    show('warn-blend', !!v.blendOver);
    out('pizza_pct', isNaN(v.pizza) || v.pizza < 0 ? DASH : num(v.pizza));
    ['waste', 'ww', 'rye', 'oil', 'sugar', 'warn-pf', 'warn-pf-pizza', 'ice', 'no-ice', 'water', 'need-kitchen',
     'warn-ice', 'warn-hot', 'warn-dry'].forEach(function (cond) { show(cond, false); });
    if (v.bad) {
      OUTS.forEach(function (k) { out(k, DASH); });
      return { v: v, r: null };
    }

    var r = compute(v);
    out('balls', fmt(v.balls, 0, 0, true));
    out('ball', num(v.ball));
    out('dough_kg', fmt(r.dough / 1000, 1, 1, true));
    out('waste', num(v.waste));
    show('waste', v.waste > 0);
    out('pf_flour', grams(r.pfFlour));
    out('pf_water', grams(r.pfWater));
    out('pf_yeast', grams(r.pfYeast));
    // A preferment bigger than the blend's pizza flour, or wetter than the whole
    // dough, leaves the final mix short.
    var shortFlour = r.finalPizza < -0.05, shortWater = r.finalWater < -0.05;
    var water = Math.max(r.finalWater, 0);
    show('warn-pf-pizza', shortFlour);
    show('warn-pf', shortWater);
    out('pizza', shortFlour ? DASH : grams(Math.max(r.finalPizza, 0)));
    out('ww', grams(r.ww));
    out('rye', grams(r.rye));
    show('ww', v.whole_wheat > 0);
    show('rye', v.rye > 0);
    out('water', shortWater ? DASH : grams(water));
    out('pf', grams(r.pf));
    out('salt', grams(r.salt));
    out('yeast', grams(r.yeast));
    out('oil', grams(r.oil));
    out('sugar', grams(r.sugar));
    show('oil', v.oil > 0);
    show('sugar', v.sugar > 0);
    out('dough_g', grams(r.dough));
    r.short = shortFlour || shortWater;

    ['w_tap', 'ice', 'w_final', 'tw', 't_dough', 't_water'].forEach(function (k) { out(k, DASH); });
    if (!v.temp || r.short) return { v: v, r: r };
    if (v.needKitchen) {
      show('need-kitchen', true);
      return { v: v, r: r };
    }
    if (v.badTemp) return { v: v, r: r };
    if (water < 0.5) {                  // all the water is in the preferment
      show('warn-dry', true);
      return { v: v, r: r };
    }
    var tooCold = r.ice > water, iced = !tooCold && r.tw < v.t_water - 0.5;
    r.iced = iced;
    out('w_tap', grams(water - r.ice));
    out('ice', grams(r.ice));
    out('w_final', grams(water));
    out('tw', degrees(r.tw));
    out('t_dough', num(v.t_dough));
    out('t_water', num(v.t_water));
    show('ice', iced);
    show('no-ice', !tooCold && !iced);
    show('water', true);
    show('warn-ice', tooCold);
    show('warn-hot', r.tw > 40);
    return { v: v, r: r };
  }

  /* The address ------------------------------------------------------------ */
  // Only what differs from the house spec, so the link stays short; what doesn't
  // apply (a preferment's boxes with no preferment, temperatures while closed) is left out.
  function writeUrl(v) {
    var url, d = defaults(v.preferment);
    d.preferment = SPEC.preferment;
    try { url = new URL(location.href); } catch (e) { return; }
    Object.keys(KEYS).forEach(function (name) { url.searchParams.delete(KEYS[name]); });
    url.searchParams.delete(TEMP_OPEN);
    Object.keys(KEYS).forEach(function (name) {
      var x = v[name];
      if ((PF_BOXES.indexOf(name) >= 0 || name === 't_pf') && v.preferment === 'none') return;
      if (name.indexOf('t_') === 0 && !v.temp) return;
      if (typeof x === 'number' && isNaN(x)) return;
      if (x !== d[name]) url.searchParams.set(KEYS[name], String(x));
    });
    if (v.temp) url.searchParams.set(TEMP_OPEN, '1');
    if (url.href !== location.href) {
      try { history.replaceState(history.state, '', url.href); } catch (e) { /* too many calls: harmless */ }
    }
  }

  function readUrl() {
    var q = null;
    try { q = new URL(location.href).searchParams; } catch (e) { /* old browser: the house spec */ }
    function get(name) { return q && has(KEYS, name) ? q.get(KEYS[name]) : null; }
    var pf = get('preferment');
    if (pf !== 'none' && !has(PREFERMENTS, pf)) pf = SPEC.preferment;
    fill(defaults(pf));
    Object.keys(boxes).forEach(function (name) {
      var x = parse(get(name));
      if (!isNaN(x)) boxes[name].value = num(x);
    });
    if (q && q.get(TEMP_OPEN) === '1') temp.open = true;
  }

  function update() {
    var v = render().v;
    clearTimeout(urlTimer);
    urlTimer = setTimeout(function () { writeUrl(v); }, 300);
  }

  /* Changes ---------------------------------------------------------------- */
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  form.addEventListener('input', update);
  form.addEventListener('change', function (e) {
    var el = e.target;
    if (el.name === 'preferment' && el.value !== 'none') {
      var d = defaults(el.value);
      PF_BOXES.forEach(function (name) { boxes[name].value = num(d[name]); });
    }
    update();
  });
  form.addEventListener('focusout', function () { setTimeout(render, 0); });   // mark a box left empty
  temp.addEventListener('toggle', update);

  resetBtn.addEventListener('click', function () {
    fill(defaults(SPEC.preferment));
    update();
  });

  // Phones: the share sheet (Zalo and the rest). Elsewhere: copy the link.
  function copied() {
    show('not-copied', false);
    show('copied', true);
    clearTimeout(copiedTimer);
    copiedTimer = setTimeout(function () { show('copied', false); show('not-copied', true); }, 2500);
  }
  function copyOld(text) {
    var ta = document.createElement('textarea'), ok = false;
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    try { ok = document.execCommand('copy'); } catch (e) { /* not allowed */ }
    document.body.removeChild(ta);
    shareBtn.focus();
    return ok;
  }
  shareBtn.addEventListener('click', function () {
    clearTimeout(urlTimer);
    writeUrl(read());
    var url = location.href;
    if (navigator.share && window.matchMedia('(pointer: coarse)').matches) {
      navigator.share({ title: document.title, url: url }).catch(function () { /* closed */ });
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(copied, function () { if (copyOld(url)) copied(); });
    } else if (copyOld(url)) {
      copied();
    }
  });

  /* The log ---------------------------------------------------------------- */
  function logState(key) { LOG_STATES.forEach(function (k) { show(k, k === key); }); }

  // What goes in the log: the batch as it's set (only what applies), the kitchen,
  // and the weights as totals (preferment included), rounded to a tenth.
  function entry(v, r) {
    var pf = v.preferment !== 'none', batch = { temp: v.temp }, tenth = function (x) { return round(x, 1); };
    Object.keys(KEYS).forEach(function (name) {
      if ((PF_BOXES.indexOf(name) >= 0 || name === 't_pf') && !pf) return;
      if (name.indexOf('t_') === 0 && !v.temp) return;
      batch[name] = v[name];
    });
    var weights = {
      dough: tenth(r.dough), pizza: tenth(r.pizza), whole_wheat: tenth(r.ww), rye: tenth(r.rye),
      water: tenth(r.water), salt: tenth(r.salt), yeast: tenth(r.yeast + r.pfYeast),
      oil: tenth(r.oil), sugar: tenth(r.sugar)
    };
    if (pf) weights.preferment = tenth(r.pf);
    if (r.tw !== undefined) {
      weights.water_c = tenth(r.tw);
      weights.ice = r.iced ? tenth(Math.min(r.ice, r.finalWater)) : 0;
    }
    return {
      day: dayBox.value, made_by: whoBox.value.trim(), notes: notesBox.value.trim(),
      kitchen_c: v.kitchen_c, humidity: v.humidity, dough_c: isNaN(v.dough_c) ? null : v.dough_c,
      batch: batch, weights: weights
    };
  }

  logBtn.addEventListener('click', function () {
    logTried = true;
    var state = render(), v = state.v, r = state.r;
    var noKitchen = KITCHEN.some(function (name) { return isNaN(v[name]); });
    var who = whoBox.value.trim(), day = dayBox.value;
    if (noKitchen) {
      logState('log-kitchen');
      (isNaN(v.kitchen_c) ? boxes.kitchen_c : boxes.humidity).focus();
      return;
    }
    if (v.bad || v.badTemp || v.badLog || !r || r.short) { logState('log-check'); return; }
    if (!who || !day) {
      logState('log-who');
      (day ? whoBox : dayBox).focus();
      return;
    }
    try { localStorage.setItem(NAME_KEY, who); } catch (e) { /* private mode */ }
    logState('log-saving');
    logBtn.disabled = true;
    fetch('/api/dough/log', {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(entry(v, r))
    }).then(function (res) {
      if (res.status === 201) {
        logState('log-saved');
        notesBox.value = '';
        boxes.dough_c.value = '';
        logTried = false;
        render();
      } else {
        logState(res.status === 401 ? 'log-signed-out' : res.status === 503 ? 'log-off' : 'log-failed');
      }
    }, function () { logState('log-failed'); }).then(function () { logBtn.disabled = false; });
  });

  // EN / VI: the boxes and the weights follow the page's number style.
  if (window.MutationObserver) {
    new MutationObserver(function () {
      Object.keys(boxes).forEach(function (name) {
        var x = parse(boxes[name].value);
        if (!isNaN(x)) boxes[name].value = num(x);
      });
      render();
    }).observe(root, { attributes: true, attributeFilter: ['lang'] });
  }

  readUrl();
  dayBox.value = hanoiToday();
  try { whoBox.value = localStorage.getItem(NAME_KEY) || ''; } catch (e) { /* private mode */ }
  render();
})();
