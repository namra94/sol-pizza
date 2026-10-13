#!/usr/bin/env python3
"""Photographs for sol.pizza: what build/media.json needs, from the files themselves.

  python3 build/media_tool.py slots
      where photos go: each slot, what to shoot, its shapes, how many, and how many it has

  python3 build/media_tool.py photo.jpg [--key 2026-11/room.jpg] [--slot home-hero ...]
      reads the photo's size, checks it's fit for the site (big enough, sRGB), and prints
      its entry for build/media.json, to paste in and finish: the alt text in English
      and Vietnamese, the credit, and the focus (the point to keep when it's cropped)

Then upload the file to the sol-media bucket under the same key (README.md,
"Photographs"). Standard library only: nothing to install.
"""
import argparse, ast, json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def jpeg_size(data):
    """(width, height, the ICC profile's bytes or b'') of a JPEG."""
    i, icc = 2, b''
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            raise ValueError('not a JPEG I can read (marker expected at %d)' % i)
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = struct.unpack('>H', data[i + 2:i + 4])[0]
        seg = data[i + 4:i + 2 + length]
        if marker == 0xE2 and seg.startswith(b'ICC_PROFILE\0'):
            icc += seg[14:]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack('>HH', seg[1:5])
            return w, h, icc
        i += 2 + length
    raise ValueError('no image size found in this JPEG')


def png_size(data):
    if data[12:16] != b'IHDR':
        raise ValueError('not a PNG I can read')
    w, h = struct.unpack('>II', data[16:24])
    return w, h, b''


def slots():
    """The slots, read from build/gen.py's SLOTS (so this tool never disagrees with the build)."""
    tree = ast.parse(open(os.path.join(HERE, 'gen.py'), encoding='utf-8').read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', '') == 'SLOTS' for t in node.targets):
            return [(name, what, wide, phone, n) for name, (what, wide, phone, _, n)
                    in ast.literal_eval(node.value).items()]
    raise SystemExit('build/gen.py has no SLOTS')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('file', help='a photo (JPEG or PNG), or "slots"')
    ap.add_argument('--key', help='its name in the bucket, e.g. 2026-11/room-ground-floor.jpg')
    ap.add_argument('--slot', action='append', default=[], help='where it goes (repeat for several)')
    a = ap.parse_args()
    media = json.load(open(os.path.join(HERE, 'media.json'), encoding='utf-8'))
    known = slots()
    if a.file == 'slots':
        for name, what, wide, phone, n in known:
            have = sum(name in p.get('slots', []) for p in media['photos'])
            print('%-20s %d of %d  %d:%d wide, %d:%d on a phone\n%20s %s'
                  % (name, have, n, wide[0], wide[1], phone[0], phone[1], '', what))
        return
    data = open(a.file, 'rb').read()
    w, h, icc = (png_size if data[:8] == b'\x89PNG\r\n\x1a\n' else jpeg_size)(data)
    problems = []
    if max(w, h) < 2400:
        problems.append('small: its long edge is %d px; 3,000 to 4,000 px keeps it sharp on big screens' % max(w, h))
    if len(data) > 25 * 1024 * 1024:
        problems.append('heavy: %.0f MB; export at quality 85-90 to stay under 25 MB' % (len(data) / 1048576))
    for name in (b'Adobe RGB', b'ProPhoto', b'Display P3', b'P3 '):
        if name in icc:
            problems.append('colour: its profile is %s; export as sRGB, or its colours will shift'
                            % name.decode().strip())
    for sl in a.slot:
        if sl not in [k[0] for k in known]:
            problems.append('slot: no %r (python3 build/media_tool.py slots)' % sl)
    key = a.key or re.sub(r'[^a-z0-9/_.-]+', '-', os.path.basename(a.file).lower())
    if any(p.get('key') == key for p in media['photos']):
        problems.append('key: %s is already in build/media.json' % key)
    entry = {'key': key, 'width': w, 'height': h, 'alt_en': '', 'alt_vi': '', 'credit': '',
             'focus': [0.5, 0.5], 'slots': a.slot}
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    print('\nAdd it to "photos" in build/media.json, fill in alt_en, alt_vi and credit, set focus, and upload\n'
          'the file to the sol-media bucket as %s.' % key, file=sys.stderr)
    for pr in problems:
        print('  ! ' + pr, file=sys.stderr)
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
