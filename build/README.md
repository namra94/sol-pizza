# build/ — how the site is generated

`python3 build/gen.py` (or `npm run build`) writes the whole site into `dist/`:

1. **Fonts.** Copies the Philosopher and EB Garamond woff2 files
   (Latin, Latin Extended, Vietnamese) out of `node_modules/@fontsource` into
   `build/fonts/` and writes `build/fonts.css`. Both are generated and
   git-ignored; run `npm ci` first on a fresh machine.
2. **Share cards.** Unpacks the PNGs in `assets.b64.json` if they're missing.
3. **Pages.** Home, About, the three menu pages (from `menu-data.json`), Booking,
   Jobs, the role pages and the privacy notice (re-wrapped from `src/`), 404.
4. **Support files.** `sitemap.xml`, `robots.txt`, and `src/_redirects` copied
   to `dist/_redirects`.
5. **Optimise.** Minifies the CSS (csso) and JS (terser), gives everything in
   `dist/assets/` a content-hashed name, inlines the free fonts' `@font-face`
   rules into each page, quantises the share cards if Pillow is installed, and
   writes `dist/_headers` (caching, security headers, a font preload hint).

## The design files

`design/tokens.css` and `design/printed-menu.css` are the Printed menu design
as delivered, with one change so a bilingual label keeps its look: three
descendant-span selectors skip `[data-l]` (the language spans) and
`.filled li span + span` is now a child selector. Don't restyle them;
put anything the design doesn't cover in `design/site.css`.
`design/printed-menu.js` is the delivered header script with the language code
merged into this repo's markup.

## BN Arora, once its web licence is confirmed

Headings use Philosopher until then. To switch:

1. Add `fonts/brand/BNArora-Regular.woff2` to `build/assets.b64.json` (extend
   `pack_assets.py` to pick it up) so the repo stays text-only.
2. In `gen.py`: copy it to `dist/assets/fonts/` in `copy_existing()`, add an
   `@font-face` for `"BN Arora"` (`font-display: swap`) to the inlined font
   CSS, preload it next to `PRELOAD_FONT`, and set
   `BRAND_FONTS = 'display serif'`.
3. Compare the result with the package's `reference/screenshots/brand/`.

Until then the BN Arora file must not reach git or `dist/`.

## Share cards

`og/og-*.html` are the sources. Render them with `node og.js` (needs
Playwright), then run `npm run pack-assets` so the PNGs travel in
`assets.b64.json`.
