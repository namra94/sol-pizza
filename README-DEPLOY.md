# Deploying sol.pizza

The site is a Cloudflare Worker with static assets (`wrangler.jsonc`, Worker name
`sol-pizza`) in the Cloudflare account **Polarized Jar**
(`8c4ec4948dc4732b29398c10fcb2020b`, pinned as `account_id` in `wrangler.jsonc`).
Everything is generated from `build/gen.py`; nothing binary lives in git: fonts
come from npm, the share-card PNGs are unpacked from `build/assets.b64.json`.

The login arman@sol.pizza also sees a second account, "Arman@sol.pizza's
Account", which has an older `sol-pizza` Worker that doesn't serve the domain.
Deploy and roll back in Polarized Jar only.

## Cloudflare Workers Builds (automatic on every push to main)

Connected. Workers → sol-pizza → Settings → Builds:

| Setting              | Value                              |
| -------------------- | ---------------------------------- |
| Production branch    | `main`                             |
| Build command        | `npm run build`                    |
| Deploy command       | `npx wrangler deploy`              |
| Preview command      | `npx wrangler preview` (other branches) |
| Root directory       | `/`                                |

The build image has Node 24 and Python 3.13, which is all the build needs. Each
build shows up as a "Workers Builds: sol-pizza" check on the commit in GitHub.
`npm run build` builds the **public** site (every page not in `HIDDEN`, which is
empty: the whole site; see "Build modes" in `build/README.md`), except on the
`full-site` branch below, and every build log starts with the mode it built.

A push to any other branch runs a **preview build**: the same build, then
`npx wrangler preview`, which puts that branch on its own Preview URL (posted on
the pull request) and leaves sol.pizza alone. The URL is the branch name, with
`/` as `-`, then `-sol-pizza.polarized-jar.workers.dev`: the branch `public-cut`
is at `https://public-cut-sol-pizza.polarized-jar.workers.dev`. A pull request's
preview shows the public site, as `main` would deploy it. It needs the
`"previews": {}` block in `wrangler.jsonc`; without it every preview build fails.
Preview URLs are public unless Cloudflare Access protects them.

## full-site: the whole site on a Preview URL

One stable link always shows `main` built in full, with `noindex`. While
`HIDDEN` (in `build/gen.py`) is empty it matches sol.pizza; a page taken down
stays reviewable there:

**https://full-site-sol-pizza.polarized-jar.workers.dev**

That is the Preview URL of the branch `full-site`. The GitHub Actions workflow
`.github/workflows/full-site.yml` force-pushes `main` to `full-site` on every push
to `main`, and on `full-site` the build sees `WORKERS_CI_BRANCH=full-site` and
builds the full site: every page, as `npm run build:full` does, with `noindex`
(`X-Robots-Tag: noindex` on every response, `Disallow: /` in `robots.txt`) so
the preview stays out of search. It never touches sol.pizza: `full-site` isn't
the production branch.

- **Never commit to `full-site`.** It is a mirror of `main`, and the next push
  to `main` overwrites it. Work on a branch and merge to `main` as usual.
- To mirror by hand: GitHub → Actions → Mirror main to full-site → Run
  workflow. That only moves `full-site` when `main` has moved; to rebuild the
  same commit (say its `full-site` build failed), rerun that build from its
  check on GitHub (the "Workers Builds: sol-pizza" check → Details → Rerun).
- `full-site` is the same commit as `main`, so each commit on `main` gets two
  "Workers Builds: sol-pizza" runs under one check name, the production deploy
  and the `full-site` preview, and GitHub shows the later one. To see whether
  sol.pizza deployed, look at Workers → sol-pizza → Deployments, not only the
  check on the commit.
- Never make `full-site` the production branch in Workers Builds: sol.pizza
  would serve the full site with `noindex`.
- To see the full build of a branch before it's merged, run `npm run build:full`
  and `npx wrangler dev` on your machine.

## full/…: a full preview for each pull request

A pull request's own preview shows the public site, as `main` would deploy it. To see the
sections still waiting for content before merging, each branch Claude works on has a
full twin: `.github/workflows/full-preview.yml` copies every push to `claude/<name>` to
`full/claude/<name>`, Workers Builds builds that as the full site (every page and
section, the "Content needed" markers, `noindex`), and it gets its own Preview URL:

**`https://full-claude-<name>-sol-pizza.polarized-jar.workers.dev`**

(for `claude/intl-1-foundations`: `https://full-claude-intl-1-foundations-sol-pizza.polarized-jar.workers.dev`).

- **Never commit to a `full/…` branch.** It's a copy; the next push overwrites it.
  Deleting `claude/<name>` deletes its copy.
- Like every preview, it's public but kept out of search. LAUNCH-CHECKLIST.md
  ("Previews") says how to put the previews behind a login.

## By hand

Only if Workers Builds is off; otherwise a push already deploys.

```
npm ci
npx wrangler login     # once
npm run deploy         # builds the public site into ./dist, then wrangler deploy
```

Always deploy with `npm run deploy`: it builds the public site
(`python3 build/gen.py --public`) right before `wrangler deploy`, so a full
build left in `./dist` by `npm run build:full` can't reach sol.pizza.

## Rolling back

```
npx wrangler deployments list        # note the version id that was live before
npx wrangler rollback <version-id>
```

Don't roll back to a version deployed between the public/full split and the
commit "Whole site public again: HIDDEN = []". Versions carry no message, so go
by date: the first is `3d69d1d0…` (27 Sep 2026, 19:02 UTC). Those serve the
temporary site, home and jobs only, with About, Menu and Booking sent to `/`
with a 302. Versions from before the split serve the whole site as it was then,
without the new home tagline.

## The kitchen: password and dough log

`/dough/` (the dough calculator and the dough log) is behind the kitchen
password, and the log is kept in a D1 database. Both live in the Cloudflare
account, not the repo: the Worker's own code (`worker/index.js`, which runs only
for `/dough/*`, `/backoffice/*` and `/api/*`) reads the password from the secret `DOUGH_PASSWORD`
and the log from the binding `DOUGH_DB` (`wrangler.jsonc`). Without the
password, `/dough/` says signing in isn't set up and lets no one in.

### Setting it up (done 6 Oct 2026)

Both are in place: the database `sol-dough` (Polarized Jar, Eastern North
America; its id is in `wrangler.jsonc` and isn't a secret) and the secret
`DOUGH_PASSWORD` on the `sol-pizza` Worker. The Worker makes the log's tables
itself the first time it's used. Were they ever lost, from this folder:

```
npx wrangler d1 create sol-dough           # then put the database_id it prints into wrangler.jsonc
npx wrangler secret put DOUGH_PASSWORD     # type the kitchen password when asked
```

Use a passphrase the kitchen can type on a phone but nobody would guess: four
or five unrelated words. After 10 wrong tries from one address, signing in from
it waits 15 minutes.

### Changing the password

Run `npx wrangler secret put DOUGH_PASSWORD` again. Every phone is signed out
and needs the new one. Do this when someone with the password leaves.

### Previews and full-site

Previews don't inherit production settings (`"previews": {}` in
`wrangler.jsonc`), so a branch's Preview URL and full-site have no database and
no password: their `/dough/` stays locked, and nothing on a Preview can touch the
real log. To try the kitchen on a Preview, give that Preview its own password
(`npx wrangler preview secret put DOUGH_PASSWORD --name <branch>`); without a
database there, the calculator works and the log says it isn't set up.

### On your own machine

Copy `.dev.vars.example` to `.dev.vars` (git-ignored) and run `npm run build`
then `npx wrangler dev`: it signs in with the test password in that file and
keeps a local log in `.wrangler/` that never touches the real one. To clear a
local lockout: `npx wrangler d1 execute sol-dough --local --command "DELETE FROM dough_login_failures"`.

### The log's data

The log holds each batch, the kitchen's readings, notes and the name typed
under "Mixed by". To look at it outside the site:
`npx wrangler d1 execute sol-dough --remote --command "SELECT day, made_by, balls, ball_g FROM dough_log ORDER BY day DESC LIMIT 20"`.
D1's Time Travel can put the whole database back to an earlier minute (how far
back depends on the Cloudflare plan): `npx wrangler d1 time-travel restore sol-dough --timestamp=<when>`.
It rewinds everything logged since, so download the CSV first. The back office's
requests are in the same database: a restore rewinds those too.

## The back office: purchase requests

`/backoffice/` is for the team, behind one shared **staff password**, separate
from the kitchen's (README.md, "The back office"). Its first tool is the
**purchase request** (`/backoffice/purchase/`): anyone with the staff password
asks for supplies on a phone, and the Worker posts the request to Slack's
**#supply** in the 🛒 format management already uses. Approval stays in Slack,
with reactions: ✅ approve (the Kitchen approver for Kitchen, the Bar & FOH
approver for Bar and FOH, and Arman too when the estimate is over the limit
before VAT or the supplier isn't Active), 📦 ordered on Zalo, 🚚 received and
checked, ❌ cancelled, 🗂️ filed.

Where its data comes from:

- **The Order Guide** (suppliers, items, prices, the approval settings and the
  staff's names) is the Google Sheet **"Sol Hanoi — Order Sheet"**, read at run
  time through a small Apps Script web app bound to it
  (`tools/order-sheet.gs`, below). The Worker keeps a copy in D1 and fetches it
  again once it's 10 minutes old; when the sheet can't be reached it uses the
  last good copy, and the form says "Order Guide as of HH:MM". This repo is
  public: nothing from the sheet is ever committed.
- **The requests** are kept in D1 (`backoffice_purchases`), in the kitchen's
  database `sol-dough` through the same `DOUGH_DB` binding, next to the dough
  log. The Worker makes its tables the first time it's used.
- **Who it mentions** in Slack: the Slack member ids in `wrangler.jsonc`
  (`vars`: `SLACK_OWNER`, `SLACK_APPROVER_KITCHEN`, `SLACK_APPROVER_BAR_FOH`).
  They aren't secrets. If an approver changes, change the id there (Slack →
  their profile → ⋮ → Copy member ID) and the name in the Order Sheet's Settings.

### The three secrets

| Secret | What it is |
| --- | --- |
| `BACKOFFICE_PASSWORD` | The staff password |
| `SLACK_WEBHOOK_URL` | The Incoming Webhook into #supply (below) |
| `ORDER_GUIDE_URL` | The Apps Script web app's address, then `?token=` and its token (below) |

```
npx wrangler secret put BACKOFFICE_PASSWORD     # type the staff password when asked
npx wrangler secret put SLACK_WEBHOOK_URL       # paste the webhook's URL
npx wrangler secret put ORDER_GUIDE_URL         # paste the web app's URL with ?token=…
```

Each one goes straight into Cloudflare: never into the repo, a chat or a
ticket. Without `BACKOFFICE_PASSWORD`, `/backoffice/` says signing in isn't set
up and lets no one in. Without `ORDER_GUIDE_URL`, the form still works:
supplier and items typed by hand, no estimate, and every request needs Arman's
✅. Without `SLACK_WEBHOOK_URL`, requests are kept but marked failed, and the
sender sees why.

The staff password: four or five unrelated words, easy to type on a phone.
After 10 wrong tries from one address, signing in from it waits 15 minutes.
Staff stay signed in on a phone for 30 days. **To change it** (when someone
with it leaves), run `npx wrangler secret put BACKOFFICE_PASSWORD` again: every
phone is signed out of the back office (not the kitchen) and needs the new one.

### Creating the Slack webhook

1. api.slack.com/apps → **Create New App** → **From scratch**: name
   "Sol Back Office", workspace **solhanoi** → Create App.
2. **Incoming Webhooks** → turn it **On** → **Add New Webhook** (to Workspace)
   → pick **#supply** → Allow.
3. Copy the webhook URL (`https://hooks.slack.com/services/…`) and paste it
   into `npx wrangler secret put SLACK_WEBHOOK_URL`.

Anyone with that URL can post to #supply. If it ever leaks: the app's Incoming
Webhooks page → remove it, add a new one, and put the new URL as above.

### Setting up the Apps Script

1. Open the Order Sheet → **Extensions** → **Apps Script**.
2. Paste `tools/order-sheet.gs` (all of it) as a script file of the project, and
   save. (If Apps Script says `doGet` is already defined, the sheet already has
   a web app: the two have to be merged before going on.)
3. **Project Settings** (the gear) → **Script properties** → Add script
   property: `TOKEN` = a long random string, at least 32 letters and numbers
   (a password manager can make one). Save.
4. **Deploy** → **New deployment** → type **Web app**: execute as **Me**, who
   has access **Anyone** → Deploy → **Authorise access** (Google asks to let it
   read the spreadsheet) → copy the **Web app URL**
   (`https://script.google.com/macros/s/…/exec`).
5. `ORDER_GUIDE_URL` is that URL, then `?token=`, then the token. Open it in a
   browser to check: you should see the Order Guide as JSON (without the token:
   `{"error":"forbidden"}`). Then put it with
   `npx wrangler secret put ORDER_GUIDE_URL`.

The script finds every column by its header in row 1 (the headers are listed at
the top of `tools/order-sheet.gs`), so columns can be moved or added; it never
sends the suppliers' contact, terms or price-list columns. If a tab or a header
it needs is renamed, the web app answers with an error, and the Worker keeps
using its last good copy: rename it in the script too.

- **After changing the script**: Deploy → **Manage deployments** → edit (the
  pencil) → Version: **New version** → Deploy. The URL stays the same; a *new*
  deployment would have a new URL, and then `ORDER_GUIDE_URL` must be put again.
- **To change the token**: change `TOKEN` in Script properties, then put
  `ORDER_GUIDE_URL` again with the new one. The old one stops working at once.

The JSON it sends (the Worker depends on this shape; these values are made up):

```json
{
  "updated": "2026-10-29T20:30:00+07:00",
  "settings": {"limit": 5000000, "kitchen_approver": "Chef", "barfoh_approver": "Supervisor", "owner": "Owner"},
  "staff": ["An", "Bình", "Chi"],
  "suppliers": [{"name": "Demo Dairy", "supplies": "Cheese", "station": "Kitchen", "status": "Active",
                 "owner": "Chef", "order_days": "Mon, Thu", "cutoff": "18:00 the day before", "delivery": "Next morning", "min_order": ""}],
  "items": [{"supplier": "Demo Dairy", "en": "Burrata 125g", "vn": "Phô mai Burrata 125g", "unit": "pc",
             "unit_vn": "cái", "pack": "", "price": 95000, "vat": "+8% VAT", "par": null,
             "category": "Dairy", "notes": "", "code": ""}]
}
```

### Previews and full-site

Locked, like the kitchen: a Preview gets no database, no passwords and no vars
(`"previews": {}` in `wrangler.jsonc`), so its `/backoffice/` says signing in
isn't set up, and nothing on a Preview can reach Slack or the Order Sheet.

### On your own machine

`.dev.vars` (copied from `.dev.vars.example`) has the test password
`local-office-test` and `BACKOFFICE_DRY_RUN=1`. Run `npm run build`, then
`npx wrangler dev`, and sign in at `http://localhost:8787/backoffice/`. In a dry
run requests are kept in the local database but never posted: the page shows the
message instead. With no `ORDER_GUIDE_URL`, the form uses the fake Order Guide in
`worker/backoffice-sample.json` (made-up suppliers, items and prices; keep it
fake). Never set `BACKOFFICE_DRY_RUN` on the real site.

- Stop `wrangler dev` before `npm run build`: a build empties `dist/`, and
  `wrangler dev` can stop with an error when files vanish under it.
- To clear a local lockout:
  `npx wrangler d1 execute sol-dough --local --command "DELETE FROM backoffice_login_failures"`.
- The requests sent locally:
  `npx wrangler d1 execute sol-dough --local --command "SELECT ref, slack_status, supplier FROM backoffice_purchases ORDER BY id DESC LIMIT 10"`.

### The production smoke test

Once the secrets are set and the branch is merged (Workers Builds deploys it):

1. On a phone, open sol.pizza/backoffice/ and sign in with the staff password.
2. **Purchase request**: any supplier, one item, and the note **TEST — ignore**.
   Preview the message, then **Send to #supply**: the page says "Sent to #supply"
   with a ref.
3. In #supply: the 🛒 message, with the right people mentioned. React ❌ to it
   (cancelled), so nobody orders it.
4. **Recent requests**: it's there, "Sent to Slack".

### The data

- `backoffice_purchases`: each request: its ref (`SOL-YYMMDD-HHMM`, Hanoi time),
  the browser's request id (a retry never posts twice), who asked, the supplier,
  the station, when it's needed, the items, the note, the estimate, whether
  Arman was needed, the message and what Slack said. To look:
  `npx wrangler d1 execute sol-dough --remote --command "SELECT ref, created_at, requested_by, supplier, slack_status FROM backoffice_purchases ORDER BY id DESC LIMIT 20"`.
- `backoffice_guide`: the Order Guide's last good copy (one row).
- `backoffice_login_failures`: wrong passwords, for the 15-minute wait.
