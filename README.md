# sol.pizza — the main site

Five pages (home, menu, wine, story, visit) alongside the site that already
serves `/jobs/` and `/privacy/`. Static HTML, no framework, deploys to
Cloudflare Pages the same way you've been deploying the careers site.

---

## Deploy

The zip is a **complete site**, not a patch — it contains your existing
`/jobs/` and `/privacy/` folders untouched alongside the new pages. Upload the
whole thing to Cloudflare Pages as usual and everything stays where it is.

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
| `menu/` | Prices — every dish is listed, none of them priced yet |
| `menu/` | Happy hour and wine night times — carried over from Sol Pizza, unconfirmed |
| `story/` | What closing Sol Pizza meant; a paragraph on Ngoc |
| Home + menu | Confirm ASU House Bakery is doing the puddings |
| `build/gen.py` | Real Google Maps pin URL, real Instagram handle |

When everything is filled in, delete the `.todo` rule from
`assets/sol.css` and the highlights disappear site-wide.

### 3. Two placeholders that aren't visible on the page

- **`sitemap.xml` / structured data** — `visit/index.html` and `index.html`
  carry `Restaurant` schema (this is what puts your hours, address and
  "reserve a table" link into Google search results). It has
  `TODO_PHONE`, `TODO_STREET`, `TODO_LAT`, `TODO_LNG` in it. Fill those in
  and the listing gets much better.
- **`hello@sol.pizza`** — used site-wide for enquiries. Make sure it exists
  and someone reads it.

---

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

`build/gen.py` generates all five pages from one file, so the menu lives in
one Python list rather than scattered through HTML. To change a dish:

```python
('Pepperoni', 'Pepperoni',
 'Tomatoes, mozzarella, pepperoni, parmigiano, basil.',
 'Cà chua, mozzarella, pepperoni, parmigiano, húng quế.',
 '', ['hot']),
#  ↑name EN   ↑name VI   ↑desc EN   ↑desc VI   ↑price   ↑tags
```

**Prices.** Every dish currently has `''` for a price, so no price column is
drawn. Put a string in — `'340,000₫'` — and it appears on the right of that
row. Nothing else has to change; you can price the menu one dish at a time.

The four lists to edit, all near the top of their section in `build/gen.py`:

| List | What it is |
|---|---|
| `MENU` | Small plates, pizza, pasta |
| `TOPPINGS` | The chips under the pizza section |
| `BAR` | Cocktails, beer, sake, soft drinks — everything but wine |
| `WINES` | The `/wine/` page, by section |

A wine row is `(name, grape, producer, region EN, region VI, tags)`, and the
tags are `'glass'` (poured by the glass), `'house'` (house pour) and `'nat'`
(natural / low-intervention) — the three keys in the legend at the top of the
page. Dish tags are `'v'`, `'hot'` and `'new'`.

Then run `python3 build/gen.py` and deploy.

Use whichever you prefer — but pick one. If you hand-edit the HTML and then
run the generator, the generator wins and your edits are gone.

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
menu/index.html       Menu — food, toppings, the bar
wine/index.html       The wine list
story/index.html      Story
visit/index.html      Visit + ResDiary booking
404.html              Not-found page
assets/sol.css        All styling — brand tokens at the top
assets/sol.js         Language switch + mobile nav
assets/fonts.css      Self-hosted webfonts
assets/fonts/         EB Garamond + Be Vietnam Pro (woff2)
assets/elevation.svg  The building elevation drawing used in the hero
og-*.png              Share cards for WhatsApp / Facebook / Zalo
                      (re-render with `node og.js`, then `python3 build/pack_assets.py`)
sitemap.xml robots.txt _redirects
jobs/ privacy/        Your existing pages, unchanged
build/                The generator — not uploaded, keep it for editing
```

### Fonts

The site self-hosts EB Garamond and Be Vietnam Pro rather than calling
Google Fonts — one less third party, and noticeably faster on Vietnamese
networks. Both carry full Vietnamese diacritics.

When you have the webfont licences for the real brand faces (BN Arora,
Gryphius MVB, Plunct), drop the `.woff2` files into `assets/fonts/` and
uncomment the `@font-face` block at the top of `assets/sol.css`. Nothing
else needs to change — those family names are already first in the stack.

### Colours

All from `Sol_Brand Standards_250619.pdf`, defined once at the top of
`assets/sol.css`:

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
