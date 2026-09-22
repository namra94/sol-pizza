# sol.pizza — the main site

Five pages (home, menu, story, visit, careers) plus the three role pages,
all in one design. Static HTML, no framework, deploys to Cloudflare Pages
the same way you've been deploying the careers site.

---

## Deploy

The site now runs as a **Cloudflare Worker with static assets** (Worker name
`sol-pizza`, config in `wrangler.jsonc`), which is what Cloudflare recommends
for new sites. `/privacy/` is carried across untouched. `/jobs/` has been
rebuilt inside the site design (see *Careers* below); the three role pages
keep their URLs, so every link you've already shared still works.

To redeploy after a change:

```
python3 build/gen.py      # rebuild ./dist
npx wrangler login        # once, opens the browser
npx wrangler deploy       # uploads ./dist to the sol-pizza Worker
```

The old Pages direct-upload zip still works too if you ever need it —
`dist/` is the same folder either way.

One thing changed in `_redirects`: the old rule that pointed `/` at
`/jobs/index.html` is gone, because the apex now has a real homepage.
Redirects added so no old link breaks:

```
/careers      → /jobs/
/book         → /visit/#book
/reservations → /visit/#book
```

---

## Before you go live — 3 things

### 1. Paste your ResDiary widget URL

In ResDiary: **Promote → Widget configurator**, build the widget (set the
colours to `#A72024` red / `#F2CC73` gold and upload the Sol logo while
you're in there), then open the **Embed Code** tab and copy the widget URL
out of the code it hands you. It looks like:

```
https://booking.resdiary.com/widget/Standard/YourVenueName/12345
```

Open `visit/index.html`, find this line near the top of the booking section,
and paste it between the quotes:

```html
<script>
  window.SOL_RESDIARY_URL = "";   /* ← paste your ResDiary widget URL here */
</script>
```

That's the whole integration. Until you paste it, the page shows a
"Booking opens soon — email us" panel instead, so it never looks broken.

Optional extras you can append to the URL: `?partySize=2`,
`?date=2026-10-05` (put a date first if you use one), `&channelcode=WEB`
to tag which bookings came from the website.

### 2. Fill in the yellow-flagged blanks

Every unconfirmed fact on the site is wrapped in `<span class="todo">` and
renders with a yellow highlight and a ⚑ flag, so you can spot them by
scrolling. Currently flagged:

| Where | What's needed |
|---|---|
| Everywhere (footer, home, visit) | Street address, phone number |
| `visit/` | Opening hours, getting here, parking, max group size |
| `menu/` | All dish names and every price |
| `story/` | What closing Sol Pizza meant; a paragraph on Ngoc |
| `jobs/` | The opening-team card: each floor and kitchen role with pay and hours, once Long and Ngọc have them |
| Home + menu | Confirm ASU House Bakery is doing the puddings |
| `build/gen.py` | Real Google Maps pin URL, real Instagram handle |

When everything is filled in, delete the `.todo` rule from
`build/sol.css`, rebuild, and the highlights disappear site-wide.

### 3. Two placeholders that aren't visible on the page

- **`sitemap.xml` / structured data** — `visit/index.html` and `index.html`
  carry `Restaurant` schema (this is what puts your hours, address and
  "reserve a table" link into Google search results). It has
  `TODO_PHONE`, `TODO_STREET`, `TODO_LAT`, `TODO_LNG` in it. Fill those in
  and the listing gets much better.
- **`hello@sol.pizza`** — used site-wide for enquiries. Make sure it exists
  and someone reads it.

---

## Careers (`/jobs/`)

The listing is generated from the `ROLES` list at the top of the careers
section in `build/gen.py`. As of this build:

| Role | Status on the site |
|---|---|
| Restaurant Accountant | **Open** — "reviewed as they arrive" (the 3 Sept deadline is gone) |
| Sous Chef | Filled, September 2026 |
| Restaurant Supervisor | Filled, September 2026 |
| Opening team — floor & kitchen | A green card inviting CVs to jobs@sol.pizza |

Filled roles are listed under "Recently filled" and their pages stay live
with a gold banner at the top, no apply button, and a `noindex` tag so
Google stops sending applicants to them. They also no longer fire the Meta
`ViewContent` event, so they won't pollute the retargeting audience.

- **To close the accountant role:** set `status='filled'` on it in `ROLES`
  and add `filled_en` / `filled_vi`. Rebuild.
- **To open a new role:** write its page in the same shape as the existing
  ones in `src/jobs/`, add an entry to `ROLES`, rebuild. The role pages are
  English-only for now; Vietnamese readers see a one-line note saying so.

`pixel.js` (the Meta events — ViewContent, ExpandJD, Lead) is unchanged and
still wired up on every careers page.

## Editing

### The easy way

Open the `.html` file and edit the text. Every translatable piece appears
twice, once in each language:

```html
<span data-l="en" lang="en">Book a table</span>
<span data-l="vi" lang="vi">Đặt bàn</span>
```

Edit both, or the two languages drift apart.

### The tidier way

`build/gen.py` generates all four pages from one file, so the menu lives in
one Python list rather than scattered through HTML. To change a dish:

```python
('Margherita', 'Margherita',
 'Fior di latte, basil, olive oil.', 'Fior di latte, húng quế, dầu ô liu.',
 '180,000₫', ['v']),
#  ↑name EN    ↑name VI    ↑desc EN    ↑desc VI    ↑price   ↑tags
```

Then run `python3 build/gen.py` and re-upload `dist/`. (One-time setup on
a fresh machine: `npm install csso terser` in the site folder — the build
uses them to minify.)

Use whichever you prefer — but pick one. If you hand-edit the HTML and then
run the generator, the generator wins and your edits are gone.

**CSS is different.** It's minified and inlined into every page at build
time, so a style change means editing `build/sol.css` and rebuilding — there
is no stylesheet file to edit in `dist/`.

---

## How the language switch works

EN/VI buttons in the header. Both languages are in the HTML; CSS hides one.
The choice is remembered in the browser, reflected in the URL as `?lang=vi`
so you can share a Vietnamese link directly, and a browser set to Vietnamese
gets Vietnamese on first visit. It works without a page reload and the page
title changes too.

The Vietnamese throughout is a first draft — worth having someone on the
team read it before opening, particularly the menu, where dish names are
partly a judgement call about what to translate and what to leave in Italian.

---

## What's in the box

```
index.html            Home
menu/index.html       Menu
story/index.html      Story
visit/index.html      Visit + ResDiary booking
jobs/index.html       Careers listing
jobs/*.html           Role pages (accountant open; sous chef + supervisor filled)
404.html              Not-found page
assets/sol.<hash>.js  Language switch + mobile nav (minified, cached a year)
assets/fonts/         EB Garamond + Be Vietnam Pro (woff2, cached a year)
og-*.png              Share cards for WhatsApp / Facebook / Zalo
pixel.js              Meta pixel events for the careers pages
_headers              Caching + security headers for Cloudflare
sitemap.xml robots.txt _redirects
privacy/              Your existing page, unchanged
build/                The generator + readable CSS/JS — not uploaded
```

### Speed

Measured with Lighthouse on a simulated slow phone, analytics scripts
excluded so it's measuring our page and not Google's:

| | Before | After |
|---|---|---|
| Mobile performance | 91 | 97–99 |
| Largest Contentful Paint | 3.3 s | 2.1–2.4 s |
| Page weight (home) | 340 KB | 194 KB |
| Accessibility | 95 | 100 |
| Old careers page | 172 KB | 27 KB |

What changed: the building drawing is gone (144 KB on its own); CSS is
minified and inlined so nothing blocks the first paint; JS is minified and
served under a content-hashed name with a one-year cache; fonts are
preloaded through Early Hints; share images are a third of the size;
`_headers` adds `nosniff`, `SAMEORIGIN`, a referrer policy and a
permissions policy. HTML pages are served with `must-revalidate`, so a
redeploy is visible immediately.

### Fonts

The site self-hosts EB Garamond and Be Vietnam Pro rather than calling
Google Fonts — one less third party, and noticeably faster on Vietnamese
networks. Both carry full Vietnamese diacritics.

When you have the webfont licences for the real brand faces (BN Arora,
Gryphius MVB, Plunct), drop the `.woff2` files into `build/fonts/` and
uncomment the `@font-face` block at the top of `build/sol.css`. Nothing
else needs to change — those family names are already first in the stack.

### Colours

All from `Sol_Brand Standards_250619.pdf`, defined once at the top of
`build/sol.css`:

```
--sol-red    #A72024   sun, wine, tomatoes    headers, hero, buttons
--sol-maroon #4E2428   wood                   body text, footer
--sol-cream  #F9E9D3   cheese                 page background
--sol-gold   #F2CC73   sunlight               buttons, accents
--sol-green  #506D55   basil, olives, pesto   the "Visit" band
```

---

## Analytics

GA4 (`G-SLBWDVH550`) and the Meta pixel (`856214124247013`) are on every new
page, same as the careers pages. The booking widget fires a
`booking_widget_shown` GA event when it loads, so you can see how many people
reach the booking step versus how many actually book.
