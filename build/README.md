# build/ — how the site is generated

`python3 build/gen.py` (or `npm run build`) writes the public site into `dist/`:
every page not in `HIDDEN`, which is empty, so the whole site.
`python3 build/gen.py --full` (or `npm run build:full`) writes every page, and every
section still waiting for content, with `noindex`; see "Build modes" below. Either way:

1. **Fonts.** Copies the Philosopher and EB Garamond woff2 files
   (Latin, Latin Extended, Vietnamese) out of `node_modules/@fontsource` into
   `build/fonts/` and writes `build/fonts.css`. Both are generated and
   git-ignored; run `npm ci` first on a fresh machine.
2. **Share cards and BN Arora.** Unpacks the PNGs and the BN Arora font in
   `assets.b64.json` if they're missing, writes each share card's page into
   `og/html/` (for `npm run og`), and stops if a card's words have changed since its
   PNG was rendered, or the PNG isn't the one packed after (`og/cards.json`; "Share
   cards" below).
3. **Pages.** Home, About, the three menu pages (from `menu-data.json`), Events and
   each Eclipse edition (from `events-data.json`), Private dining, Visit, Booking,
   Press, Gift cards, Jobs and the opening-team role pages (from `jobs-data.json` and
   `jobs/*.md`), the filled role pages and the applicant privacy notice (re-wrapped
   from `src/`), the cookie notice, the guest privacy notice and the accessibility
   statement, 404, and in the full build the components page (`/styleguide/`). Pages
   in `WAITING` (gift cards, an edition without its details, the legal drafts) are
   built in both modes but written only in the full build. Photographs come from
   `media.json` (checked: alt text in both languages, a credit, a known slot), each a
   `<picture>` of Cloudflare-resized sizes; the full build puts a placeholder where one
   is missing. Each guest page is assembled with every line in both languages and
   written twice: English at `/…`, Vietnamese at `/vi/…` (`write_pages()`,
   `localise()`). The kitchen's pages (`/dough/`, `/dough/log/`, `/dough/login/`:
   behind the kitchen password, which `worker/index.js` checks; `noindex`) are written
   once each, bilingual, in their own frozen shell (`kitchen_page()`).
   The public build builds any page in `HIDDEN` but doesn't write it, so a
   mistake in one still stops every build, pull request previews included.
4. **Support files.** `sitemap.xml` (every public page in both languages, each listing
   both and English as the default, including the six role pages), `robots.txt`, and
   `dist/_redirects`: `src/_redirects` as it is, or, in a public build while `HIDDEN`
   lists a page, that file rewritten for it (below).
5. **Optimise.** Minifies the CSS (csso) and JS (terser), gives everything in
   `dist/assets/` a content-hashed name, inlines the free fonts' `@font-face`
   rules into each page, quantises the share cards if Pillow is installed, and
   writes `dist/_headers` (caching, security headers, and early hints for the fonts
   above the fold: English pages' and, for `/vi/`, Vietnamese pages').
6. **Language check** (both builds). Every guest page is in `dist/` in both
   languages, each with the right `<html lang>`, a self-canonical and reciprocal
   `hreflang`, nothing of the other language left in it, and links that stay in its
   language (EN · VI and other links with an `hreflang` go where they say); nothing is
   written under `/vi/dough`; and every section `gate()` keeps back is listed in
   `CONTENT-NEEDED.md`.
7. **Link check** (public build). Every `href`, `src`, canonical and alternate
   link, `og:url`, `og:image`, JSON-LD address, CSS `url()`, sitemap and
   `robots.txt` address, font preload and redirect destination must be a file in
   `dist/`, a redirect or an address the Worker answers (`WORKER_PATHS`: the
   kitchen's `/api/`), and none may lead to a page in `HIDDEN` (nor may such a
   page be in `dist/`). If one does, the build stops and lists it.

The checks on the data run in both modes: the wine counts (`PROSE_WINE_COUNTS`),
the job descriptions against `jobs-data.json` (salaries, openings, dates), the
announcements' dates (`announcements.json`), and the settings (`SITE_STATE`,
`OPENING_DATE`).

`npm run check` (in `check/`, its own package) runs both builds, then what a browser
can check: the behaviour (languages, cookie banner, header, phone bar, analytics events,
forms, Eclipse's dates, the keyboard, structured data: `behaviour.js`), accessibility
with axe on every page in both languages (`axe.js`), and screenshots at five widths in
both languages (`screens.js`, of the URL when there is one); given a URL, also Lighthouse
against the budgets
(`lighthouse.js`: Home, Menu and Booking, the median of three first visits each) and
every photo online (`media.js`).

## Build modes

Every page is public: `HIDDEN`, near the top of `gen.py`, is empty, so the public
build is the whole site and starts "Build mode: PUBLIC: not yet public: nothing,
the whole site". To take a page down, add its section's key (`menu`, `about`, `visit`,
`booking`, `events`, `private-dining`, as in `SECTIONS`); the Public column says what
changes then. Every build prints its mode on its first line.

| | Public (the default) | Full |
| --- | --- | --- |
| Run by | `npm run build`, `npm run deploy` (`--public`), Workers Builds on `main` and on every other branch (pull request previews) | `npm run build:full` (`--full`), Workers Builds on the `full-site` branch and on the `full/…` branches (`WORKERS_CI_BRANCH`), each pull request's full preview |
| Pages | Every page not in `HIDDEN` (now all of them) or `WAITING` (gift cards, the legal drafts, an Eclipse edition without its details), in both languages. A hidden page isn't written, and neither are the share cards and illustrations only it uses | Every page, in both languages, and the components page |
| Sections waiting for content (`gate()`) | Left out | Shown, with a yellow "Content needed" label and the key in `CONTENT-NEEDED.md` |
| Header | The public tabs whose pages exist (`BUILT`), plus Work with us while anything is hidden; no Food / Wine / Bar tabs while Menu is hidden. Now Menu · About · Events · Private dining · Visit | The same, whatever `HIDDEN` says |
| Footer "More" | The public tabs, Booking, Press, Work with us, Privacy, Cookies (and the waiting pages once they're public) | The same, whatever `HIDDEN` says, with the waiting pages |
| Home buttons | The first two of Book a table, See the menu, See open roles and @solhanoi on Instagram whose page is public (red, then outline): now Book a table and See the menu | Book a table, See the menu |
| 404 buttons | The first two of Menu, Booking, Home and See open roles whose page is public: now Menu and Booking | Menu, Booking |
| Home JSON-LD | `hasMenu` and `acceptsReservations` only while Menu and Booking are public (now both) | Both |
| Sitemap | Only public pages (now all of them), in both languages: `/`, About, the three menu pages, Visit, Booking, `/jobs/` and the six open role pages | The same pages, whatever `HIDDEN` says |
| `_redirects` | While anything is hidden, its pages (with and without the slash, and anything under them, English and `/vi/`) and every old address in `src/_redirects` that leads to one go to the home page in the same language with a **302** (browsers cache a 301, and these pages come back), and the rest of `src/_redirects` stays as it is. Now `src/_redirects` as it is | `src/_redirects` as it is |
| Search | Indexable | `noindex`: `X-Robots-Tag: noindex` in `_headers`, `Disallow: /` in `robots.txt` |
| Link check | Yes | No |

`--public` builds the public site even on the `full-site` and `full/…` branches; `npm
run deploy` uses it, so a full build can't be deployed by accident. With `HIDDEN` empty,
as now, the public build is every page, the same as the full build without `noindex`,
the components page and the sections waiting for content.

## The design files

`design/tokens.css` and `design/printed-menu.css` are the Printed menu design
as delivered, with one change so a bilingual label keeps its look: three
descendant-span selectors skip `[data-l]` (the language spans) and
`.filled li span + span` is now a child selector. The website feedback of
24 Sep 2026 changed them too: EB Garamond for body text, BN Arora and Plunct
switched on, the design-system tokens (`--surface-raised`, `--ink-on-brand`,
`--ink-on-sun`, `--focus`) and a 2px focus ring with a 2px offset, and the
footer column headings in EB Garamond SemiBold (600, the one extra weight in
`FONT_PLAN`; `<strong>` text uses it too). The feedback of 6 Oct 2026 took the
rules off the home facts row. The header comment in each file lists what
changed. Don't restyle them otherwise;
put anything the design doesn't cover in `design/site.css`.
`design/site.js` is the guest pages' script: the delivered header script (menu tabs,
nav sheet), grown into the bar that stays at the top, EN · VI, the cookie banner and
the analytics it allows, the events, the announcements.

`design/kitchen/` is the kitchen pages' own shell, frozen as every page had it on
12 Oct 2026: `kitchen.css` is tokens.css, printed-menu.css and site.css of that day,
one after the other; `kitchen.js` is printed-menu.js of that day (the in-page EN / VI
switch). Guest pages never load them, and the kitchen never loads the guest files, so
a change on one side can't reach the other.

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
- Preloaded: on English pages BN Arora and EB Garamond (Latin); on Vietnamese pages
  Philosopher and EB Garamond, Latin and Vietnamese (in each page's head, and as early
  hints in `_headers`).

## Share cards

A share card for each page in each language: `og-<name>.png` (English) and
`og-<name>-vi.png` (Vietnamese), 1200 × 630, in the site's own fonts (BN Arora for
English titles, Philosopher for Vietnamese, EB Garamond for the rest). The words are
`OG_CARDS` in `gen.py`; the layout is `og/card.html`. No counts and no "opening soon":
they'd go stale on a card nobody re-renders.

To change one: edit `OG_CARDS` (or the template), then from the repo's root

```
npm run build          # writes each card's page into build/og/html/ (and stops: the card is out of date)
npm run og             # renders build/og/png/, notes what each was rendered from in og/cards.json
npm run pack-assets    # reduces the PNGs to 96 colours (Pillow), packs them into assets.b64.json,
                       # and notes each one's hash in og/cards.json
npm run build          # passes again
```

and commit `build/assets.b64.json` and `build/og/cards.json`. `npm run og` needs the
check package (`npm --prefix check ci`); it answers the cards' font requests
(`localhost:8897`) from `build/` itself, so no server runs. The build stops while any card
was rendered from words that have since changed, or was rendered but not packed (the PNG
it unpacks isn't the one `og/cards.json` names), so a stale card can't reach sol.pizza.
