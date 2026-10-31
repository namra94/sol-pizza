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
asks for **items only** on a phone (what, how much, for which station and by
when), and the Worker posts it to Slack's **#supply** as a 📝 **PURCHASE
REQUEST**. Staff never pick a supplier, a brand or a price: management chooses
the supplier and the brand when they order.

In #supply:

1. **The station's approver** reacts to the 📝 request: ✅ approved, or ❌
   declined, with the reason in the thread. The message mentions the Kitchen
   approver for a Kitchen request, the Bar & FOH approver for Bar and FOH.
2. **Management places the order**: they choose the supplier and the brand, and
   post the 🛒 orders with the Order Sheet's Order helper, one per supplier, so
   one request can become several orders. Arman's ✅ rules apply to those 🛒
   orders, as they always have: over 5,000,000đ before VAT, or a supplier that
   isn't Active.
3. **Once the orders are posted**, someone reacts 🛒 on the 📝 request.

| On | Reaction | Means |
| --- | --- | --- |
| a 📝 request | ✅ | Approved by the station's approver |
| | ❌ | Declined: the reason is in the thread |
| | 🛒 | Ordered: its 🛒 orders are posted |
| a 🛒 order | ✅ 📦 🚚 ❌ 🗂️ | As before: approved, ordered on Zalo, received and checked, cancelled, filed |

The website never posts a 🛒 order, and a 📝 request never has a 🛒 in it (one
typed in is left out): in #supply a 🛒 is an order to a supplier, and the Order
desk agent reads it that way. For the same reason the 📝 message's labels never
change once it's live.

Where its data is:

- **The requests** are kept in D1 (`backoffice_requests`), in the kitchen's
  database `sol-dough` through the same `DOUGH_DB` binding, next to the dough
  log. The Worker makes its tables the first time it's used.
- **What the form suggests** comes from those requests: the names that asked
  before, and the items asked for at each station, most-asked first, each with
  the unit used most (never a note). Nothing is kept anywhere else, and nothing
  about suppliers, brands, prices or people is in this repo, which is public.
- **Who it mentions** in Slack: the Slack member ids in `wrangler.jsonc`
  (`vars`: `SLACK_APPROVER_KITCHEN`, `SLACK_APPROVER_BAR_FOH`). They aren't
  secrets. If an approver changes, change the id there (Slack → their profile →
  ⋮ → Copy member ID). Without an id, the message names the role as text
  ("Kitchen approver") and mentions no one.

### The two secrets

| Secret | What it is |
| --- | --- |
| `BACKOFFICE_PASSWORD` | The staff password |
| `SLACK_WEBHOOK_URL` | The Incoming Webhook into #supply (below) |

```
npx wrangler secret put BACKOFFICE_PASSWORD     # type the staff password when asked
npx wrangler secret put SLACK_WEBHOOK_URL       # paste the webhook's URL
```

Each one goes straight into Cloudflare: never into the repo, a chat or a
ticket. Without `BACKOFFICE_PASSWORD`, `/backoffice/` says signing in isn't set
up and lets no one in. Without `SLACK_WEBHOOK_URL`, requests are kept but marked
failed, and the sender sees why.

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

### Retiring the Order Sheet's web app

Before staff asked for items only, the form read the Order Sheet's suppliers,
items and prices through an Apps Script web app bound to the sheet, set up with
#15. Nothing reads it now. Once this is live:

1. `npx wrangler secret delete ORDER_GUIDE_URL`.
2. In the Order Sheet, open **Extensions** → **Apps Script** → **Deploy** →
   **Manage deployments**, and archive the web app.
3. Delete the code that was pasted from `tools/order-sheet.gs` (no longer in
   this repo; its history has it). If it was merged into another file, take out
   only its part.
4. **Project Settings** (the gear) → **Script properties**: delete `TOKEN`.

The Order Sheet itself, its Order helper and the 🛒 format stay as they are.

### Previews and full-site

Locked, like the kitchen: a Preview gets no database, no passwords and no vars
(`"previews": {}` in `wrangler.jsonc`), so its `/backoffice/` says signing in
isn't set up, and nothing on a Preview can reach Slack.

### On your own machine

`.dev.vars` (copied from `.dev.vars.example`) has the test password
`local-office-test` and `BACKOFFICE_DRY_RUN=1`. Run `npm run build`, then
`npx wrangler dev`, and sign in at `http://localhost:8787/backoffice/`. In a dry
run requests are kept in the local database but never posted: the page shows the
message instead. There's no sample data: the form suggests nothing until a few
dry-run requests have been sent, then their names and items. Never set
`BACKOFFICE_DRY_RUN` on the real site.

- Stop `wrangler dev` before `npm run build`: a build empties `dist/`, and
  `wrangler dev` can stop with an error when files vanish under it.
- To clear a local lockout:
  `npx wrangler d1 execute sol-dough --local --command "DELETE FROM backoffice_login_failures"`.
- The requests sent locally:
  `npx wrangler d1 execute sol-dough --local --command "SELECT ref, slack_status, station, requested_by FROM backoffice_requests ORDER BY id DESC LIMIT 10"`.

### The production smoke test

Once the branch is merged (Workers Builds deploys it):

1. On a phone, open sol.pizza/backoffice/ and sign in with the staff password.
2. **Purchase request**: any station, one item, and the note **TEST — ignore**.
   Preview the message, then **Send to #supply**: the page says "Sent to #supply"
   with a ref, `REQ-…`.
3. In #supply: the 📝 message, mentioning the station's approver. React ❌ to it
   (declined), so nobody orders it.
4. **Recent requests**: it's there, "Sent to Slack".

### The data

- `backoffice_requests`: each request: its ref (`REQ-YYMMDD-HHMM`, Hanoi time;
  `-2`, `-3`… for more in the same minute), the browser's request id (a retry
  never posts twice), who asked, the station, when it's needed, the items (name,
  quantity, unit, note), the note, the message and what Slack said. To look:
  `npx wrangler d1 execute sol-dough --remote --command "SELECT ref, created_at, requested_by, station, slack_status FROM backoffice_requests ORDER BY id DESC LIMIT 20"`.
- `backoffice_login_failures`: wrong passwords, for the 15-minute wait.
- Two tables from before staff asked for items only, left as they were. Nothing
  reads or writes them:
  - `backoffice_purchases`: the 🛒-format requests sent until then, each with
    its supplier. They aren't on Recent requests. To look:
    `npx wrangler d1 execute sol-dough --remote --command "SELECT ref, created_at, requested_by, supplier, slack_status FROM backoffice_purchases ORDER BY id DESC"`.
  - `backoffice_guide`: the Order Sheet's copy the form read then (one row).

  Once Arman is happy, drop them (D1's Time Travel, under "The log's data",
  rewinds the whole database if one is ever needed back):

  ```
  npx wrangler d1 execute sol-dough --remote --command "DROP TABLE IF EXISTS backoffice_guide"
  npx wrangler d1 execute sol-dough --remote --command "DROP TABLE IF EXISTS backoffice_purchases"
  ```
