# Launch checklist

Everything the site needs that lives outside this repo: DNS, Cloudflare settings,
Google, ResDiary and the opening day itself. These are steps for a person with the
logins (the code never changes them). Tick them off as you go.

Cloudflare: the account is **Polarized Jar**, the zone is **sol.pizza** (see
`README-DEPLOY.md`). The login also sees a second account with an unused `sol-pizza`
Worker: make every change in Polarized Jar.

---

## Do now

### 1. www.sol.pizza goes to sol.pizza

`www.sol.pizza` has no DNS record today, so it doesn't load.

1. Cloudflare → sol.pizza → **DNS** → **Records** → **Add record**:
   type `AAAA`, name `www`, IPv6 address `100::`, proxy status **Proxied** (orange
   cloud). (`100::` is a placeholder: the redirect below answers before anything
   would try to reach it.)
2. **Rules** → **Redirect Rules** → **Create rule** (or the "Redirect from WWW to root"
   template):
   - If: **Hostname** equals `www.sol.pizza`
   - Then: **Dynamic**, expression `concat("https://sol.pizza", http.request.uri.path)`,
     status **301**, **Preserve query string** on.
3. Check: `https://www.sol.pizza/menu/` lands on `https://sol.pizza/menu/`.

### 2. Mail: SPF and DMARC (Google Workspace)

sol.pizza's mail runs on Google Workspace, and DKIM is already set up. SPF and DMARC are
missing, so mail from @sol.pizza is easier to spoof and more likely to land in spam.

1. First, list everything that sends mail **as** an @sol.pizza address: Google Workspace,
   and maybe ResDiary's confirmations, CukCuk, a newsletter tool. Each one needs its own
   `include:` in the SPF record (its help pages give it).
2. Cloudflare → sol.pizza → **DNS** → **Add record**: type `TXT`, name `@`, content
   `v=spf1 include:_spf.google.com ~all` (other senders' `include:`s go before `~all`).
   There must be only one SPF record: if a `v=spf1` record already exists, edit it.
3. Create an address for DMARC reports in Google Workspace (for example a group
   `dmarc@sol.pizza`), then **Add record**: type `TXT`, name `_dmarc`, content
   `v=DMARC1; p=none; rua=mailto:dmarc@sol.pizza; fo=1`.
4. After two to four weeks of reports showing only your own senders, change `p=none` to
   `p=quarantine`, and later to `p=reject`.
5. Check with Google's https://toolbox.googleapps.com/apps/checkmx/ (domain `sol.pizza`).

Never turn on **Cloudflare Email Routing** for sol.pizza: it replaces the MX records and
mail to Google Workspace stops arriving.

### 3. Share cards: ask Facebook to look again

The share cards changed (new fonts, one per language, nothing out of date). Facebook and
Zalo keep the old picture until they look again. Once this is on sol.pizza:

1. https://developers.facebook.com/tools/debug/ → paste each address → **Scrape Again**:
   `https://sol.pizza/`, `/vi/`, `/menu/`, `/menu/wine/`, `/about/`, `/booking/`,
   `/visit-us/`, `/private-dining/`, `/events/`, `/press/`, `/jobs/`.
2. Zalo has no such tool: its previews update by themselves within a few days.

### 4. Adobe Fonts: show the hand-written line straight away

https://fonts.adobe.com → **My Adobe Fonts** → **Web Projects** → the project with kit
`umo0non` → **Font display**: **swap** → **Save**. (Today it's "auto", which can hide
the hand-written line for up to three seconds.) While there, remove Gryphius MVB and
Gryphius MVB Small Caps from the project: the site doesn't use them, and the kit gets
lighter. Keep the Creative Cloud plan behind the project active.

### 5. Old `?lang=vi` links: a 301 at the edge (optional)

The pages already send `sol.pizza/menu/?lang=vi` to `/vi/menu/` themselves, a moment after
they load. A Redirect Rule does it before anything loads, with a 301 search engines
understand:

**Rules** → **Redirect Rules** → **Create rule** → **Edit expression**:

```
(http.host eq "sol.pizza" and http.request.uri.query contains "lang=vi"
 and not starts_with(http.request.uri.path, "/vi/")
 and http.request.uri.path ne "/vi"
 and not http.request.uri.path contains "."
 and not starts_with(http.request.uri.path, "/dough")
 and not starts_with(http.request.uri.path, "/api/")
 and not starts_with(http.request.uri.path, "/careers")
 and not http.request.uri.path in {"/story" "/story/" "/visit" "/visit/" "/wine" "/wine/"
   "/wines" "/wine-list" "/winelist" "/drinks" "/book" "/book/" "/reservations" "/reservations/"})
```

Then: **Dynamic**, `concat("https://sol.pizza/vi", http.request.uri.path)`, **301**,
**Preserve query string** on. Check: `https://sol.pizza/about/?lang=vi` goes to
`https://sol.pizza/vi/about/?lang=vi`, and `https://sol.pizza/story/?lang=vi` still
reaches `/vi/about/`. Left out: the kitchen (`/dough/`, no Vietnamese address), files
(addresses with a dot), and the old addresses in `src/_redirects`: those go to their new
page first, which then opens in Vietnamese. If `src/_redirects` gains an address, add it
to the list in braces.

### 6. Cloudflare's bot script (decide)

On sol.pizza (not on previews) Cloudflare adds a bot-detection script to every page. On
a phone it costs about half a second of the browser's time before the page responds, and
a deprecated browser feature in it costs Lighthouse "Best Practices" points; it also sets
the `cf_clearance` cookie (listed in the cookie notice). The site has no guest forms or
logins for bots to attack (the kitchen's sign-in limits tries itself). To switch it off:
**Security** → **Bots** → **JavaScript Detections** off (and **Bot Fight Mode** off, if
it's on). Keep it if you'd rather have the protection; the budgets are measured both ways
(`npm run check -- https://sol.pizza`).

### 7. Previews: who can see them (optional)

Pull request previews and the full previews are public addresses, kept out of search
(`noindex`) but not secret: the full ones show drafts and "Content needed" markers. To
put them behind a login: Cloudflare **Zero Trust** → **Access** → **Applications** → add
a self-hosted application for `*-sol-pizza.polarized-jar.workers.dev`, allowing your
team's email addresses (free for up to 50 people). sol.pizza itself stays public.

---

## Before opening

### 8. Google Business Profile

The listing is "Sol Hanoi" and still carries Sol Pizza's reviews.

- [ ] Name: as decided (the site says "Sol", with "Sol Hanoi" as its other name).
- [ ] Address: the full address, with its street: Số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội.
      Check the pin is on the new building (it drives directions everywhere).
- [ ] Opening date: set it, so the listing shows "Opening on …".
- [ ] Hours: Tuesday to Sunday, 17:00–23:00, closed Monday (none are set today), and
      special hours for holidays and Tết.
- [ ] Links: website `https://sol.pizza/`, menu `https://sol.pizza/menu/`, reservations
      `https://sol.pizza/booking/`.
- [ ] Photos: the room, the food, the outside, once they're shot.
- [ ] Ask ResDiary whether **Reserve with Google** works for restaurants in Vietnam.

### 9. ResDiary

- [ ] Widget: ResDiary → **Promote** → **Widget configurator**: languages English and
      Vietnamese, then **Embed Code** → copy the widget's URL into `RESDIARY_URL` in
      `build/gen.py` (CONTENT-NEEDED.md). The widget appears on `/booking/`, and the
      phone number, Call and Zalo become tappable across the site.
- [ ] Deposits: if guests pay a deposit inside the widget, say so: the site has to
      allow payment in the widget's frame (and ask ResDiary whether the payment step
      comes from another address, which needs allowing too).
- [ ] Languages: ask whether the widget can open in Vietnamese (a separate widget
      address, or a setting). If it's a separate address, it goes in `RESDIARY_URL_VI`.
- [ ] Analytics: the site already counts clicks on Book (`book_click`), after a yes to
      Analytics. If you switch on ResDiary's own Google Analytics, it runs inside the
      widget without the site's cookie banner: ask ResDiary first whether it waits for
      consent, and leave it off if not.

### 10. Enquiries and the newsletter

The site's forms send email to hello@sol.pizza (`ENQUIRIES` in `build/gen.py`), with
subjects that start the same way every time (`Private dining — Lan`, `Opening week —
Minh`, `Newsletter`):

- [ ] In Gmail, a filter for each, so nothing waits: **Subject** `"Private dining —"`
      (label "Private dining", and star it), `"Opening week —"` (label "Opening week"),
      `Newsletter` (label "Newsletter").
- [ ] Newsletter: keep the addresses in one place (a Google Contacts label, or a sheet),
      with the date each asked. When you choose a newsletter tool, import them, and
      honour every "please take me off".
- [ ] Decide who answers private dining enquiries, and how soon (the page promises
      "we'll come back to you").

### 11. Search

- [ ] Google Search Console: add `sol.pizza` as a **Domain** property and verify it
      with the TXT record it gives (Cloudflare → DNS → Add record), or send the
      HTML-tag code for the site's verification slot. Then **Sitemaps** → submit
      `https://sol.pizza/sitemap.xml` (both languages are in it).
- [ ] Bing Webmaster Tools: **Import from Google Search Console**.

### 12. Analytics

- [ ] GA4 (`G-SLBWDVH550`): **Admin** → **Events**: mark `book_click`, `call_click`,
      `zalo_click`, `directions_click`, `enquiry_submit` and `newsletter_signup` as key
      events (they appear after the first visitor who says yes).
- [ ] GA4: **Admin** → **Data retention**: 14 months, unless the lawyer says shorter.
- [ ] Meta Events Manager (pixel `856214124247013`): the site sends `BookClick`
      (custom), `Contact`, `FindLocation`, `ViewContent` and `Lead`, only after a yes to
      Advertising; build custom conversions from them.
- [ ] Both count only visitors who said yes: expect lower numbers than before the banner.

### 13. Workers Builds

- [ ] Workers → sol-pizza → **Settings** → **Builds** → **Branch control**: builds for
      non-production branches stay on for every branch (the `full/…` previews need it).

---

### 14. The legal pages: the lawyer's review

Drafts waiting in the full preview (`/privacy/guests/`, `/accessibility/`; the booking
terms on `/booking/`), each marked "Draft":

- [ ] The guest privacy notice: the retention periods, the list of companies that handle
      guests' data, and the wording. Once approved, delete its line in `WAITING`
      (`build/gen.py`) and merge: it goes live, and into the footer.
- [ ] The accessibility statement: the building's facts (step-free access, the lift, the
      toilets), then the same.
- [ ] Once the guest notice is live, link it from the enquiry forms and the newsletter
      sign-up.

---

## Opening day

1. [ ] In `build/gen.py`, set `SITE_STATE = 'open'` (and `OPENING_DATE`, if it isn't set
       already). Merge it: the home page, Booking, Visit, the descriptions and the
       structured data all switch, and every "opening soon" line goes. (With an
       `OPENING_DATE` set, the pages already switch in the browser at the opening time;
       this makes it permanent and tells search engines.)
2. [ ] ResDiary live, and `RESDIARY_URL` set.
3. [ ] Google Business Profile: open.
4. [ ] `npm run check -- https://sol.pizza` after the deploy.
