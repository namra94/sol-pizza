// The cookie choice the checks store before they load pages, in the version the site
// asks for (CONSENT_VERSION in build/gen.py): raising it, when the banner's wording
// changes, asks every guest again, and the checks follow without an edit.
//   const consent = require('./consent.js');
//   const v = await consent.versionAt(base);          // the checked site's own version
//   await ctx.addInitScript(consent.store, consent.choice({analytics: true}, v));
const fs = require('fs'), path = require('path');

const VERSION = Number(/^CONSENT_VERSION = (\d+)/m.exec(
  fs.readFileSync(path.resolve(__dirname, '..', 'build', 'gen.py'), 'utf8'))[1]);

// Runs in the page (addInitScript or evaluate): stores the choice, as site.js would
function store({v, analytics, ads}) {
  localStorage.setItem('sol-consent', JSON.stringify({v, t: new Date().toISOString(), analytics, ads}));
}

// The version a site asks for, from its home page's head script: a check of sol.pizza
// or a preview stores the choice that site expects, which may not be this checkout's yet.
async function versionAt(base) {
  try {
    const m = /c\.v!==(\d+)/.exec(await (await fetch(base.replace(/\/$/, '') + '/')).text());
    return m ? Number(m[1]) : VERSION;
  } catch (e) {
    return VERSION;
  }
}

module.exports = {
  VERSION,
  store,
  versionAt,
  // the argument for store(): Reject all unless told otherwise
  choice: (tools = {}, v = VERSION) => ({v, analytics: !!tools.analytics, ads: !!tools.ads}),
};
