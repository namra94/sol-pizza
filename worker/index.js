/* sol.pizza — the Worker in front of the static site.
   Everything else is the files in dist/ (build/gen.py), served by Cloudflare as
   they are. wrangler.jsonc runs this first only for the kitchen (/dough/*), the
   back office (/backoffice/*) and /api/*, and it
     - keeps /dough/ (the dough calculator, the dough log) behind the kitchen
       password, the secret DOUGH_PASSWORD (README-DEPLOY.md, "The kitchen");
     - keeps the dough log in D1 (the DOUGH_DB binding) and serves it as JSON for
       the pages and as a CSV to download;
     - keeps /backoffice/ behind the staff password, the secret BACKOFFICE_PASSWORD,
       and sends its purchase requests to Slack (worker/backoffice.js;
       README-DEPLOY.md, "The back office: purchase requests").
   The kitchen and the back office are the two sections below (KITCHEN, OFFICE),
   each with its own password, cookie, pages and API, so one password never opens
   the other. Signed in = the section's cookie (sol_dough, sol_office): an expiry
   and an HMAC of it keyed with that password, so changing a password signs every
   phone out of its section. With no password set (a Preview, unless it's given
   one), a section stays locked and says so; with no database the calculator works
   but the log says it isn't set up, and the back office says the same.
   Anything else that reaches the Worker (an address with no file) goes back to
   the static site, which shows the 404 page. */

import * as backoffice from './backoffice.js';

const SESSION_DAYS = 30;
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

// The two places behind a password. The HMAC keys start with the section's key, so
// the kitchen's are what they have always been and every phone stays signed in.
const KITCHEN = {
  password: 'DOUGH_PASSWORD', cookie: 'sol_dough', key: 'sol-dough', failures: 'dough_login_failures',
  home: '/dough/', login: '/dough/login/', api: '/api/dough/',
  next: /^\/dough\/[\w\-./?=&%]*$/,     // where signing in may lead
  redirects: {},                         // its redirects' headers, as they have always been
};
const OFFICE = {
  password: 'BACKOFFICE_PASSWORD', cookie: 'sol_office', key: 'sol-office', failures: 'backoffice_login_failures',
  home: '/backoffice/', login: '/backoffice/login/', api: '/api/backoffice/',
  next: /^\/backoffice\/[\w\-./?=&%]*$/,
  redirects: SECURITY,                   // the security headers go on its redirects too
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    try {
      if (path.startsWith('/api/')) return await api(request, env, url);
      if (path === '/dough' || path.startsWith('/dough/')) return await pages(KITCHEN, request, env, url);
      if (path === '/backoffice' || path.startsWith('/backoffice/')) return await pages(OFFICE, request, env, url);
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
async function rightPassword(s, given, env) {
  const key = s.key + '-password';
  return same(await hmac(key, given), await hmac(key, env[s.password]));
}

async function session(s, env, exp) {
  return exp + '.' + (await hmac(s.key + '-session\n' + env[s.password], String(exp)));
}

function cookie(s, value, maxAge) {
  return `${s.cookie}=${value}; Path=/; Max-Age=${maxAge}; HttpOnly; Secure; SameSite=Lax`;
}

async function signedIn(s, request, env) {
  if (!env[s.password]) return false;
  const m = new RegExp(`(?:^|;\\s*)${s.cookie}=(\\d+)\\.([0-9a-f]{64})(?:;|$)`).exec(request.headers.get('Cookie') || '');
  if (!m || Number(m[1]) < Date.now() / 1000) return false;
  return same(await session(s, env, m[1]), `${m[1]}.${m[2]}`);
}

// Where to go after signing in: a page of the same section, never somewhere else
function safeNext(s, next) {
  return typeof next === 'string' && s.next.test(next) && !next.includes('..') &&
    !next.startsWith(s.login) ? next : s.home;
}

function loginUrl(s, next, flag) {
  const q = [];
  if (flag) q.push(flag + '=1');
  if (next !== s.home) q.push('next=' + encodeURIComponent(next));
  return s.login + (q.length ? '?' + q.join('&') : '');
}

/* The sections' pages -------------------------------------------------------- */
async function pages(s, request, env, url) {
  const path = url.pathname;
  const next = safeNext(s, url.searchParams.get('next'));
  if ([s.login.slice(0, -1), s.login, s.login + 'index.html'].includes(path)) {
    if (await signedIn(s, request, env)) return redirect(next, s.redirects);
    const flag = !env[s.password] ? 'off' : ['wrong', 'wait'].find((f) => url.searchParams.has(f));
    let rewriter = new HTMLRewriter().on('input[name="next"]', {
      element(el) { el.setAttribute('value', next); },
    });
    if (flag) {
      rewriter = rewriter.on(`[data-if="${flag}"]`, { element(el) { el.removeAttribute('hidden'); } });
    }
    return withHeaders(rewriter.transform(await env.ASSETS.fetch(request)), { ...SECURITY, ...PRIVATE });
  }
  if (!(await signedIn(s, request, env))) return redirect(loginUrl(s, safeNext(s, path + url.search)), s.redirects);
  return withHeaders(await env.ASSETS.fetch(request), { ...SECURITY, ...PRIVATE });
}

/* The API -------------------------------------------------------------------- */
async function api(request, env, url) {
  const path = url.pathname;
  const method = request.method;
  const s = [KITCHEN, OFFICE].find((x) => path.startsWith(x.api));
  if (!s) return json({ error: 'not found' }, 404);
  if (path === s.api + 'login') return login(s, request, env);
  if (path === s.api + 'logout') return redirect(s.login, { ...s.redirects, 'Set-Cookie': cookie(s, '', 0) });
  if (!(await signedIn(s, request, env))) return json({ error: 'signed out' }, 401);
  // Changes come from the section's own pages only
  const origin = request.headers.get('Origin');
  if (method !== 'GET' && method !== 'HEAD' && origin && origin !== url.origin) return json({ error: 'forbidden' }, 403);
  if (!env.DOUGH_DB) return json({ error: 'no database' }, 503);
  const db = await database(env, tables(s));
  if (s === OFFICE) return office(request, env, url, db);

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

async function login(s, request, env) {
  if (request.method !== 'POST') return redirect(s.login, s.redirects);
  const form = await request.formData();
  const next = safeNext(s, form.get('next'));
  if (!env[s.password]) return redirect(loginUrl(s, next, 'off'), s.redirects);
  const db = env.DOUGH_DB ? await database(env, tables(s)) : null;
  const ip = request.headers.get('CF-Connecting-IP') || 'local';
  const now = Math.floor(Date.now() / 1000);
  if (db) {
    const row = await db.prepare(`SELECT COUNT(*) AS n FROM ${s.failures} WHERE ip = ? AND at > ?`)
      .bind(ip, now - TRIES_WINDOW).first();
    if (row.n >= MAX_TRIES) return redirect(loginUrl(s, next, 'wait'), s.redirects);
  }
  if (!(await rightPassword(s, String(form.get('password') || ''), env))) {
    if (db) {
      await db.batch([
        db.prepare(`INSERT INTO ${s.failures} (ip, at) VALUES (?, ?)`).bind(ip, now),
        db.prepare(`DELETE FROM ${s.failures} WHERE at < ?`).bind(now - 86400),
      ]);
    }
    return redirect(loginUrl(s, next, 'wrong'), s.redirects);
  }
  if (db) await db.prepare(`DELETE FROM ${s.failures} WHERE ip = ?`).bind(ip).run();
  const maxAge = SESSION_DAYS * 86400;
  return redirect(next, { ...s.redirects, 'Set-Cookie': cookie(s, await session(s, env, now + maxAge), maxAge) });
}

/* The back office's API ------------------------------------------------------ */
// What the forms ask for; the work is in worker/backoffice.js.
async function office(request, env, url, db) {
  const path = url.pathname;
  const method = request.method;
  if (path === '/api/backoffice/guide' && method === 'GET') return json(await backoffice.guide(env, db));
  if (path === '/api/backoffice/purchases' && method === 'GET') return json(await backoffice.purchases(db));
  if (path === '/api/backoffice/purchase' && method === 'POST') {
    if (!(request.headers.get('Content-Type') || '').startsWith('application/json')) return json({ error: 'json' }, 415);
    let body;
    try { body = await request.json(); } catch { return json({ error: 'json' }, 400); }
    const [status, out] = await backoffice.purchase(env, db, body);
    return json(out, status);
  }
  return json({ error: 'not found' }, 404);
}

/* The log in D1 -------------------------------------------------------------- */
// The tables are made on first use, so a new database (and `wrangler dev`'s local
// one) needs no setup. To change them later, add a migration (README-DEPLOY.md).
// The back office keeps its own tables in the same database (backoffice.SCHEMA).
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
const ready = new Map();                // each section's tables, once they're made

function tables(s) { return s === OFFICE ? backoffice.SCHEMA : SCHEMA; }

async function database(env, schema) {
  if (!ready.has(schema)) {
    ready.set(schema, env.DOUGH_DB.batch(schema.map((sql) => env.DOUGH_DB.prepare(sql))).catch((err) => {
      ready.delete(schema);
      throw err;
    }));
  }
  await ready.get(schema);
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
