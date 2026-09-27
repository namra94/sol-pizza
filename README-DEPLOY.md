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
`npm run build` builds the **public** site (the home page and the jobs section;
see "Build modes" in `build/README.md`), except on the `full-site` branch below,
and every build log starts with the mode it built.

A push to any other branch runs a **preview build**: the same build, then
`npx wrangler preview`, which puts that branch on its own Preview URL (posted on
the pull request) and leaves sol.pizza alone. The URL is the branch name, with
`/` as `-`, then `-sol-pizza.polarized-jar.workers.dev`: the branch `public-cut`
is at `https://public-cut-sol-pizza.polarized-jar.workers.dev`. A pull request's
preview shows the public site, as `main` would deploy it. It needs the
`"previews": {}` block in `wrangler.jsonc`; without it every preview build fails.
Preview URLs are public unless Cloudflare Access protects them.

## full-site: the whole site on a Preview URL

The pages that aren't public yet (`HIDDEN` in `build/gen.py`) stay reviewable at
one stable link:

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

Don't roll back to a version deployed before the public/full split (the commit
"Public site: home and jobs only; full site on full-site"): those versions serve
the whole site, About, Menu and Booking included, with 301s into them.
