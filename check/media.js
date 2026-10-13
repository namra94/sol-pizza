// Every photograph in build/media.json, online: its original in the sol-media bucket
// (media.sol.pizza) answers, and every resized copy the pages ask Cloudflare for
// (sol.pizza/cdn-cgi/image/…, read from the build in ../dist) comes back as an image.
// And the home page's first photo, as the biggest phone gets it, weighs under about
// 200 KB (the budget: it's what a phone waits for first). Run it after uploading photos
// and merging their entries, with the public build in ../dist (npm run check runs it
// with a URL, after building). Nothing to check while media.json has no photos.
//   node media.js
const fs = require('fs'), path = require('path');

const MEDIA = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'build', 'media.json'), 'utf8'));
const DIST = path.resolve(__dirname, '..', 'dist');
const BASE = 'https://media.sol.pizza/';
const HERO_BUDGET = 200 * 1024;
// What Chrome on Android asks for (Safari on an iPhone takes AVIF too)
const PHONE_ACCEPT = 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8';
const TIMEOUT = 30000;

function htmlFiles(dir) {
  return fs.readdirSync(dir, {withFileTypes: true}).flatMap(d => d.isDirectory() ? htmlFiles(path.join(dir, d.name))
    : d.name.endsWith('.html') ? [path.join(dir, d.name)] : []);
}

// An address's answer: its status, type and (for GET) its weight
async function fetchOne(url, method) {
  try {
    const r = await fetch(url, {method, headers: {accept: PHONE_ACCEPT}, signal: AbortSignal.timeout(TIMEOUT)});
    const bytes = method === 'GET' ? (await r.arrayBuffer()).byteLength : 0;
    const type = r.headers.get('content-type') || '';
    return {bytes, type, problem: r.ok && type.startsWith('image/') ? null : r.status + ' ' + type};
  } catch (e) {
    return {problem: e.name === 'TimeoutError' ? 'no answer in ' + TIMEOUT / 1000 + ' s' : e.message};
  }
}

// Six at a time
async function each(items, fn) {
  const out = [];
  for (let i = 0; i < items.length; i += 6) out.push(...await Promise.all(items.slice(i, i + 6).map(fn)));
  return out;
}

(async () => {
  const photos = MEDIA.photos || [];
  if (!photos.length) {
    console.log('photos: none in build/media.json yet, nothing to check');
    return;
  }
  if (!fs.existsSync(path.join(DIST, 'index.html'))) {
    console.log('FAIL  no ../dist/index.html: build first (python3 build/gen.py)');
    process.exit(1);
  }
  let failed = 0;
  // The originals: HEAD, so nothing is downloaded
  for (const [p, r] of (await each(photos, async p => [p, await fetchOne(BASE + p.key, 'HEAD')]))) {
    if (r.problem) { failed++; console.log('FAIL  %s, the original: %s', p.key, r.problem); }
  }
  // Every resized copy the pages ask for: the same addresses visitors' browsers will
  const urls = new Set();
  for (const f of htmlFiles(DIST)) {
    for (const m of fs.readFileSync(f, 'utf8').matchAll(/https:\/\/sol\.pizza\/cdn-cgi\/image\/[^\s"<>]+/g)) {
      urls.add(m[0].replace(/&amp;/g, '&'));
    }
  }
  const results = await each([...urls], async u => [u, await fetchOne(u, 'GET')]);
  for (const [u, r] of results) {
    if (r.problem) { failed++; console.log('FAIL  %s: %s', u, r.problem); }
  }
  const unused = photos.filter(p => ![...urls].some(u => u.endsWith('/' + BASE + p.key)));
  if (unused.length) console.log('note  on no page (no slot, or its page is off): %s', unused.map(p => p.key).join(', '));
  // The home page's first photo, as a phone gets it: the largest in its phone srcset
  const home = fs.readFileSync(path.join(DIST, 'index.html'), 'utf8');
  const m = home.match(/<figure class="band band-hero"><picture><source media="\(max-width: 760\.98px\)" srcset="([^"]+)"/);
  if (m) {
    const [url, width] = m[1].split(', ').pop().trim().split(' ');
    const r = results.find(([u]) => u === url.replace(/&amp;/g, '&'))[1];
    const line = 'the home page\'s first photo as a phone gets it (' + width + '): ';
    if (r.problem) { /* counted above */ }
    else if (r.bytes > HERO_BUDGET) {
      failed++;
      console.log('FAIL  ' + line + Math.round(r.bytes / 1024) + ' KB ' + r.type + ', over the ~200 KB budget: choose a '
                  + 'calmer photo (less fine detail or grain), or export it with less sharpening');
    } else console.log('ok    ' + line + Math.round(r.bytes / 1024) + ' KB ' + r.type);
  }
  console.log(failed ? failed + ' photo problem(s)' : 'photos: all ' + photos.length + ' originals and the ' + urls.size
              + ' resized copies the pages use load');
  process.exit(failed ? 1 : 0);
})();
