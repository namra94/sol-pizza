/* sol.pizza — the back office's purchase requests, for the Worker (worker/index.js
   sends /api/backoffice/* here once someone is signed in).
   A staff member fills in /backoffice/purchase/ (build/design/purchase.js). This
   works the request out again from the Order Guide, never from what the browser
   says: the supplier and each item by their exact names, the units and prices from
   the guide, the estimate, who approves. It keeps the request in D1 and posts it to
   Slack's #supply through an Incoming Webhook (the secret SLACK_WEBHOOK_URL), in the
   🛒 format management already uses: the Order Sheet's "Order helper" writes the
   same block and an Order desk agent reads #supply by its labels, so those stay
   exactly as they are. Approval happens in Slack, with reactions.
   The Order Guide is the Order Sheet's suppliers, items, prices and settings, read
   at run time from a Google Apps Script web app (tools/order-sheet.gs; its address
   with ?token= is the secret ORDER_GUIDE_URL), kept in D1 and fetched again once
   it's 10 minutes old; when the sheet can't be reached, the last good copy. This
   repo is public: no supplier, price or person from the sheet is ever in it.
   Without a guide the form still works: everything typed by hand, no estimate, and
   Arman's ✅ always needed. With BACKOFFICE_DRY_RUN=1 (`wrangler dev`, the checks)
   nothing is posted, the answer carries the message instead, and with no
   ORDER_GUIDE_URL the guide is the fake one in worker/backoffice-sample.json.
   README-DEPLOY.md, "The back office: purchase requests". */

import SAMPLE from './backoffice-sample.json' with { type: 'json' };

const FRESH = 10 * 60;            // the Order Guide is fetched again once it's 10 minutes old
const RETRY = 60;                 // but not within a minute of a fetch that failed
const LIMIT = 5000000;            // đồng before VAT, only if the Settings tab has no approval limit
const MAX_ITEMS = 30;
const MAX_QTY = 100000;
const RECENT = 30;                // requests on /backoffice/purchases/
const STUCK = 60;                 // seconds after which a request still "sending" may be tried again
const STATIONS = { Kitchen: 'Bếp / Kitchen', Bar: 'Bar', FOH: 'FOH' };   // as the Station line writes them
const STATUSES = ['Active', 'Quoting', 'Not used yet', 'Stopped'];
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// The back office's tables, made on first use in the kitchen's database (DOUGH_DB),
// next to the dough log's
export const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS backoffice_purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref TEXT NOT NULL UNIQUE,         -- SOL-YYMMDD-HHMM, Hanoi time; -2, -3… for more in the same minute
    request_id TEXT NOT NULL UNIQUE,  -- the browser's id for it: a second tap or a retry never posts twice
    created_at TEXT NOT NULL,         -- UTC, ISO 8601
    tried_at INTEGER NOT NULL,        -- when it was last sent to Slack, Unix seconds
    requested_by TEXT NOT NULL,
    supplier TEXT NOT NULL,
    listed INTEGER NOT NULL,          -- 1: a supplier in the Order Sheet
    station TEXT NOT NULL,            -- Kitchen, Bar or FOH
    needed_by TEXT NOT NULL,          -- YYYY-MM-DD, or YYYY-MM-DD HH:MM, Hanoi time
    items TEXT NOT NULL,              -- JSON: [{item, qty, unit, note, price}], price null when unpriced
    note TEXT NOT NULL DEFAULT '',
    estimate INTEGER NOT NULL,        -- đồng before VAT, from the priced items
    owner_needed INTEGER NOT NULL,    -- 1: Arman's ✅ too
    message TEXT NOT NULL,            -- what went (or would go) to #supply
    slack_status TEXT NOT NULL,       -- sending, sent, failed or dry_run
    slack_error TEXT NOT NULL DEFAULT ''
  )`,
  `CREATE TABLE IF NOT EXISTS backoffice_guide (
    id INTEGER PRIMARY KEY CHECK (id = 1),   -- one row
    fetched_at INTEGER,               -- when the last good copy came from the Order Sheet, Unix seconds
    failed_at INTEGER,                -- the last fetch that failed
    guide TEXT                        -- JSON: that copy, tidied (tidy())
  )`,
  'CREATE TABLE IF NOT EXISTS backoffice_login_failures (ip TEXT NOT NULL, at INTEGER NOT NULL)',
  'CREATE INDEX IF NOT EXISTS backoffice_login_failures_ip ON backoffice_login_failures (ip, at)',
];

/* The API -------------------------------------------------------------------- */
// GET /api/backoffice/guide: the Order Guide for the form, how fresh it is, and
// whether this copy of the site only pretends to post (a dry run)
export async function guide(env, db) {
  return { ...(await orderGuide(env, db)), dry_run: env.BACKOFFICE_DRY_RUN === '1' };
}

// GET /api/backoffice/purchases: the last 30 requests, newest first
export async function purchases(db) {
  const { results } = await db.prepare(`SELECT ref, created_at, requested_by, supplier, station, needed_by, items,
      estimate, owner_needed, slack_status FROM backoffice_purchases ORDER BY id DESC LIMIT ?`).bind(RECENT).all();
  return {
    requests: results.map((r) => ({
      ref: r.ref, created_at: r.created_at, requested_by: r.requested_by, supplier: r.supplier, station: r.station,
      needed_by: r.needed_by, items: JSON.parse(r.items).length, estimate: r.estimate,
      owner_needed: !!r.owner_needed, status: r.slack_status,
    })),
  };
}

// POST /api/backoffice/purchase: [status, answer]. With preview: true, the message it
// would post, and nothing kept. Otherwise the request is kept and posted once: an id
// seen before gets that request's answer (a second tap, a retry after the answer was
// lost on the way); one that failed is tried again, as the form says now, under its
// first ref.
export async function purchase(env, db, body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return [400, { error: 'invalid', field: 'body' }];
  const preview = body.preview === true;
  const id = typeof body.request_id === 'string' && UUID.test(body.request_id) ? body.request_id.toLowerCase() : '';
  if (!preview && !id) return [400, { error: 'invalid', field: 'request_id' }];
  const now = Date.now();
  const row = id ? await byId(db, id) : null;
  if (row && !preview && !retry(row, now)) return answer(await settle(db, row));

  const { guide } = await orderGuide(env, db);
  const o = order(body, guide, now);
  if (o.problem) return [400, { error: 'invalid', field: o.problem }];
  if (preview) {
    const ref = row ? row.ref : await freeRef(db, stamp(now));
    return [200, { preview: true, ref, message: message(o, ref, env), ...summary(o) }];
  }

  let ref;
  if (row) {
    ref = row.ref;
    const res = await db.prepare(`UPDATE backoffice_purchases SET tried_at = ?, requested_by = ?, supplier = ?,
        listed = ?, station = ?, needed_by = ?, items = ?, note = ?, estimate = ?, owner_needed = ?, message = ?,
        slack_status = 'sending', slack_error = ''
      WHERE request_id = ? AND (slack_status = 'failed' OR (slack_status = 'sending' AND tried_at < ?))`)
      .bind(Math.floor(now / 1000), ...columns(o), message(o, ref, env), id, Math.floor(now / 1000) - STUCK).run();
    if (!res.meta.changes) return answer(await settle(db, await byId(db, id)));   // another tap took it
  } else {
    ref = await insert(db, id, o, env, now);
    if (!ref) return answer(await settle(db, await byId(db, id)));                 // the same request, twice at once
  }
  const text = message(o, ref, env);
  const dry = env.BACKOFFICE_DRY_RUN === '1';
  const error = dry ? '' : await post(env, text);
  const status = dry ? 'dry_run' : error ? 'failed' : 'sent';
  await db.prepare('UPDATE backoffice_purchases SET slack_status = ?, slack_error = ? WHERE request_id = ?')
    .bind(status, error, id).run();
  return answer({ ref, message: text, slack_status: status, slack_error: error });
}

/* Keeping requests ----------------------------------------------------------- */
async function byId(db, id) {
  return db.prepare('SELECT * FROM backoffice_purchases WHERE request_id = ?').bind(id).first();
}

// May this request be sent again? It failed, or it has been "sending" too long to be.
function retry(row, now) {
  return row.slack_status === 'failed' || (row.slack_status === 'sending' && row.tried_at < now / 1000 - STUCK);
}

// A request another tap is still sending: wait for it, up to about eight seconds
async function settle(db, row) {
  for (let i = 0; i < 25 && row && row.slack_status === 'sending' && !retry(row, Date.now()); i++) {
    await new Promise((resolve) => setTimeout(resolve, 300));
    row = await byId(db, row.request_id);
  }
  return row;
}

// What the browser gets for a request that's in: sent (or a dry run), still being
// sent, or failed with what Slack said
function answer(row) {
  if (!row) return [500, { error: 'server' }];
  if (row.slack_status === 'sent') return [200, { ok: true, ref: row.ref, message: row.message }];
  if (row.slack_status === 'dry_run') return [200, { ok: true, dry_run: true, ref: row.ref, message: row.message }];
  if (row.slack_status === 'sending') return [409, { error: 'sending', ref: row.ref }];
  return [502, { error: 'slack', detail: row.slack_error, ref: row.ref }];
}

// The request's own columns, in the order insert() and purchase() write them
function columns(o) {
  return [o.requested_by, o.supplier, o.listed ? 1 : 0, o.station, o.needed_by, JSON.stringify(o.items), o.note,
    o.estimate, o.owner_needed ? 1 : 0];
}

// Keeps a new request, "sending", under the minute's first free ref. null: a request
// with this id got there first.
async function insert(db, id, o, env, now) {
  for (let tries = 0; tries < 5; tries++) {
    const ref = await freeRef(db, stamp(now));
    try {
      await db.prepare(`INSERT INTO backoffice_purchases (ref, request_id, created_at, tried_at, requested_by,
          supplier, listed, station, needed_by, items, note, estimate, owner_needed, message, slack_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'sending')`)
        .bind(ref, id, new Date(now).toISOString(), Math.floor(now / 1000), ...columns(o), message(o, ref, env)).run();
      return ref;
    } catch (err) {
      if (await byId(db, id)) return null;
      if (!/UNIQUE/.test(String(err && err.message))) throw err;   // the ref was taken a moment ago: the next one
    }
  }
  throw new Error('no free ref');
}

// SOL-YYMMDD-HHMM in Hanoi time (UTC+7 all year)
function stamp(ms) {
  const d = new Date(ms + 7 * 3600e3);
  const p = (n) => String(n).padStart(2, '0');
  return `SOL-${p(d.getUTCFullYear() % 100)}${p(d.getUTCMonth() + 1)}${p(d.getUTCDate())}-` +
    `${p(d.getUTCHours())}${p(d.getUTCMinutes())}`;
}

// The minute's ref, or the first of -2, -3… after it that's free
async function freeRef(db, base) {
  const { results } = await db.prepare("SELECT ref FROM backoffice_purchases WHERE ref = ?1 OR ref GLOB (?1 || '-[0-9]*')")
    .bind(base).all();
  const taken = new Set(results.map((r) => r.ref));
  let ref = base;
  for (let n = 2; taken.has(ref); n++) ref = `${base}-${n}`;
  return ref;
}

/* The request ---------------------------------------------------------------- */
// The request as it will be posted, worked out from the form and the Order Guide,
// or { problem: field } for the first thing that isn't right. The limits: names up
// to 60 characters (one from the Order Guide as it is), other fields 200, the note
// 1,000; 1 to 30 items, each more than 0 and at most 100,000.
function order(body, guide, now) {
  const who = oneLine(body.requested_by, 60);
  if (!who) return { problem: 'requested_by' };
  const named = oneLine(body.supplier, 200);
  const supplier = named && guide ? guide.suppliers.find((s) => s.name === named) : undefined;
  if (!named || (!supplier && named.length > 60)) return { problem: 'supplier' };
  if (!Object.keys(STATIONS).includes(body.station)) return { problem: 'station' };
  // Not in the past: today in Hanoi, or yesterday for a request sent just after midnight
  const day = body.needed_by;
  if (!isDay(day) || day < hanoiDay(now - 86400e3)) return { problem: 'needed_by' };
  const time = body.needed_time === undefined ? '' : body.needed_time;
  if (typeof time !== 'string' || (time && !/^([01]\d|2[0-3]):[0-5]\d$/.test(time))) return { problem: 'needed_time' };
  if (!Array.isArray(body.items) || !body.items.length || body.items.length > MAX_ITEMS) return { problem: 'items' };

  const offered = supplier ? guide.items.filter((x) => x.supplier === supplier.name) : [];
  const items = [];
  for (const [i, x] of body.items.entries()) {
    const line = x && typeof x === 'object' ? x : {};
    const name = oneLine(line.item, 200);
    const known = name ? offered.find((it) => it.name === name) : undefined;
    if (!name || (!known && name.length > 60)) return { problem: `items.${i}.item` };
    const qty = typeof line.qty === 'number' && Number.isFinite(line.qty) ? Math.round(line.qty * 1000) / 1000 : NaN;
    if (!(qty > 0 && qty <= MAX_QTY)) return { problem: `items.${i}.qty` };
    const unit = oneLine(line.unit ?? '', 200), note = oneLine(line.note ?? '', 200);
    if (unit === undefined) return { problem: `items.${i}.unit` };
    if (note === undefined) return { problem: `items.${i}.note` };
    items.push(known ? { item: known.name, qty, unit: known.unit || unit, note, price: known.price }
      : { item: name, qty, unit, note, price: null });
  }
  const note = oneLine(body.note ?? '', 1000);
  if (note === undefined) return { problem: 'note' };

  // The Order Sheet's rule: the station's approver, and Arman too above the limit
  // or for a supplier that isn't Active (one not in the sheet isn't)
  const settings = guide ? guide.settings : { limit: LIMIT };
  const estimate = Math.round(items.reduce((sum, x) => sum + (x.price === null ? 0 : x.qty * x.price), 0));
  const over = estimate > settings.limit;
  const inactive = !supplier || supplier.status !== 'Active';
  return {
    requested_by: who, supplier: supplier ? supplier.name : named, listed: !!supplier, station: body.station,
    needed_by: day + (time ? ' ' + time : ''), items, note, estimate, limit: settings.limit, over, inactive,
    owner_needed: over || inactive, settings,
  };
}

function summary(o) {
  return { estimate: o.estimate, owner_needed: o.owner_needed, over: o.over, inactive: o.inactive, listed: o.listed };
}

// The 🛒 block. Its labels never change: the Order helper writes the same, and the
// Order desk agent reads #supply by them.
function message(o, ref, env) {
  const lines = [
    '🛒 ĐẶT HÀNG / ORDER',
    'NCC / Supplier: ' + slack(o.supplier),
    'Bộ phận / Station: ' + STATIONS[o.station],
    'Cần lúc / Needed by: ' + when(o.needed_by),
    'Hàng / Items:',
  ].concat(o.items.map((x) => '• ' + slack(x.item) + ' — ' + number(x.qty) + (x.unit ? ' ' + slack(x.unit) : '') +
    (x.note ? ' (' + slack(x.note) + ')' : '')));
  if (o.estimate > 0) lines.push('Ước tính / Est.: ~' + number(o.estimate) + 'đ chưa VAT / before VAT');
  lines.push('Người yêu cầu / Requested by: ' + slack(o.requested_by));
  if (o.note) lines.push('Ghi chú / Note: ' + slack(o.note));
  if (o.owner_needed) {
    const why = [];
    if (o.over) why.push('trên / over ' + number(o.limit) + 'đ');
    if (o.inactive) why.push('NCC chưa Active / supplier not Active yet');
    lines.push('⚠️ Cần anh Arman vì / Arman needed because: ' + why.join(', ') + ' — ' +
      mention(env.SLACK_OWNER, o.settings.owner || 'Arman'));
  }
  lines.push('Duyệt / Approve: ' + (o.station === 'Kitchen'
    ? mention(env.SLACK_APPROVER_KITCHEN, o.settings.kitchen_approver || 'Kitchen approver')
    : mention(env.SLACK_APPROVER_BAR_FOH, o.settings.barfoh_approver || 'Bar & FOH approver')) + ' ✅');
  lines.push('_Gửi từ sol.pizza/backoffice · Ref ' + ref + '_');
  return lines.join('\n');
}

// Posts to #supply: '' when Slack took it, else what went wrong (never the address)
async function post(env, text) {
  const url = env.SLACK_WEBHOOK_URL;
  if (!url) return 'SLACK_WEBHOOK_URL is not set';
  try {
    const res = await fetch(url, {
      method: 'POST', headers: { 'Content-Type': 'application/json; charset=utf-8' },
      body: JSON.stringify({ text, unfurl_links: false, unfurl_media: false }),
      signal: AbortSignal.timeout(10000),
    });
    if (res.ok) return '';
    return `Slack answered ${res.status}: ${(await res.text()).slice(0, 200)}`;
  } catch (err) {
    const why = err && err.name === 'TimeoutError' ? 'no answer in 10 seconds' : String((err && err.message) || err);
    return ('Slack could not be reached: ' + why).split(url).join('…').slice(0, 300);
  }
}

/* The Order Guide ------------------------------------------------------------ */
// The guide and how fresh it is: from D1 while it's under 10 minutes old, else from
// the Order Sheet; if that fails, the last good copy (stale, as of when it came).
async function orderGuide(env, db) {
  if (!env.ORDER_GUIDE_URL) {
    const sample = env.BACKOFFICE_DRY_RUN === '1' ? tidy(SAMPLE) : null;
    return { guide: sample, source: sample ? 'sample' : null, as_of: null, stale: false };
  }
  const now = Math.floor(Date.now() / 1000);
  const row = await db.prepare('SELECT fetched_at, failed_at, guide FROM backoffice_guide WHERE id = 1').first();
  const kept = row && row.guide
    ? { guide: JSON.parse(row.guide), source: 'sheet', as_of: new Date(row.fetched_at * 1000).toISOString(), stale: false }
    : null;
  if (kept && row.fetched_at > now - FRESH) return kept;
  if (!(row && row.failed_at > now - RETRY)) {
    const guide = await fetchGuide(env.ORDER_GUIDE_URL);
    if (guide) {
      await db.prepare(`INSERT INTO backoffice_guide (id, fetched_at, failed_at, guide) VALUES (1, ?1, NULL, ?2)
        ON CONFLICT (id) DO UPDATE SET fetched_at = ?1, failed_at = NULL, guide = ?2`)
        .bind(now, JSON.stringify(guide)).run();
      return { guide, source: 'sheet', as_of: new Date(now * 1000).toISOString(), stale: false };
    }
    await db.prepare('INSERT INTO backoffice_guide (id, failed_at) VALUES (1, ?1) ON CONFLICT (id) DO UPDATE SET failed_at = ?1')
      .bind(now).run();
  }
  return kept ? { ...kept, stale: true } : { guide: null, source: null, as_of: null, stale: false };
}

async function fetchGuide(url) {
  try {
    const res = await fetch(url, { headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(8000) });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const raw = await res.json();
    if (raw && raw.error) throw new Error('the Order Sheet says: ' + String(raw.error));
    const guide = tidy(raw);
    if (!guide) throw new Error('not an Order Guide');
    return guide;
  } catch (err) {
    const why = err && err.name === 'TimeoutError' ? 'no answer in 8 seconds' : String((err && err.message) || err);
    console.error('Order Guide: ' + why.split(url).join('ORDER_GUIDE_URL').slice(0, 300));   // never the token
    return null;
  }
}

// What the Order Sheet's web app sends (tools/order-sheet.gs), checked and tidied:
// texts cut to size, numbers as numbers or null, each item's name unique within its
// supplier (the pack goes after a name that comes twice), and only items of a
// supplier on the Suppliers tab. null if it isn't an Order Guide.
function tidy(raw) {
  if (!raw || typeof raw !== 'object' || raw.error || !Array.isArray(raw.suppliers) || !Array.isArray(raw.items)) {
    return null;
  }
  const set = raw.settings && typeof raw.settings === 'object' ? raw.settings : {};
  const suppliers = [], items = [], names = new Set(), seen = new Set();
  for (const s of raw.suppliers.slice(0, 500)) {
    const name = s ? cut(s.name) : '';
    if (!name || names.has(name)) continue;
    names.add(name);
    suppliers.push({
      name, supplies: cut(s.supplies), station: spelt(Object.keys(STATIONS), s.station),
      status: spelt(STATUSES, s.status) || cut(s.status, 40), owner: cut(s.owner, 60), order_days: cut(s.order_days),
      cutoff: cut(s.cutoff), delivery: cut(s.delivery), min_order: cut(s.min_order),
    });
  }
  for (const it of raw.items.slice(0, 5000)) {
    const supplier = it ? cut(it.supplier) : '';
    let name = it ? cut(it.en) || cut(it.vn) : '';
    if (!names.has(supplier) || !name) continue;
    const pack = cut(it.pack, 60);
    if (seen.has(supplier + '\n' + name) && pack) name += ` (${pack})`;
    if (seen.has(supplier + '\n' + name)) continue;
    seen.add(supplier + '\n' + name);
    items.push({
      supplier, name, vn: cut(it.vn), unit: cut(it.unit, 40), unit_vn: cut(it.unit_vn, 40), pack,
      price: amount(it.price), vat: cut(it.vat, 40), category: cut(it.category, 60), notes: cut(it.notes),
      code: cut(it.code, 40),
    });
  }
  return {
    updated: cut(raw.updated, 40),
    settings: {
      limit: amount(set.limit) ?? LIMIT,
      kitchen_approver: cut(set.kitchen_approver, 60),
      barfoh_approver: cut(set.barfoh_approver, 60),
      owner: cut(set.owner, 60),
    },
    staff: [...new Set((Array.isArray(raw.staff) ? raw.staff : []).map((x) => cut(x, 60)).filter(Boolean))].slice(0, 200),
    suppliers,
    items,
  };
}

/* Text ----------------------------------------------------------------------- */
// Someone's text on one line: no control or invisible formatting characters, line
// breaks and tabs as spaces, Vietnamese in one form (NFC) so names match. Too long,
// or not text: undefined.
function oneLine(value, most) {
  if (typeof value !== 'string') return undefined;
  const s = value.normalize('NFC').replace(/[\r\n\t\u2028\u2029]+/g, ' ')
    .replace(/[\u0000-\u001f\u007f-\u009f\u200b-\u200f\u202a-\u202e\u2060-\u2069\ufeff]/g, '')
    .replace(/ {2,}/g, ' ').trim();
  return s.length <= most ? s : undefined;
}

// A text from the Order Sheet, the same way, cut to size rather than refused
function cut(value, most = 200) {
  if (typeof value === 'number' && Number.isFinite(value)) value = String(value);
  return typeof value === 'string' ? oneLine(value, Infinity).slice(0, most) : '';
}

// The listed spelling of a value, whatever its case ('foh' is FOH); '' if it isn't listed
function spelt(list, value) {
  const v = cut(value).toLowerCase();
  return list.find((x) => x.toLowerCase() === v) || '';
}

function amount(value) {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : null;
}

// Slack reads &, < and > as markup (<!channel>, <@someone>, links): as text, always
function slack(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// A Slack mention by member id, or the name as text when the id isn't set
function mention(id, name) {
  return typeof id === 'string' && /^[UW][A-Z0-9]{2,}$/.test(id) ? `<@${id}>` : slack(name);
}

// The message's numbers, whatever the page's language: 1,250,000 and 1.5
function number(x) {
  const [whole, part] = String(x).split('.');
  return whole.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (part ? '.' + part : '');
}

function isDay(day) {
  if (typeof day !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(day)) return false;
  const d = new Date(day + 'T00:00:00Z');
  return !Number.isNaN(d.getTime()) && d.toISOString().startsWith(day);
}

function hanoiDay(ms) {
  return new Date(ms + 7 * 3600e3).toISOString().slice(0, 10);
}

// Thu 5 Nov 2026, 10:00: the day and time as typed, Hanoi time
function when(neededBy) {
  const [day, time] = neededBy.split(' ');
  const [y, m, d] = day.split('-').map(Number);
  return `${DAYS[new Date(Date.UTC(y, m - 1, d)).getUTCDay()]} ${d} ${MONTHS[m - 1]} ${y}` + (time ? ', ' + time : '');
}
