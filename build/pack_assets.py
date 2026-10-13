#!/usr/bin/env python3
"""Pack the site's few binary files (the share-card PNGs and the BN Arora font)
into build/assets.b64.json, a text file that can travel through any text-only
channel (the GitHub connector, a chat message). gen.py unpacks it at build time.
Run this after re-rendering the share cards (npm run og), or after putting a new
BN Arora file at build/brand/BNArora-Regular.woff2:   python3 build/pack_assets.py
With Pillow installed, the share cards in build/og/png/ are reduced to 96 colours
first (they're flat colour, so they look the same at a third of the size), as the
build does."""
import base64, glob, io, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
files = sorted(glob.glob(os.path.join(HERE, 'og', 'png', '*.png'))) + \
        sorted(glob.glob(os.path.join(ROOT, 'src', 'jobs', 'og-*.png'))) + \
        sorted(glob.glob(os.path.join(HERE, 'brand', '*.woff2')))       # BN Arora (licensed for web use)
try:
    from PIL import Image
except ImportError:
    Image = None


def data(f):
    raw = open(f, 'rb').read()
    if Image and os.path.dirname(f) == os.path.join(HERE, 'og', 'png'):
        out = io.BytesIO()
        Image.open(io.BytesIO(raw)).convert('RGB').quantize(colors=96, method=Image.Quantize.MEDIANCUT) \
            .save(out, format='PNG', optimize=True)
        raw = out.getvalue()
    return raw


# Keys use / on every OS: the Linux build machine unpacks them.
m = {os.path.relpath(f, ROOT).replace(os.sep, '/'): base64.b64encode(data(f)).decode() for f in files}
with open(os.path.join(HERE, 'assets.b64.json'), 'w', newline='\n') as out:
    json.dump(m, out, indent=0)
print('packed', len(m), 'files' + ('' if Image else ' (no Pillow: the share cards at full size)'))
