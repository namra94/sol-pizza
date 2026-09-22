#!/usr/bin/env python3
"""Pack the site's few binary files (share-card PNGs) into build/assets.b64.json,
a text file that can travel through any text-only channel (the GitHub connector,
a chat message). gen.py unpacks it at build time. Run this after re-rendering
the share cards with og.js:   python3 build/pack_assets.py"""
import base64, json, os, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
files = sorted(glob.glob(os.path.join(HERE, 'og', 'png', '*.png'))) + \
        sorted(glob.glob(os.path.join(ROOT, 'src', 'jobs', 'og-*.png')))
m = {os.path.relpath(f, ROOT): base64.b64encode(open(f, 'rb').read()).decode() for f in files}
json.dump(m, open(os.path.join(HERE, 'assets.b64.json'), 'w'), indent=0)
print('packed', len(m), 'files')
