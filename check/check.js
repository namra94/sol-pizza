// npm run check (from the repo's root): everything that keeps sol.pizza right.
//   1. both builds: the full one (every page, noindex) and the public one, each with
//      its own checks (wine counts, job data, share cards, languages, gates; the
//      public one also checks every link)
//   2. behaviour: languages, cookies, header, phone bar, events (behaviour.js)
//   3. accessibility: axe on every page in both languages (axe.js)
//   with a URL (npm run check -- https://…): behaviour and axe there too,
//   Lighthouse against the budgets (lighthouse.js), and every photo in
//   build/media.json loading from R2 and through Cloudflare (media.js)
// The public build is left in dist/ at the end. Nothing here is committed: reports go
// to check/out/. First time: npm --prefix check ci (and, outside Claude's cloud,
// npx --prefix check playwright install chromium).
const {spawnSync} = require('child_process');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const url = process.argv[2];
const steps = [
  ['full build', 'python3', ['build/gen.py', '--full'], ROOT],
  ['public build', 'python3', ['build/gen.py', '--public'], ROOT],
  ['behaviour', 'node', ['behaviour.js'], __dirname],
  ['accessibility', 'node', ['axe.js'], __dirname],
];
if (url) {
  steps.push(['behaviour at ' + url, 'node', ['behaviour.js', url], __dirname],
             ['accessibility at ' + url, 'node', ['axe.js', url], __dirname],
             ['Lighthouse at ' + url, 'node', ['lighthouse.js', url], __dirname],
             ['photos online', 'node', ['media.js'], __dirname]);
}
const results = [];
for (const [name, cmd, args, cwd] of steps) {
  console.log('\n== ' + name);
  const r = spawnSync(cmd, args, {cwd, stdio: 'inherit'});
  results.push([name, r.status === 0]);
  if (r.status !== 0 && name.endsWith('build')) break;      // nothing to check without a build
}
console.log('\n' + results.map(([n, good]) => (good ? 'ok    ' : 'FAIL  ') + n).join('\n'));
process.exit(results.every(([, good]) => good) && results.length === steps.length ? 0 : 1);
