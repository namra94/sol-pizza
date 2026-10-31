/* sol.pizza — the back office's purchase requests, for the Worker (worker/index.js
   sends /api/backoffice/* here once someone is signed in).
   Staff ask for items only: who's asking, the station, when it's needed, and each
   item with how much of it, in what unit, and a note if they like. They never pick a
   supplier, a brand or a price: management chooses those when they order. A staff
   member fills in /backoffice/purchase/ (build/design/purchase.js); this checks it
   all again, trusting nothing from the browser, keeps it in D1 and posts a
   📝 PURCHASE REQUEST to Slack's #supply through an Incoming Webhook (the secret
   SLACK_WEBHOOK_URL), mentioning the station's approver.
   The rest happens in Slack: the approver reacts ✅ (or ❌, with the reason in the
   thread); management chooses the supplier and the brand, posts the 🛒 orders with
   the Order Sheet's Order helper (one per supplier, with Arman's ✅ rules as they have
   always been), then reacts 🛒 on the request. So a request never carries a 🛒: in
   #supply that's an order to a supplier, and the Order desk agent reads it that way.
   The form's suggestions (the names that asked before, the items asked for at each
   station) come from the requests kept here and nowhere else: this repo is public,
   and nothing about suppliers, brands, prices or people is in it.
   With BACKOFFICE_DRY_RUN=1 (`wrangler dev`, the checks) nothing is posted: the answer
   carries the message instead. README-DEPLOY.md, "The back office: purchase requests". */

const MAX_ITEMS = 30;
const MAX_QTY = 100000;
const RECENT = 30;                // requests on /backoffice/purchases/
const STUCK = 60;                 // seconds after which a request still "sending" may be tried again
const LATEST = 500;               // the requests the form's suggestions come from
const PEOPLE = 50;                // names suggested, at most
const ASKED = 300;                // items suggested for each station, at most
const STATIONS = { Kitchen: 'Bếp / Kitchen', Bar: 'Bar', FOH: 'FOH' };   // as the Station line writes them
// The units the form offers (OFFICE_UNITS in build/gen.py), by code: [Vietnamese,
// English]. One is kept as its code, and the message writes it in both languages
// (2 thùng/case; kg, g, L and ml are the same in both). Any other unit was typed
// under "Other…", and is kept and written as typed.
const UNITS = new Map(Object.entries({
  kg: ['kg', 'kg'], g: ['g', 'g'], L: ['L', 'L'], ml: ['ml', 'ml'], pc: ['cái', 'pc'], pack: ['gói', 'pack'],
  box: ['hộp', 'box'], bottle: ['chai', 'bottle'], can: ['lon', 'can'], jar: ['hũ', 'jar'], bag: ['túi', 'bag'],
  sack: ['bao', 'sack'], bunch: ['bó', 'bunch'], tray: ['khay', 'tray'], case: ['thùng', 'case'], roll: ['cuộn', 'roll'],
}));
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// The back office's tables, made on first use in the kitchen's database (DOUGH_DB),
// next to the dough log's. Two older ones may sit beside them, from before staff
// asked for items only: backoffice_purchases (the requests sent then, each with its
// supplier) and backoffice_guide (the Order Sheet's copy the form read then). Nothing
// reads or writes them any more; README-DEPLOY.md says how to drop them.
export const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS backoffice_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref TEXT NOT NULL UNIQUE,         -- REQ-YYMMDD-HHMM, Hanoi time; -2, -3… for more in the same minute
    request_id TEXT NOT NULL UNIQUE,  -- the browser's id for it: a second tap or a retry never posts twice
    created_at TEXT NOT NULL,         -- UTC, ISO 8601
    tried_at INTEGER NOT NULL,        -- when it was last sent to Slack, Unix seconds
    requested_by TEXT NOT NULL,
    station TEXT NOT NULL,            -- Kitchen, Bar or FOH
    needed_by TEXT NOT NULL,          -- YYYY-MM-DD, or YYYY-MM-DD HH:MM, Hanoi time
    items TEXT NOT NULL,              -- JSON: [{item, qty, unit, note}], unit a code from UNITS or as typed
    note TEXT NOT NULL DEFAULT '',
    message TEXT NOT NULL,            -- what went (or would go) to #supply
    slack_status TEXT NOT NULL,       -- sending, sent, failed or dry_run
    slack_error TEXT NOT NULL DEFAULT ''
  )`,
  'CREATE TABLE IF NOT EXISTS backoffice_login_failures (ip TEXT NOT NULL, at INTEGER NOT NULL)',
  'CREATE INDEX IF NOT EXISTS backoffice_login_failures_ip ON backoffice_login_failures (ip, at)',
];

/* The API -------------------------------------------------------------------- */
// GET /api/backoffice/form: what the form suggests, from the latest 500 requests in
// one query: the names that asked, most recent first (50 at most), and the items
// asked for at each station, most-asked first (300 at most for each), each in the
// spelling used last with the unit used most. Never a note. And whether this copy of
// the site only pretends to post (a dry run).
export async function form(env, db) {
  const { results } = await db.prepare('SELECT requested_by, station, items FROM backoffice_requests ORDER BY id DESC LIMIT ?')
    .bind(LATEST).all();
  const people = new Map(), asked = new Map();
  let seen = 0;                   // items gone through, newest first: how long ago one was last asked for
  for (const r of results) {
    const who = key(r.requested_by);
    if (people.size < PEOPLE && !people.has(who)) people.set(who, r.requested_by);
    for (const x of JSON.parse(r.items)) {
      const k = r.station + '\n' + key(x.item);
      if (!asked.has(k)) asked.set(k, { station: r.station, item: x.item, units: new Map(), count: 0, last: seen });
      const a = asked.get(k);
      a.count++;
      a.units.set(x.unit, (a.units.get(x.unit) || 0) + 1);
      seen++;
    }
  }
  const kept = {};                // items so far for each station
  const items = [...asked.values()].sort((a, b) => b.count - a.count || a.last - b.last)
    .filter((a) => (kept[a.station] = (kept[a.station] || 0) + 1) <= ASKED)
    .map((a) => ({ station: a.station, item: a.item, unit: usual(a.units), count: a.count }));
  return { dry_run: env.BACKOFFICE_DRY_RUN === '1', people: [...people.values()], items };
}

// GET /api/backoffice/purchases: the last 30 requests, newest first, with their items
export async function purchases(db) {
  const { results } = await db.prepare(`SELECT ref, created_at, requested_by, station, needed_by, items, slack_status,
      slack_error FROM backoffice_requests ORDER BY id DESC LIMIT ?`).bind(RECENT).all();
  return {
    requests: results.map((r) => ({
      ref: r.ref, created_at: r.created_at, requested_by: r.requested_by, station: r.station, needed_by: r.needed_by,
      items: JSON.parse(r.items), status: r.slack_status, slack_error: r.slack_error,
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

  const r = read(body, now);
  if (r.problem) return [400, { error: 'invalid', field: r.problem }];
  if (preview) {
    const ref = row ? row.ref : await freeRef(db, stamp(now));
    return [200, { preview: true, ref, message: message(r, ref, env) }];
  }

  let ref;
  if (row) {
    ref = row.ref;
    const res = await db.prepare(`UPDATE backoffice_requests SET tried_at = ?, requested_by = ?, station = ?,
        needed_by = ?, items = ?, note = ?, message = ?, slack_status = 'sending', slack_error = ''
      WHERE request_id = ? AND (slack_status = 'failed' OR (slack_status = 'sending' AND tried_at < ?))`)
      .bind(Math.floor(now / 1000), ...columns(r), message(r, ref, env), id, Math.floor(now / 1000) - STUCK).run();
    if (!res.meta.changes) return answer(await settle(db, await byId(db, id)));   // another tap took it
  } else {
    ref = await insert(db, id, r, env, now);
    if (!ref) return answer(await settle(db, await byId(db, id)));                 // the same request, twice at once
  }
  const text = message(r, ref, env);
  const dry = env.BACKOFFICE_DRY_RUN === '1';
  const error = dry ? '' : await post(env, text);
  const status = dry ? 'dry_run' : error ? 'failed' : 'sent';
  await db.prepare('UPDATE backoffice_requests SET slack_status = ?, slack_error = ? WHERE request_id = ?')
    .bind(status, error, id).run();
  return answer({ ref, message: text, slack_status: status, slack_error: error });
}

/* Keeping requests ----------------------------------------------------------- */
async function byId(db, id) {
  return db.prepare('SELECT * FROM backoffice_requests WHERE request_id = ?').bind(id).first();
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
function columns(r) {
  return [r.requested_by, r.station, r.needed_by, JSON.stringify(r.items), r.note];
}

// Keeps a new request, "sending", under the minute's first free ref. null: a request
// with this id got there first.
async function insert(db, id, r, env, now) {
  for (let tries = 0; tries < 5; tries++) {
    const ref = await freeRef(db, stamp(now));
    try {
      await db.prepare(`INSERT INTO backoffice_requests (ref, request_id, created_at, tried_at, requested_by, station,
          needed_by, items, note, message, slack_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'sending')`)
        .bind(ref, id, new Date(now).toISOString(), Math.floor(now / 1000), ...columns(r), message(r, ref, env)).run();
      return ref;
    } catch (err) {
      if (await byId(db, id)) return null;
      if (!/UNIQUE/.test(String(err && err.message))) throw err;   // the ref was taken a moment ago: the next one
    }
  }
  throw new Error('no free ref');
}

// REQ-YYMMDD-HHMM in Hanoi time (UTC+7 all year)
function stamp(ms) {
  const d = new Date(ms + 7 * 3600e3);
  const p = (n) => String(n).padStart(2, '0');
  return `REQ-${p(d.getUTCFullYear() % 100)}${p(d.getUTCMonth() + 1)}${p(d.getUTCDate())}-` +
    `${p(d.getUTCHours())}${p(d.getUTCMinutes())}`;
}

// The minute's ref, or the first of -2, -3… after it that's free
async function freeRef(db, base) {
  const { results } = await db.prepare("SELECT ref FROM backoffice_requests WHERE ref = ?1 OR ref GLOB (?1 || '-[0-9]*')")
    .bind(base).all();
  const taken = new Set(results.map((r) => r.ref));
  let ref = base;
  for (let n = 2; taken.has(ref); n++) ref = `${base}-${n}`;
  return ref;
}

/* The request ---------------------------------------------------------------- */
// The request as it will be posted, read from the form, or { problem: field } for the
// first thing that isn't right. Nothing else in the body counts: a page loaded before
// staff asked for items only may still send a supplier, and it's left out. The
// limits: the name up to 60 characters; 1 to 30 items, each named in up to 80, more
// than 0 and at most 100,000 of it (to 3 decimals), in a unit of up to 20, with a
// note of up to 200; the request's note up to 1,000.
function read(body, now) {
  const who = oneLine(body.requested_by, 60);
  if (!who) return { problem: 'requested_by' };
  if (!Object.keys(STATIONS).includes(body.station)) return { problem: 'station' };
  // Not in the past: today in Hanoi, or yesterday for a request sent just after midnight
  const day = body.needed_by;
  if (!isDay(day) || day < hanoiDay(now - 86400e3)) return { problem: 'needed_by' };
  const time = body.needed_time === undefined ? '' : body.needed_time;
  if (typeof time !== 'string' || (time && !/^([01]\d|2[0-3]):[0-5]\d$/.test(time))) return { problem: 'needed_time' };
  if (!Array.isArray(body.items) || !body.items.length || body.items.length > MAX_ITEMS) return { problem: 'items' };

  const items = [];
  for (const [i, x] of body.items.entries()) {
    const line = x && typeof x === 'object' ? x : {};
    const item = oneLine(line.item, 80);
    if (!item) return { problem: `items.${i}.item` };
    const qty = typeof line.qty === 'number' && Number.isFinite(line.qty) ? Math.round(line.qty * 1000) / 1000 : NaN;
    if (!(qty > 0 && qty <= MAX_QTY)) return { problem: `items.${i}.qty` };
    const unit = oneLine(line.unit, 20);
    if (!unit) return { problem: `items.${i}.unit` };
    const note = oneLine(line.note ?? '', 200);
    if (note === undefined) return { problem: `items.${i}.note` };
    items.push({ item, qty, unit, note });
  }
  const note = oneLine(body.note ?? '', 1000);
  if (note === undefined) return { problem: 'note' };
  return { requested_by: who, station: body.station, needed_by: day + (time ? ' ' + time : ''), items, note };
}

// The 📝 block. Its labels are fixed once it's live, never to change: an agent may
// read #supply by them. It never has a 🛒 (an order to a supplier, which management
// posts once they've chosen one) and mentions no one but the station's approver.
function message(r, ref, env) {
  const lines = [
    '📝 YÊU CẦU MUA HÀNG / PURCHASE REQUEST',
    'Bộ phận / Station: ' + STATIONS[r.station],
    'Cần lúc / Needed by: ' + when(r.needed_by),
    'Hàng / Items:',
  ].concat(r.items.map((x) => '• ' + slack(x.item) + ' — ' + number(x.qty) + ' ' + unitText(x.unit) +
    (x.note ? ' (' + slack(x.note) + ')' : '')));
  lines.push('Người yêu cầu / Requested by: ' + slack(r.requested_by));
  if (r.note) lines.push('Ghi chú / Note: ' + slack(r.note));
  lines.push('Duyệt / Approve: ' + (r.station === 'Kitchen'
    ? mention(env.SLACK_APPROVER_KITCHEN, 'Kitchen approver')
    : mention(env.SLACK_APPROVER_BAR_FOH, 'Bar & FOH approver')) + ' ✅ / ❌');
  lines.push('Đặt hàng / Ordering: quản lý chọn NCC và thương hiệu / management picks the supplier and brand');
  lines.push('_Gửi từ sol.pizza/backoffice · Ref ' + ref + '_');
  return lines.join('\n');
}

// A unit as the message writes it: one from UNITS in both languages (bó/bunch, but kg
// as it is), any other as typed
function unitText(unit) {
  const names = UNITS.get(unit);
  if (!names) return slack(unit);
  return names[0] === names[1] ? names[0] : names.join('/');
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

/* The suggestions ------------------------------------------------------------ */
// Two spellings of one name or item, made the same: one form (NFC), no capitals,
// single spaces. The accents stay: bơ (butter) and bò (beef) are two items.
function key(s) {
  return s.normalize('NFC').toLowerCase().replace(/\s+/g, ' ').trim();
}

// The unit used most; of two used as often, the one used last (the first one in)
function usual(units) {
  let best = '', n = 0;
  for (const [unit, count] of units) if (count > n) [best, n] = [unit, count];
  return best;
}

/* Text ----------------------------------------------------------------------- */
// Someone's text on one line: no control or invisible formatting characters, line
// breaks and tabs as spaces, Vietnamese in one form (NFC) so names match, and no 🛒
// (nor Slack's :shopping_trolley:, which shows as one): in #supply that's an order to
// a supplier, never a request. Too long, or not text: undefined.
function oneLine(value, most) {
  if (typeof value !== 'string') return undefined;
  const s = value.normalize('NFC').replace(/[\r\n\t\u2028\u2029]+/g, ' ')
    .replace(/[\u0000-\u001f\u007f-\u009f\u200b-\u200f\u202a-\u202e\u2060-\u2069\ufeff]/g, '')
    .replace(/\u{1f6d2}\ufe0f?|:shopping_trolley:/giu, '')
    .replace(/ {2,}/g, ' ').trim();
  return s.length <= most ? s : undefined;
}

// Slack reads &, < and > as markup (<!channel>, <@someone>, links): as text, always
function slack(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// A Slack mention by member id, or the role as text when the id isn't set
function mention(id, role) {
  return typeof id === 'string' && /^[UW][A-Z0-9]{2,}$/.test(id) ? `<@${id}>` : slack(role);
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
