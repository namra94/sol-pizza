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
| Root directory       | `/`                                |

The build image has Node 24 and Python 3.13, which is all the build needs. Each
build shows up as a "Workers Builds: sol-pizza" check on the commit in GitHub.

## By hand

Only if Workers Builds is off; otherwise a push already deploys.

```
npm ci
npm run build          # writes ./dist
npx wrangler login     # once
npx wrangler deploy
```

## Rolling back

```
npx wrangler deployments list        # note the version id that was live before
npx wrangler rollback <version-id>
```
