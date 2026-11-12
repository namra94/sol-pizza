// The back office's purchase request as the Worker writes it for Google Chat and posts
// it: worker/backoffice.js itself, run here with no browser, database or network.
//   node backoffice.js
// 1. The message. Other tools read Supply by its labels, so for a Kitchen, a Bar and a
//    FOH request it must be exactly these lines in this order: the approver mentioned
//    by Google user id (<users/ID>), or named as text when there's no id, and no 🛒.
// 2. What a person types. Google Chat reads <users/all> as a mention and
//    <address|words> as a link, makes a link of a web address it finds, and has no way
//    to write < or > as plain text. So whatever goes in the five places a person types
//    (the name, an item, its unit, its note, the request's note), the message's only <
//    and > are the approver's mention, no line is added, and no address is left whole:
//    no ://, and no www. or dot with a name straight after it. Tried with every way
//    Google documents, in each place, then with 4,000 requests made of their pieces
//    at random (the same ones every run).
// 3. Posting. To CHAT_WEBHOOK_URL and nowhere else (never the old SLACK_WEBHOOK_URL),
//    as {"text": …} and nothing more. When it fails, what staff are told is the
//    Worker's own words, the HTTP status and Google's status word: never the webhook's
//    address or a part of it, even when the answer or the error quotes it.
const fs = require('fs'), path = require('path');
const {randomUUID} = require('crypto');

const ROOT = path.resolve(__dirname, '..');
let failures = 0;
function ok(cond, what) {
  console.log((cond ? '  ok   ' : '  FAIL ') + what);
  if (!cond) failures++;
}

// D1, as far as one new request needs it: nothing kept before, every write taken
const db = {prepare: () => ({bind: () => ({
  all: async () => ({results: []}), first: async () => null, run: async () => ({meta: {changes: 1}}),
})})};
const KITCHEN_ID = '100000000000000000001', BAR_FOH_ID = '100000000000000000002';    // made up
const IDS = {CHAT_APPROVER_KITCHEN: KITCHEN_ID, CHAT_APPROVER_BAR_FOH: BAR_FOH_ID};
const DAY = '2099-12-31';                   // a Thursday, and never in the past
const ORDERING = 'Đặt hàng / Ordering: quản lý chọn NCC và thương hiệu / management picks the supplier and brand';
const SENT_FROM = '_Gửi từ sol.pizza/backoffice · Ref REQ-…_';
// Characters the file tools would write raw, and nobody would see
const LINE_SEP = String.fromCharCode(0x2028), ZERO_WIDTH = String.fromCharCode(0x200b);

async function main() {
  // The Worker's file is a module and this folder's scripts aren't, so it's loaded
  // from its text. It imports nothing.
  const source = fs.readFileSync(path.join(ROOT, 'worker', 'backoffice.js'), 'utf8');
  const worker = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));

  // The message for a request, as the form's Preview asks for it, its ref as REQ-…
  async function message(body, env) {
    const [status, out] = await worker.purchase(env || IDS, db, {...body, preview: true});
    if (status !== 200) return {status, field: out.field};
    return {status, ref: out.ref, text: out.message.split(out.ref).join('REQ-…')};
  }
  // Where two texts first part, to show under a FAIL
  function apart(got, want) {
    const g = String(got).split('\n'), w = want.split('\n');
    const i = w.findIndex((line, n) => line !== g[n]);
    const at = i < 0 ? w.length : i;
    return '\n         line ' + (at + 1) + '\n         got:    ' + JSON.stringify(g[at]) + '\n         wanted: ' + JSON.stringify(w[at]);
  }

  console.log('The message');
  {
    const kitchen = {
      requested_by: 'Nguyễn Văn A', station: 'Kitchen', needed_by: DAY, needed_time: '10:00', note: 'Giao trước 10h sáng',
      items: [
        {item: 'Fior di latte', qty: 10, unit: 'kg', note: 'for Saturday'},
        {item: 'Húng quế', qty: 4, unit: 'bunch', note: 'lá to'},
        {item: 'Giấy nướng', qty: 2, unit: 'cuộn 50m', note: ''},
        {item: 'Bột 00', qty: 1250.5, unit: 'sack'},
      ],
    };
    const bar = {
      requested_by: 'Trần Thị B', station: 'Bar', needed_by: DAY,
      items: [{item: 'Chanh vàng', qty: 2.5, unit: 'kg'}, {item: 'Soda', qty: 24, unit: 'can', note: 'không đường'}],
    };
    const foh = {
      requested_by: 'Lê Văn C', station: 'FOH', needed_by: DAY, needed_time: '09:30', note: '',
      items: [{item: 'Khăn giấy', qty: 12, unit: 'pack'}],
    };
    const wanted = {
      kitchen: [
        '📝 YÊU CẦU MUA HÀNG / PURCHASE REQUEST',
        'Bộ phận / Station: Bếp / Kitchen',
        'Cần lúc / Needed by: Thu 31 Dec 2099, 10:00',
        'Hàng / Items:',
        '• Fior di latte — 10 kg (for Saturday)',
        '• Húng quế — 4 bó/bunch (lá to)',
        '• Giấy nướng — 2 cuộn 50m',
        '• Bột 00 — 1,250.5 bao/sack',
        'Người yêu cầu / Requested by: Nguyễn Văn A',
        'Ghi chú / Note: Giao trước 10h sáng',
        'Duyệt / Approve: <users/' + KITCHEN_ID + '> ✅ / ❌',
        ORDERING,
        SENT_FROM,
      ].join('\n'),
      bar: [
        '📝 YÊU CẦU MUA HÀNG / PURCHASE REQUEST',
        'Bộ phận / Station: Bar',
        'Cần lúc / Needed by: Thu 31 Dec 2099',
        'Hàng / Items:',
        '• Chanh vàng — 2.5 kg',
        '• Soda — 24 lon/can (không đường)',
        'Người yêu cầu / Requested by: Trần Thị B',
        'Duyệt / Approve: <users/' + BAR_FOH_ID + '> ✅ / ❌',
        ORDERING,
        SENT_FROM,
      ].join('\n'),
      foh: [
        '📝 YÊU CẦU MUA HÀNG / PURCHASE REQUEST',
        'Bộ phận / Station: FOH',
        'Cần lúc / Needed by: Thu 31 Dec 2099, 09:30',
        'Hàng / Items:',
        '• Khăn giấy — 12 gói/pack',
        'Người yêu cầu / Requested by: Lê Văn C',
        'Duyệt / Approve: <users/' + BAR_FOH_ID + '> ✅ / ❌',
        ORDERING,
        SENT_FROM,
      ].join('\n'),
    };
    const k = await message(kitchen), b = await message(bar), f = await message(foh);
    ok(k.text === wanted.kitchen, 'a Kitchen request: the 📝 block, line for line, mentioning the Kitchen approver' +
       (k.text === wanted.kitchen ? '' : apart(k.text, wanted.kitchen)));
    ok(b.text === wanted.bar, 'a Bar request: the same lines, mentioning the Bar & FOH approver' +
       (b.text === wanted.bar ? '' : apart(b.text, wanted.bar)));
    ok(f.text === wanted.foh, 'a FOH request: the same, and the same approver' + (f.text === wanted.foh ? '' : apart(f.text, wanted.foh)));
    ok([k, b, f].every(m => /^REQ-\d{6}-\d{4}$/.test(m.ref)), 'the ref is REQ-YYMMDD-HHMM (' + k.ref + ')');

    // No id, or something that isn't one: the role as text, and no one mentioned
    const role = {Kitchen: 'Kitchen approver', Bar: 'Bar & FOH approver'};
    const notIds = [undefined, '', 'all', 'users/all', 'U0BTWU0P2TH', '<users/1>', '12 34', '1'.repeat(33), 123456789];
    const named = [];
    for (const id of notIds) {
      for (const body of [kitchen, bar]) {
        const m = await message(body, {CHAT_APPROVER_KITCHEN: id, CHAT_APPROVER_BAR_FOH: id});
        const line = 'Duyệt / Approve: ' + role[body.station] + ' ✅ / ❌';
        if (m.status !== 200 || !m.text.split('\n').includes(line) || /[<>]/.test(m.text)) named.push(JSON.stringify(id));
      }
    }
    ok(!named.length, 'without a Google user id (unset, "all", an old Slack id, a number…) the role is named as text and ' +
       'no one is mentioned' + (named.length ? ' (' + named.join(' ') + ')' : ''));

    const conf = fs.readFileSync(path.join(ROOT, 'wrangler.jsonc'), 'utf8');
    const set = ['CHAT_APPROVER_KITCHEN', 'CHAT_APPROVER_BAR_FOH'].map(v => (new RegExp('"' + v + '":\\s*"(\\d{1,32})"').exec(conf) || [])[1]);
    ok(set[0] && set[1] && !/SLACK_/.test(conf), 'wrangler.jsonc: both approvers are Google user ids, digits in quotes, and ' +
       'no Slack setting is left');
  }

  console.log('What a person types');
  {
    // The five places a person types in, each with something harmless in the others
    const PLACES = {
      'the name': (b, s) => { b.requested_by = s; },
      'an item': (b, s) => { b.items[0].item = s; },
      'a unit': (b, s) => { b.items[0].unit = s; },
      'an item’s note': (b, s) => { b.items[0].note = s; },
      'the note': (b, s) => { b.note = s; },
    };
    const request = station => ({requested_by: 'A', station, needed_by: DAY, note: '', items: [{item: 'B', qty: 1, unit: 'C', note: ''}]});

    // What a person's text has made of a message that it shouldn't: '' for nothing
    function harm(text, body, env) {
      const lines = text.split('\n'), n = body.items.length;
      const id = body.station === 'Kitchen' ? env.CHAT_APPROVER_KITCHEN : env.CHAT_APPROVER_BAR_FOH;
      const noted = lines.length === n + 9;                 // with the request's note
      if (lines.length !== n + 8 && !noted) return 'a line too many or too few';
      const starts = ['📝 YÊU CẦU MUA HÀNG / PURCHASE REQUEST', 'Bộ phận / Station: ', 'Cần lúc / Needed by: ', 'Hàng / Items:']
        .concat(body.items.map(() => '• '), 'Người yêu cầu / Requested by: ', noted ? ['Ghi chú / Note: '] : [],
                'Duyệt / Approve: <users/' + id + '> ✅ / ❌', ORDERING, SENT_FROM);
      const off = starts.findIndex((s, i) => !lines[i].startsWith(s));
      if (off >= 0) return 'line ' + (off + 1) + ' isn’t its label’s';
      const approve = lines.length - 3, typed = lines.filter((_, i) => i !== approve && i !== lines.length - 1);
      if (lines[approve] !== starts[approve] || lines[approve + 1] !== ORDERING || lines[approve + 2] !== SENT_FROM) return 'a fixed line changed';
      if (typed.some(l => /[<>]/.test(l))) return 'a < or > that isn’t the approver’s mention';
      if (text.includes('://')) return 'an address with ://';
      if (typed.some(l => /www\.[\p{L}\p{N}]/iu.test(l))) return 'www. with a name straight after it';
      if (typed.some(l => /\.\p{L}[\p{L}\p{M}]/u.test(l))) return 'a dot with a name straight after it';
      if (text.includes('🛒')) return 'a 🛒';
      return '';
    }

    // Every way Google documents to write a mention or a link, and a few it doesn't.
    // 20 characters at most, so each fits a unit too.
    const TRIES = [
      '<users/all>', '<users/' + KITCHEN_ID.slice(0, 12) + '>', '<<users/all>>', '<users/all', 'users/all>', '< users/all >',
      '<https://x.io|menu>', '<https://x.io>', '<x.io|menu>', '<customEmojis/x>', '<@U123> <!channel>',
      'https://x.io/a?b=c', 'HTTPS://X.IO', 'ftp://x.io', 'zalo://x', 'http://10.0.0.1/a', 'www.x.io', 'WWW.7-eleven.vn',
      'x.io', 'sol.pizza/menu', 'a@x.io', 'mailto:a@x.io', '> quoted',
      '<users/\nall>', '<users/all' + LINE_SEP + '>', '<' + ZERO_WIDTH + 'users/all>', '&lt;users/all&gt;', '🛒 <users/all>',
    ];
    const shown = [];
    let bad = [];
    for (const text of TRIES) {
      for (const [place, put] of Object.entries(PLACES)) {
        for (const station of ['Kitchen', 'Bar']) {
          const body = request(station);
          put(body, text);
          const m = await message(body);
          const wrong = m.status !== 200 ? 'refused (' + m.field + ')' : harm(m.text, body, IDS);
          if (wrong) bad.push(JSON.stringify(text) + ' as ' + place + ': ' + wrong);
          else if (place === 'the note' && station === 'Kitchen') shown.push([text, m.text.split('\n')[6].slice('Ghi chú / Note: '.length)]);
        }
      }
    }
    ok(!bad.length, TRIES.length + ' ways to write a mention or a link, each as the name, an item, a unit, an item’s note and the ' +
       'note: none makes one, or a line' + (bad.length ? '\n         ' + bad.slice(0, 8).join('\n         ') : ''));
    // (the two characters nobody would see, written out)
    const unseen = new RegExp('[' + LINE_SEP + ZERO_WIDTH + ']', 'g');
    const quoted = s => JSON.stringify(s).replace(unseen, c => '\\u' + c.charCodeAt(0).toString(16));
    for (const [typed, sent] of shown) console.log('         ' + quoted(typed) + ' goes as ' + quoted(sent));

    // The same pieces thrown together, in all five places at once
    let seed = 20261113;
    const random = () => {                  // mulberry32: the same requests every run
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    const PIECES = ['<', '<', '>', '>', '|', '/', '//', ':', '.', '.', '@', '&', ';', '#', '*', '_', '~', '`', ' ', ' ', '\n', '\t',
      LINE_SEP, ZERO_WIDTH, 'users/', 'users/all', 'all', KITCHEN_ID, '123', 'customEmojis/', 'http', 'https', 'ftp', 'mailto',
      'www', 'WWW', 'x', 'io', 'com', 'vn', 'sol', 'pizza', 'ế', 'Ü', '7', '&lt;', '&gt;', '%3C', '🛒', ':shopping_trolley:', '•', '✅'];
    const some = most => {
      let s = 'a';
      while (s.length < most && random() < 0.94) s += PIECES[Math.floor(random() * PIECES.length)];
      return s.slice(0, most);
    };
    const RUNS = 4000;
    let made = 0;
    bad = [];
    for (let i = 0; i < RUNS && !bad.length; i++) {
      const body = {
        requested_by: some(60), station: ['Kitchen', 'Bar', 'FOH'][Math.floor(random() * 3)], needed_by: DAY, note: random() < 0.8 ? some(1000) : '',
        items: Array.from({length: 1 + Math.floor(random() * 3)}, () => ({item: some(80), qty: 1, unit: some(20), note: random() < 0.7 ? some(200) : ''})),
      };
      const m = await message(body);
      if (m.status !== 200) continue;       // refused: nothing would be posted at all
      made++;
      const wrong = harm(m.text, body, IDS);
      if (wrong) bad.push(wrong + ', from ' + JSON.stringify(body));
    }
    ok(!bad.length && made > RUNS * 0.9, made.toLocaleString('en') + ' requests made of those pieces at random: none makes a mention, ' +
       'a link or a line' + (bad.length ? '\n         ' + bad[0] : ''));

    // And what isn't an address goes as it was typed
    const note = async text => {
      const body = request('Kitchen');
      body.note = text;
      return (await message(body)).text.split('\n')[6].slice('Ghi chú / Note: '.length);
    };
    const KEPT = ['San Marzano D.O.P.', 'Parmigiano 24 tháng, I.G.P.', '2.5 kg, loại 1', 'giao trước 10:30', 'tỉ lệ 1:1', 'A&B',
      'túi 5kg (x2) v.v.', '1.250.000đ', 'size L/XL, 30cm x 50m', '*gấp* _hôm nay_', 'No.1'];
    const changed = [];
    for (const text of KEPT) if (await note(text) !== text) changed.push(JSON.stringify(text) + ' went as ' + JSON.stringify(await note(text)));
    ok(!changed.length, 'ordinary notes go as typed: D.O.P., 2.5 kg, 10:30, 1:1, A&B, 1.250.000đ…' +
       (changed.length ? '\n         ' + changed.join('\n         ') : ''));
    const opened = {'size > 30cm, < 5kg': 'size › 30cm, ‹ 5kg', 'S.Pellegrino 750ml': 'S. Pellegrino 750ml', 'TP.HCM': 'TP. HCM'};
    const not = [];
    for (const [typed, sent] of Object.entries(opened)) if (await note(typed) !== sent) not.push(JSON.stringify(typed) + ' went as ' + JSON.stringify(await note(typed)));
    ok(!not.length, 'and what only looks like markup or an address stays readable: size › 30cm, S. Pellegrino, TP. HCM' +
       (not.length ? '\n         ' + not.join('\n         ') : ''));
  }

  console.log('Posting');
  {
    // Not a real webhook: the shape of one, to see that no part of it ever gets out
    const ADDRESS = 'https://chat.googleapis.com/v1/spaces/AAAA-check-space/messages?key=check-key-0123456789&token=check-token-abcdefghij%3D';
    const PARTS = [ADDRESS, 'chat.googleapis.com', '/v1/spaces', 'AAAA-check-space', 'check-key-0123456789', 'check-token-abcdefghij'];
    const body = () => ({
      request_id: randomUUID(), requested_by: 'A', station: 'Kitchen', needed_by: DAY, note: 'TEST — ignore',
      items: [{item: 'B', qty: 1, unit: 'kg'}],
    });
    const real = globalThis.fetch;
    let calls = [];
    const answers = respond => { globalThis.fetch = async (url, init) => { calls.push({url, init}); return respond(); }; };
    const send = async env => { calls = []; return worker.purchase(env, db, body()); };
    const json = (status, data) => () => new Response(JSON.stringify(data), {status, headers: {'Content-Type': 'application/json; charset=UTF-8'}});
    try {
      answers(json(200, {name: 'spaces/AAAA-check-space/messages/1', thread: {name: 'spaces/AAAA-check-space/threads/1'}}));
      let [status, out] = await send({...IDS, CHAT_WEBHOOK_URL: ADDRESS});
      const sent = calls[0] || {init: {}};
      let posted = null;
      try { posted = JSON.parse(sent.init.body); } catch (e) { /* not JSON */ }
      ok(status === 200 && out.ok === true && !out.dry_run && calls.length === 1 && sent.url === ADDRESS && sent.init.method === 'POST',
         'a request is posted once, to CHAT_WEBHOOK_URL');
      ok((sent.init.headers || {})['Content-Type'] === 'application/json; charset=UTF-8' && posted &&
         Object.keys(posted).join() === 'text' && posted.text === out.message,
         'as JSON, {"text": the message} and nothing else (no unfurl_links or unfurl_media)');

      [status, out] = await send({...IDS, SLACK_WEBHOOK_URL: 'https://hooks.slack.com/services/check/not/real'});
      ok(status === 502 && out.error === 'chat' && out.detail === 'CHAT_WEBHOOK_URL is not set' && calls.length === 0,
         'with only the old SLACK_WEBHOOK_URL set, nothing is posted anywhere, and the page says CHAT_WEBHOOK_URL is not set');
      [status, out] = await send({...IDS, CHAT_WEBHOOK_URL: 'spaces/AAAA-check-space, pasted by mistake'});
      ok(status === 502 && out.detail === 'CHAT_WEBHOOK_URL is not a web address' && calls.length === 0,
         'with something else pasted as CHAT_WEBHOOK_URL, nothing is posted, and the page says it is not a web address');
      [status, out] = await send({...IDS, CHAT_WEBHOOK_URL: '  ' + ADDRESS + '\n'});
      ok(status === 200 && calls.length === 1 && calls[0].url === ADDRESS, 'a space or a line break pasted around the address is left off');
      [status, out] = await send({...IDS, CHAT_WEBHOOK_URL: ADDRESS, BACKOFFICE_DRY_RUN: '1'});
      ok(status === 200 && out.dry_run === true && calls.length === 0, 'a dry run posts nothing');

      // Google Chat's ways of saying no, each quoting the address where it can
      const quote = 'No webhook at ' + ADDRESS + ' (spaces/AAAA-check-space, key check-key-0123456789, token check-token-abcdefghij=)';
      const refusals = [
        [json(400, {error: {code: 400, message: 'Invalid JSON payload received. Unknown name "unfurl_links"', status: 'INVALID_ARGUMENT'}}),
         'Google Chat answered 400: INVALID_ARGUMENT'],
        [json(404, {error: {code: 404, message: quote, status: 'NOT_FOUND'}}), 'Google Chat answered 404: NOT_FOUND'],
        [json(429, {error: {code: 429, message: 'Resource has been exhausted (e.g. check quota).', status: 'RESOURCE_EXHAUSTED'}}),
         'Google Chat answered 429: RESOURCE_EXHAUSTED'],
        [json(403, {error: {code: 403, message: quote, status: quote}}), 'Google Chat answered 403'],
        [json(400, {error: quote}), 'Google Chat answered 400'],
        [() => new Response('<!DOCTYPE html><p>The requested URL <code>' + ADDRESS + '</code> was not found.', {status: 404}),
         'Google Chat answered 404'],
        [() => new Response('', {status: 503}), 'Google Chat answered 503'],
        [() => { throw new TypeError('fetch failed: ' + ADDRESS); }, 'Google Chat could not be reached: the connection failed'],
        [() => { throw new DOMException('The operation timed out: ' + ADDRESS, 'TimeoutError'); },
         'Google Chat could not be reached: no answer in 10 seconds'],
      ];
      const told = [], leaks = [];
      for (const [respond, wanted] of refusals) {
        answers(respond);
        [status, out] = await send({...IDS, CHAT_WEBHOOK_URL: ADDRESS});
        const all = JSON.stringify(out);
        if (status !== 502 || out.error !== 'chat' || out.detail !== wanted) told.push(JSON.stringify(out.detail) + ', not ' + JSON.stringify(wanted));
        if (PARTS.some(p => all.includes(p))) leaks.push(all);
      }
      ok(!told.length, 'when Google Chat says no or can’t be reached, staff are told the HTTP status and Google’s status word, ' +
         'or that there was no answer' + (told.length ? '\n         ' + told.join('\n         ') : ''));
      ok(!leaks.length, 'and never the webhook’s address or a part of it, in ' + refusals.length + ' answers and errors that quote it' +
         (leaks.length ? '\n         ' + leaks.join('\n         ') : ''));
    } finally {
      globalThis.fetch = real;
    }
  }

  console.log(failures ? '\n' + failures + ' failed' : '\nall good');
  process.exit(failures ? 1 : 0);
}

main().catch(err => { console.error(err); process.exit(1); });
