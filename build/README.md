# build/ — how the site is generated

`python3 build/gen.py` (or `npm run build`) writes the whole site into `dist/`:

1. **Fonts.** Copies the Philosopher and EB Garamond woff2 files
   (Latin, Latin Extended, Vietnamese) out of `node_modules/@fontsource` into
   `build/fonts/` and writes `build/fonts.css`. Both are generated and
   git-ignored; run `npm ci` first on a fresh machine.
2. **Share cards and BN Arora.** Unpacks the PNGs and the BN Arora font in
   `assets.b64.json` if they're missing.
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
`.filled li span + span` is now a child selector. The website feedback of
24 Sep 2026 changed them too: EB Garamond for body text, BN Arora and Plunct
switched on, the design-system tokens (`--surface-raised`, `--ink-on-brand`,
`--ink-on-sun`, `--focus`) and a 2px focus ring with a 2px offset; the header
comment in each file lists what changed. Don't restyle them otherwise;
put anything the design doesn't cover in `design/site.css`.
`design/printed-menu.js` is the delivered header script with the language code
merged into this repo's markup.

## Brand fonts

- **BN Arora** (English headings) is licensed for web use (confirmed 24 Sep
  2026). The file travels in `assets.b64.json` as `build/brand/BNArora-Regular.woff2`
  (unpacked at build time, git-ignored) and is served at
  `/assets/fonts/bn-arora-400-normal.woff2`, with its `@font-face` inlined into
  every page (`font-display: swap`, weight 400 only). Headings set
  `font-synthesis: none`, so the browser never fakes a bold or an italic. To
  replace the file, put the new one at `build/brand/BNArora-Regular.woff2` and
  run `npm run pack-assets`; on other machines delete `build/brand/` before the
  next build (an unpacked file is never overwritten). `/assets/` is cached for a
  year and this filename has no content hash, so a changed font also needs a new
  name: change `BN_ARORA_URL` in `gen.py` (e.g. `bn-arora-400-normal-v2.woff2`). It has no Vietnamese letters: Vietnamese pages set
  headings in Philosopher, and a Vietnamese name inside an English heading is
  marked `<span lang="vi">` so it gets Philosopher too (see `site.css`).
- **Plunct** (the one hand-written phrase per section, `.hand`, English only)
  comes from the Adobe Fonts kit, loaded without blocking the first paint.
  Vietnamese pages keep EB Garamond italic.
- Preloaded on every page: BN Arora and EB Garamond (latin).

## Share cards

`og/og-*.html` are the sources. Render them with `node og.js` (needs
Playwright), then run `npm run pack-assets` so the PNGs travel in
`assets.b64.json`.
