# Deploying sol.pizza

The site is a Cloudflare Worker with static assets (`wrangler.jsonc`, Worker name
`sol-pizza`). Everything is generated from `build/gen.py`; nothing binary lives in
git — fonts come from npm, the share-card PNGs are unpacked from
`build/assets.b64.json`.

## Cloudflare Workers Builds (automatic on every push)

Workers → sol-pizza → Settings → Builds → connect this repository:

| Setting              | Value                              |
| -------------------- | ---------------------------------- |
| Production branch    | `main`                             |
| Build command        | `npm run build`                    |
| Deploy command       | `npx wrangler deploy`              |
| Root directory       | `/`                                |

The build image has Node 24 and Python 3.13, which is all the build needs.

## By hand

```
npm ci
npm run build          # writes ./dist
npx wrangler login     # once
npx wrangler deploy
```
