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
for `/dough/*` and `/api/*`) reads the password from the secret `DOUGH_PASSWORD`
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
It rewinds everything logged since, so download the CSV first.
