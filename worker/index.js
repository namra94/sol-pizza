/* sol.pizza — the Worker in front of the static site.
   Everything else is the files in dist/ (build/gen.py), served by Cloudflare as
   they are. wrangler.jsonc runs this first only for the kitchen, /dough/* and
   /api/*, and it
     - keeps /dough/ (the dough calculator, the dough log) behind the kitchen
       password, the secret DOUGH_PASSWORD (README-DEPLOY.md, "The kitchen");
     - keeps the dough log in D1 (the DOUGH_DB binding) and serves it as JSON for
       the pages and as a CSV to download.
   Signed in = the cookie sol_dough: an expiry and an HMAC of it keyed with the
   password, so changing the password signs every phone out. With no password set
   (a Preview, unless it's given one), /dough/ stays locked and says so; with no
   database the calculator works but the log says it isn't set up.
   Anything else that reaches the Worker (an address with no file) goes back to
   the static site, which shows the 404 page. */

const COOKIE = 'sol_dough';
const SESSION_DAYS = 30;
const LOGIN = '/dough/login/';
const HOME = '/dough/';
const PAGE = 50;                        // log entries per page
const MAX_TRIES = 10;                   // wrong passwords per address per 15 minutes
const TRIES_WINDOW = 15 * 60;

// Security headers as dist/_headers sets them on the static site: _headers doesn't
// reach what the Worker answers. The kitchen's pages are private and never cached.
const SECURITY = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'SAMEORIGIN',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=()',
};
const PRIVATE = { 'Cache-Control': 'private, no-store', 'X-Robots-Tag': 'noindex, nofollow' };

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    try {
      if (path.startsWith('/api/')) return await api(request, env, url);
      if (path === '/dough' || path.startsWith('/dough/')) return await kitchen(request, env, url);
      return withHeaders(await env.ASSETS.fetch(request), SECURITY);
    } catch (err) {
      console.error(err);
      return json({ error: 'server' }, 500);
    }
  },
};

/* Responses ------------------------------------------------------------------ */
function withHeaders(res, headers) {
  const out = new Response(res.body, res);
  for (const [k, v] of Object.entries(headers)) out.headers.set(k, v);
  return out;
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...SECURITY, ...PRIVATE },
  });
}

function redirect(to, extra = {}) {
  return new Response(null, { status: 303, headers: { Location: to, ...PRIVATE, ...extra } });
}

/* Signing in ----------------------------------------------------------------- */
const enc = new TextEncoder();

async function hmac(key, data) {
  const k = await crypto.subtle.importKey('raw', enc.encode(key), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = new Uint8Array(await crypto.subtle.sign('HMAC', k, enc.encode(data)));
  return [...sig].map((b) => b.toString(16).padStart(2, '0')).join('');
}

// Compares two strings of the same length without stopping at the first difference
function same(a, b) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

// Both sides hashed first, so the comparison takes the same time whatever was typed
async function rightPassword(given, env) {
  return same(await hmac('sol-dough-password', given), await hmac('sol-dough-password', env.DOUGH_PASSWORD));
}

async function session(env, exp) {
  return exp + '.' + (await hmac('sol-dough-session\n' + env.DOUGH_PASSWORD, String(exp)));
}

function cookie(value, maxAge) {
  return `${COOKIE}=${value}; Path=/; Max-Age=${maxAge}; HttpOnly; Secure; SameSite=Lax`;
}

async function signedIn(request, env) {
  if (!env.DOUGH_PASSWORD) return false;
  const m = new RegExp(`(?:^|;\\s*)${COOKIE}=(\\d+)\\.([0-9a-f]{64})(?:;|$)`).exec(request.headers.get('Cookie') || '');
  if (!m || Number(m[1]) < Date.now() / 1000) return false;
  return same(await session(env, m[1]), `${m[1]}.${m[2]}`);
}

// Where to go after signing in: a kitchen page, never somewhere else
function safeNext(next) {
  return typeof next === 'string' && /^\/dough\/[\w\-./?=&%]*$/.test(next) && !next.includes('..') &&
    !next.startsWith(LOGIN) ? next : HOME;
}

function loginUrl(next, flag) {
  const q = [];
  if (flag) q.push(flag + '=1');
  if (next !== HOME) q.push('next=' + encodeURIComponent(next));
  return LOGIN + (q.length ? '?' + q.join('&') : '');
}

/* The kitchen's pages -------------------------------------------------------- */
async function kitchen(request, env, url) {
  const path = url.pathname;
  const next = safeNext(url.searchParams.get('next'));
  if (/^\/dough\/login(\/(index\.html)?)?$/.test(path)) {
    if (await signedIn(request, env)) return redirect(next);
    const flag = !env.DOUGH_PASSWORD ? 'off' : ['wrong', 'wait'].find((f) => url.searchParams.has(f));
    let rewriter = new HTMLRewriter().on('input[name="next"]', {
      element(el) { el.setAttribute('value', next); },
    });
    if (flag) {
      rewriter = rewriter.on(`[data-if="${flag}"]`, { element(el) { el.removeAttribute('hidden'); } });
    }
    return withHeaders(rewriter.transform(await env.ASSETS.fetch(request)), { ...SECURITY, ...PRIVATE });
  }
  if (!(await signedIn(request, env))) return redirect(loginUrl(safeNext(path + url.search)));
  return withHeaders(await env.ASSETS.fetch(request), { ...SECURITY, ...PRIVATE });
}

/* The API -------------------------------------------------------------------- */
async function api(request, env, url) {
  const path = url.pathname;
  const method = request.method;
  if (path === '/api/dough/login') return login(request, env);
  if (path === '/api/dough/logout') return redirect(LOGIN, { 'Set-Cookie': cookie('', 0) });
  if (!path.startsWith('/api/dough/')) return json({ error: 'not found' }, 404);
  if (!(await signedIn(request, env))) return json({ error: 'signed out' }, 401);
  // Changes come from the kitchen's own pages only
  const origin = request.headers.get('Origin');
  if (method !== 'GET' && method !== 'HEAD' && origin && origin !== url.origin) return json({ error: 'forbidden' }, 403);
  if (!env.DOUGH_DB) return json({ error: 'no database' }, 503);
  const db = await database(env);

  if (path === '/api/dough/log' && method === 'GET') return list(db, url);
  if (path === '/api/dough/log' && method === 'POST') return add(db, request);
  if (path === '/api/dough/log.csv' && method === 'GET') return csv(db);
  const one = /^\/api\/dough\/log\/(\d+)$/.exec(path);
  if (one && method === 'DELETE') {
    const res = await db.prepare('DELETE FROM dough_log WHERE id = ?').bind(Number(one[1])).run();
    return res.meta.changes ? json({ ok: true }) : json({ error: 'not found' }, 404);
  }
  return json({ error: 'not found' }, 404);
}

async function login(request, env) {
  if (request.method !== 'POST') return redirect(LOGIN);
  const form = await request.formData();
  const next = safeNext(form.get('next'));
  if (!env.DOUGH_PASSWORD) return redirect(loginUrl(next, 'off'));
  const db = env.DOUGH_DB ? await database(env) : null;
  const ip = request.headers.get('CF-Connecting-IP') || 'local';
  const now = Math.floor(Date.now() / 1000);
  if (db) {
    const row = await db.prepare('SELECT COUNT(*) AS n FROM dough_login_failures WHERE ip = ? AND at > ?')
      .bind(ip, now - TRIES_WINDOW).first();
    if (row.n >= MAX_TRIES) return redirect(loginUrl(next, 'wait'));
  }
  if (!(await rightPassword(String(form.get('password') || ''), env))) {
    if (db) {
      await db.batch([
        db.prepare('INSERT INTO dough_login_failures (ip, at) VALUES (?, ?)').bind(ip, now),
        db.prepare('DELETE FROM dough_login_failures WHERE at < ?').bind(now - 86400),
      ]);
    }
    return redirect(loginUrl(next, 'wrong'));
  }
  if (db) await db.prepare('DELETE FROM dough_login_failures WHERE ip = ?').bind(ip).run();
  const maxAge = SESSION_DAYS * 86400;
  return redirect(next, { 'Set-Cookie': cookie(await session(env, now + maxAge), maxAge) });
}

/* The log in D1 -------------------------------------------------------------- */
// The tables are made on first use, so a new database (and `wrangler dev`'s local
// one) needs no setup. To change them later, add a migration (README-DEPLOY.md).
const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS dough_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT NOT NULL,            -- the day it was mixed, YYYY-MM-DD
    logged_at TEXT NOT NULL,      -- when it was logged, UTC, ISO 8601
    made_by TEXT NOT NULL,
    balls INTEGER NOT NULL,
    ball_g REAL NOT NULL,
    dough_g REAL NOT NULL,
    kitchen_c REAL NOT NULL,      -- the kitchen's temperature, °C
    humidity REAL NOT NULL,       -- the kitchen's air humidity, %
    dough_c REAL,                 -- the dough's temperature after mixing, °C, if taken
    notes TEXT NOT NULL DEFAULT '',
    batch TEXT NOT NULL,          -- JSON: the calculator's boxes as they were set
    weights TEXT NOT NULL         -- JSON: what it said to weigh out, in totals
  )`,
  'CREATE INDEX IF NOT EXISTS dough_log_day ON dough_log (day, id)',
  'CREATE TABLE IF NOT EXISTS dough_login_failures (ip TEXT NOT NULL, at INTEGER NOT NULL)',
  'CREATE INDEX IF NOT EXISTS dough_login_failures_ip ON dough_login_failures (ip, at)',
];
let ready = null;

async function database(env) {
  if (!ready) {
    ready = env.DOUGH_DB.batch(SCHEMA.map((sql) => env.DOUGH_DB.prepare(sql))).catch((err) => {
      ready = null;
      throw err;
    });
  }
  await ready;
  return env.DOUGH_DB;
}

function entry(row) {
  return { ...row, batch: JSON.parse(row.batch), weights: JSON.parse(row.weights) };
}

// Newest day first; ?before=<day>.<id> continues after the last one shown
async function list(db, url) {
  const before = /^(\d{4}-\d{2}-\d{2})\.(\d+)$/.exec(url.searchParams.get('before') || '');
  const { results } = before
    ? await db.prepare('SELECT * FROM dough_log WHERE day < ?1 OR (day = ?1 AND id < ?2) ORDER BY day DESC, id DESC LIMIT ?3')
      .bind(before[1], Number(before[2]), PAGE + 1).all()
    : await db.prepare('SELECT * FROM dough_log ORDER BY day DESC, id DESC LIMIT ?1').bind(PAGE + 1).all();
  return json({ entries: results.slice(0, PAGE).map(entry), more: results.length > PAGE });
}

// What the calculator sends (dough.js, entry()). It checks every box against its
// range; this checks the shape and that the numbers are sane.
const BATCH_NUMBERS = ['balls', 'ball', 'waste', 'hydration', 'salt', 'yeast', 'oil', 'sugar', 'whole_wheat', 'rye',
  'pf_flour', 'pf_hydration', 'pf_yeast', 't_dough', 't_flour', 't_pf', 't_friction', 't_water'];
const WEIGHTS = ['dough', 'pizza', 'whole_wheat', 'rye', 'water', 'salt', 'yeast', 'oil', 'sugar', 'preferment',
  'water_c', 'ice'];

function isNum(x, lo, hi) { return typeof x === 'number' && Number.isFinite(x) && x >= lo && x <= hi; }

function validDay(day) {
  if (typeof day !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(day)) return false;
  const d = new Date(day + 'T00:00:00Z');
  return !Number.isNaN(d.getTime()) && d.toISOString().startsWith(day);
}

function check(body) {
  if (!body || typeof body !== 'object') return 'body';
  const { day, made_by: who, notes, kitchen_c: kc, humidity, dough_c: dc, batch, weights } = body;
  if (!validDay(day)) return 'day';
  if (typeof who !== 'string' || !who.trim() || who.length > 60) return 'made_by';
  if (typeof notes !== 'string' || notes.length > 1000) return 'notes';
  if (!isNum(kc, -10, 60)) return 'kitchen_c';
  if (!isNum(humidity, 0, 100)) return 'humidity';
  if (dc !== null && !isNum(dc, -10, 60)) return 'dough_c';
  if (!batch || typeof batch !== 'object' || Array.isArray(batch)) return 'batch';
  for (const [k, v] of Object.entries(batch)) {
    if (k === 'preferment') { if (!['none', 'poolish', 'biga'].includes(v)) return 'batch.preferment'; }
    else if (k === 'temp') { if (typeof v !== 'boolean') return 'batch.temp'; }
    else if (!BATCH_NUMBERS.includes(k) || !isNum(v, -100, 10000)) return 'batch.' + k;
  }
  if (!Number.isInteger(batch.balls) || batch.balls < 1 || !isNum(batch.ball, 1, 10000)) return 'batch.balls';
  if ((batch.whole_wheat || 0) + (batch.rye || 0) > 100) return 'batch.blend';
  if (!weights || typeof weights !== 'object' || Array.isArray(weights)) return 'weights';
  for (const [k, v] of Object.entries(weights)) {
    if (!WEIGHTS.includes(k) || !isNum(v, -1000, 1e7)) return 'weights.' + k;
  }
  if (!isNum(weights.dough, 0, 1e7)) return 'weights.dough';
  return null;
}

async function add(db, request) {
  if (!(request.headers.get('Content-Type') || '').startsWith('application/json')) return json({ error: 'json' }, 415);
  let body;
  try { body = await request.json(); } catch { return json({ error: 'json' }, 400); }
  const problem = check(body);
  if (problem) return json({ error: 'invalid', field: problem }, 400);
  const row = await db.prepare(
    `INSERT INTO dough_log (day, logged_at, made_by, balls, ball_g, dough_g, kitchen_c, humidity, dough_c, notes, batch, weights)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING *`,
  ).bind(body.day, new Date().toISOString(), body.made_by.trim(), body.batch.balls, body.batch.ball, body.weights.dough,
    body.kitchen_c, body.humidity, body.dough_c, body.notes.trim(), JSON.stringify(body.batch),
    JSON.stringify(body.weights)).first();
  return json({ entry: entry(row) }, 201);
}

// The whole log, oldest first, for a spreadsheet. A text cell that starts like a
// formula gets a ' in front, so the spreadsheet shows it rather than runs it.
async function csv(db) {
  const { results } = await db.prepare('SELECT * FROM dough_log ORDER BY day, id').all();
  const cols = [
    ['day', (e) => e.day], ['logged_at', (e) => e.logged_at], ['made_by', (e) => e.made_by],
    ['balls', (e) => e.balls], ['ball_g', (e) => e.ball_g], ['dough_g', (e) => e.dough_g],
    ['pizza_flour_pct', (e) => 100 - (e.batch.whole_wheat || 0) - (e.batch.rye || 0)],
    ['whole_wheat_pct', (e) => e.batch.whole_wheat], ['rye_pct', (e) => e.batch.rye],
    ['hydration_pct', (e) => e.batch.hydration], ['salt_pct', (e) => e.batch.salt],
    ['fresh_yeast_pct', (e) => e.batch.yeast], ['oil_pct', (e) => e.batch.oil], ['sugar_pct', (e) => e.batch.sugar],
    ['preferment', (e) => e.batch.preferment], ['pf_flour_pct', (e) => e.batch.pf_flour],
    ['pf_hydration_pct', (e) => e.batch.pf_hydration], ['pf_yeast_pct', (e) => e.batch.pf_yeast],
    ['kitchen_c', (e) => e.kitchen_c], ['humidity_pct', (e) => e.humidity],
    ['dough_target_c', (e) => e.batch.t_dough], ['dough_c', (e) => e.dough_c],
    ['water_c', (e) => e.weights.water_c], ['ice_g', (e) => e.weights.ice],
    ['pizza_flour_g', (e) => e.weights.pizza], ['whole_wheat_g', (e) => e.weights.whole_wheat],
    ['rye_g', (e) => e.weights.rye], ['water_g', (e) => e.weights.water], ['salt_g', (e) => e.weights.salt],
    ['fresh_yeast_g', (e) => e.weights.yeast], ['oil_g', (e) => e.weights.oil], ['sugar_g', (e) => e.weights.sugar],
    ['preferment_g', (e) => e.weights.preferment], ['notes', (e) => e.notes],
  ];
  const cell = (v) => {
    if (v === null || v === undefined) return '';
    if (typeof v === 'number') return String(v);
    const s = /^[=+\-@\t\r]/.test(v) ? "'" + v : v;
    return '"' + s.replace(/"/g, '""') + '"';
  };
  const lines = [cols.map(([name]) => name).join(',')]
    .concat(results.map(entry).map((e) => cols.map(([, get]) => cell(get(e))).join(',')));
  const today = new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10);   // Hanoi
  return new Response('﻿' + lines.join('\r\n') + '\r\n', {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': `attachment; filename="sol-dough-log-${today}.csv"`,
      ...SECURITY, ...PRIVATE,
    },
  });
}
