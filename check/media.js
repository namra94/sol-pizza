// Every photograph in build/media.json, online: the original in the sol-media bucket
// (media.sol.pizza), and Cloudflare's resized copy on sol.pizza, both answer with an
// image. Run it after uploading photos and merging their entries; npm run check runs
// it with a URL. Nothing to check while media.json has no photos.
//   node media.js
const fs = require('fs'), path = require('path');

const MEDIA = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'build', 'media.json'), 'utf8'));
const BASE = 'https://media.sol.pizza/';
const CDN = 'https://sol.pizza/cdn-cgi/image/';

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
  console.log(failed ? failed + ' photo address(es) failed' : 'photos: all ' + photos.length + ' load, original and resized');
  process.exit(failed ? 1 : 0);
})();
