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
import argparse, ast, json, os, re, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = r'[a-z0-9][a-z0-9/_.-]*\.(jpe?g|png|webp)'      # as build/gen.py checks it


def exif_orientation(seg):
    """The EXIF Orientation (1-8) in an APP1 segment, or 1."""
    if not seg.startswith(b'Exif\0\0'):
        return 1
    tiff = seg[6:]
    order = {b'II': '<', b'MM': '>'}.get(tiff[:2])
    if not order or len(tiff) < 8:
        return 1
    ifd = struct.unpack(order + 'I', tiff[4:8])[0]
    if ifd + 2 > len(tiff):
        return 1
    for n in range(struct.unpack(order + 'H', tiff[ifd:ifd + 2])[0]):
        e = ifd + 2 + 12 * n
        if e + 12 > len(tiff):
            break
        if struct.unpack(order + 'H', tiff[e:e + 2])[0] == 0x0112:
            return struct.unpack(order + 'H', tiff[e + 8:e + 10])[0]
    return 1


def jpeg_size(data):
    """(width, height, the ICC profile's bytes or b'', the EXIF orientation) of a JPEG."""
    i, icc, orientation = 2, b'', 1
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            raise ValueError('not a JPEG I can read (marker expected at byte %d)' % i)
        marker = data[i + 1]
        if marker == 0xFF:                       # fill bytes before a marker
            i += 1
            continue
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = struct.unpack('>H', data[i + 2:i + 4])[0]
        seg = data[i + 4:i + 2 + length]
        if marker == 0xE1:
            orientation = exif_orientation(seg) if orientation == 1 else orientation
        if marker == 0xE2 and seg.startswith(b'ICC_PROFILE\0'):
            icc += seg[14:]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack('>HH', seg[1:5])
            return w, h, icc, orientation
        i += 2 + length
    raise ValueError('no image size found in this JPEG')


def png_size(data):
    """(width, height, the ICC profile's bytes or b'', 1) of a PNG."""
    if data[12:16] != b'IHDR':
        raise ValueError('not a PNG I can read')
    w, h = struct.unpack('>II', data[16:24])
    icc, i = b'', 8
    while i + 8 <= len(data):
        n, kind = struct.unpack('>I', data[i:i + 4])[0], data[i + 4:i + 8]
        if kind == b'iCCP':
            chunk = data[i + 8:i + 8 + n]
            try:
                icc = zlib.decompress(chunk[chunk.index(b'\0') + 2:])
            except (ValueError, zlib.error):
                pass
            break
        if kind == b'IDAT':
            break
        i += 12 + n
    return w, h, icc, 1


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
    try:
        data = open(a.file, 'rb').read()
    except OSError as e:
        sys.exit('%s: %s' % (a.file, e.strerror))
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        read = png_size
    elif data[:3] == b'\xff\xd8\xff':
        read = jpeg_size
    else:
        sys.exit('%s: not a JPEG or PNG; export it as a JPEG (README.md, "Photographs")' % a.file)
    try:
        w, h, icc, orientation = read(data)
    except (ValueError, struct.error) as e:
        sys.exit('%s: %s; export it again as a JPEG' % (a.file, e))
    problems = []
    if orientation in (5, 6, 7, 8):
        w, h = h, w          # stored on its side, shown upright: Cloudflare turns it as the EXIF says
        print('  (turned: the entry has its size as it shows, %d x %d)' % (w, h), file=sys.stderr)
    if max(w, h) < 2400:
        problems.append('small: its long edge is %d px; 3,000 to 4,000 px keeps it sharp on big screens' % max(w, h))
    if len(data) > 25 * 1024 * 1024:
        problems.append('heavy: %.0f MB; export at quality 85-90 to stay under 25 MB' % (len(data) / 1048576))
    for name in ('Adobe RGB', 'ProPhoto', 'Display P3', 'P3 '):
        # an ICC v2 profile names itself in ASCII, a v4 one in UTF-16
        if name.encode() in icc or name.encode('utf-16-be') in icc:
            problems.append('colour: its profile is %s; export as sRGB, so it looks the same in every '
                            'browser and app' % name.strip())
    for sl in a.slot:
        spec = next((k for k in known if k[0] == sl), None)
        if not spec:
            problems.append('slot: no %r (python3 build/media_tool.py slots; an Eclipse edition\'s photo needs '
                            'no slot: it\'s the "image" in events-data.json)' % sl)
        elif sum(sl in p.get('slots', []) for p in media['photos']) >= spec[4]:
            problems.append('slot: %s already has its %d photo%s in build/media.json'
                            % (sl, spec[4], '' if spec[4] == 1 else 's'))
    key = a.key or re.sub(r'^[^a-z0-9]+', '', re.sub(r'[^a-z0-9/_.-]+', '-', os.path.basename(a.file).lower()))
    if not re.fullmatch(KEY, key):
        problems.append('key: %r won\'t do: lower-case letters, digits and / _ . - only, starting with a letter '
                        'or digit, ending .jpg, .jpeg or .png (--key 2026-11/room-ground-floor.jpg)' % key)
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
