# build/ — how the site is generated

`python3 build/gen.py` (or `npm run build`) writes the public site into `dist/`:
every page not in `HIDDEN`, which is empty, so the whole site.
`python3 build/gen.py --full` (or `npm run build:full`) writes every page with
`noindex`; see "Build modes" below. Either way:

1. **Fonts.** Copies the Philosopher and EB Garamond woff2 files
   (Latin, Latin Extended, Vietnamese) out of `node_modules/@fontsource` into
   `build/fonts/` and writes `build/fonts.css`. Both are generated and
   git-ignored; run `npm ci` first on a fresh machine.
2. **Share cards and BN Arora.** Unpacks the PNGs and the BN Arora font in
   `assets.b64.json` if they're missing.
3. **Pages.** Home, About, the three menu pages (from `menu-data.json`), Booking,
   Jobs and the opening-team role pages (from `jobs-data.json` and `jobs/*.md`),
   the filled role pages and the privacy notice (re-wrapped from `src/`), 404.
   The public build builds any page in `HIDDEN` but doesn't write it, so a
   mistake in one still stops every build, pull request previews included.
4. **Support files.** `sitemap.xml` (including the six role pages), `robots.txt`,
   and `dist/_redirects`: `src/_redirects` as it is, or, in a public build while
   `HIDDEN` lists a page, that file rewritten for it (below).
5. **Optimise.** Minifies the CSS (csso) and JS (terser), gives everything in
   `dist/assets/` a content-hashed name, inlines the free fonts' `@font-face`
   rules into each page, quantises the share cards if Pillow is installed, and
   writes `dist/_headers` (caching, security headers, a font preload hint).
6. **Link check** (public build). Every `href`, `src`, canonical and alternate
   link, `og:url`, `og:image`, JSON-LD address, CSS `url()`, sitemap and
   `robots.txt` address, font preload and redirect destination must be a file in
   `dist/` or a redirect, and none may lead to a page in `HIDDEN` (nor may such
   a page be in `dist/`). If one does, the build stops and lists it.

The checks on the data run in both modes: the wine counts (`PROSE_WINE_COUNTS`)
and the job descriptions against `jobs-data.json` (salaries, openings, dates).

## Build modes

Every page is public: `HIDDEN`, near the top of `gen.py`, is empty, so the public
build is the whole site and starts "Build mode: PUBLIC: not yet public: nothing,
the whole site". To take a page down, add its header tab's key (`about`, `menu`,
`booking`, as in `NAV_TABS`); the Public column says what changes then. Every
build prints its mode on its first line.

| | Public (the default) | Full |
| --- | --- | --- |
| Run by | `npm run build`, `npm run deploy` (`--public`), Workers Builds on `main` and on every other branch (pull request previews) | `npm run build:full` (`--full`), Workers Builds on the `full-site` branch (`WORKERS_CI_BRANCH=full-site`) |
| Pages | Every page not in `HIDDEN` (now all of them). A hidden page isn't written, and neither are the share cards and illustrations only it uses | Every page |
| Header | The public tabs, plus Work with us while anything is hidden; no Food / Wine / Bar tabs while Menu is hidden. Now About · Menu · Booking | About · Menu · Booking |
| Footer "More" | The public tabs, Work with us, Privacy | About, Menu, Booking, Work with us, Privacy |
| Home buttons | The first two of Book a table, See the menu, See open roles and @solhanoi on Instagram whose page is public (red, then outline): now Book a table and See the menu | Book a table, See the menu |
| 404 buttons | The first two of Menu, Booking, Home and See open roles whose page is public: now Menu and Booking | Menu, Booking |
| Home JSON-LD | `hasMenu` and `acceptsReservations` only while Menu and Booking are public (now both) | Both |
| Sitemap | Only public pages (now all of them): `/`, About, the three menu pages, Booking, `/jobs/` and the six open role pages | The same pages, whatever `HIDDEN` says |
| `_redirects` | While anything is hidden, its pages (with and without the slash, and anything under them) and every old address in `src/_redirects` that leads to one go to `/` with a **302** (browsers cache a 301, and these pages come back), and the rest of `src/_redirects` stays as it is. Now `src/_redirects` as it is | `src/_redirects` as it is |
| Search | Indexable | `noindex`: `X-Robots-Tag: noindex` in `_headers`, `Disallow: /` in `robots.txt` |
| Link check | Yes | No |

`--public` builds the public site even on the `full-site` branch; `npm run
deploy` uses it, so a full build can't be deployed by accident. With `HIDDEN`
empty, as now, the public build is the whole site, the same as the full build
without `noindex`. To take a page down, add its key to `HIDDEN`; to put it back,
delete the key (README.md, "Taking a page down").

## The design files

`design/tokens.css` and `design/printed-menu.css` are the Printed menu design
as delivered, with one change so a bilingual label keeps its look: three
descendant-span selectors skip `[data-l]` (the language spans) and
`.filled li span + span` is now a child selector. The website feedback of
24 Sep 2026 changed them too: EB Garamond for body text, BN Arora and Plunct
switched on, the design-system tokens (`--surface-raised`, `--ink-on-brand`,
`--ink-on-sun`, `--focus`) and a 2px focus ring with a 2px offset, and the
footer column headings in EB Garamond SemiBold (600, the one extra weight in
`FONT_PLAN`; `<strong>` text uses it too); the header comment in each file lists
what changed. Don't restyle them otherwise;
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
