// Every photograph in build/media.json, online: the original in the sol-media bucket
// (media.sol.pizza), and Cloudflare's resized copy on sol.pizza, both answer with an
// image. And the home page's first photo, as the biggest phone gets it, weighs under
// about 200 KB (the budget: it's what a phone waits for first). Run it after uploading
// photos and merging their entries, with the public build in ../dist (npm run check
// runs it with a URL, after building). Nothing to check while media.json has no photos.
//   node media.js
const fs = require('fs'), path = require('path');

const MEDIA = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'build', 'media.json'), 'utf8'));
const BASE = 'https://media.sol.pizza/';
const CDN = 'https://sol.pizza/cdn-cgi/image/';
const HERO_BUDGET = 200 * 1024;
// What Chrome on Android asks for (Safari on an iPhone takes AVIF too)
const PHONE_ACCEPT = 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8';

// The home page's first photo as a phone gets it: the largest in its phone srcset
function heroForPhones() {
  const file = path.resolve(__dirname, '..', 'dist', 'index.html');
  if (!fs.existsSync(file)) return {problem: 'no ../dist/index.html: build first (python3 build/gen.py)'};
  const html = fs.readFileSync(file, 'utf8');
  const m = html.match(/<figure class="band band-hero"><picture><source media="\(max-width: 760\.98px\)" srcset="([^"]+)"/);
  if (!m) return {};
  const last = m[1].split(', ').pop().trim().split(' ');
  return {url: last[0].replace(/&amp;/g, '&'), width: last[1]};
}

async function check(url) {
  try {
    const r = await fetch(url, {redirect: 'follow'});
    const type = r.headers.get('content-type') || '';
    return r.ok && type.startsWith('image/') ? null : r.status + ' ' + type;
  } catch (e) {
    return e.message;
  }
}

(async () => {
  const photos = MEDIA.photos || [];
  if (!photos.length) {
    console.log('photos: none in build/media.json yet, nothing to check');
    return;
  }
  let failed = 0;
  for (const p of photos) {
    const original = BASE + p.key;
    const resized = CDN + 'width=480,quality=75,format=auto/' + original;
    for (const [what, url] of [['original', original], ['resized', resized]]) {
      const problem = await check(url);
      if (problem) { failed++; console.log('FAIL  %s %s: %s', p.key, what, problem); }
    }
  }
  const hero = heroForPhones();
  if (hero.problem) { failed++; console.log('FAIL  the home page\'s first photo: %s', hero.problem); }
  if (hero.url) {
    try {
      const r = await fetch(hero.url, {headers: {accept: PHONE_ACCEPT}});
      const bytes = (await r.arrayBuffer()).byteLength, kb = Math.round(bytes / 1024);
      const type = r.headers.get('content-type') || '';
      const line = 'the home page\'s first photo as a phone gets it (' + hero.width + ', ' + hero.url + '): ';
      if (!r.ok || !type.startsWith('image/')) { failed++; console.log('FAIL  ' + line + r.status + ' ' + type); }
      else if (bytes > HERO_BUDGET) {
        failed++;
        console.log('FAIL  ' + line + kb + ' KB ' + type + ', over the ~200 KB budget: choose a calmer photo (less fine'
                    + ' detail or grain), or export it with less sharpening');
      } else console.log('ok    ' + line + kb + ' KB ' + type);
    } catch (e) {
      failed++;
      console.log('FAIL  the home page\'s first photo: %s', e.message);
    }
  }
  console.log(failed ? failed + ' photo address(es) failed' : 'photos: all ' + photos.length + ' load, original and resized');
  process.exit(failed ? 1 : 0);
})();
