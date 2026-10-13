#!/usr/bin/env python3
"""
Build the sol.pizza static site: the "Printed menu" design.

    npm run build          (= python3 build/gen.py; run `npm ci` once first, for the fonts)
    npm run build:full     (= python3 build/gen.py --full: the whole site, see HIDDEN)

Writes plain, readable HTML into dist/, which the sol-pizza Worker serves.
Every page is generated here. Each line of copy appears twice, English then
Vietnamese, so the two never drift apart, and each guest page is written once in
each language: English at /…, Vietnamese at /vi/…. The menu lives in
build/menu-data.json.

  build/design/        tokens.css + printed-menu.css (the design), site.css (what
                       this repo adds), site.js (header, EN · VI, cookie banner,
                       analytics, events); kitchen/ the kitchen pages' frozen shell
  build/assets/        logo, illustrations and the sun pattern (SVG)
  build/menu-data.json food, wine and bar: names as the kitchen and bar write them
  src/                 role pages and privacy notice (re-wrapped here, copy
                       untouched), _redirects, favicon.svg, pixel.js
"""
import os, re, sys, json, stat, shutil, hashlib, subprocess, base64, argparse, html as _html
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from urllib.parse import quote, unquote, urljoin, urlsplit

HERE   = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.dirname(HERE)
DIST   = os.path.join(ROOT, 'dist')
SRC    = os.path.join(ROOT, 'src')
DESIGN = os.path.join(HERE, 'design')
ASSETS = os.path.join(HERE, 'assets')

SITE   = 'https://sol.pizza'
GA_ID  = 'G-SLBWDVH550'
FB_PIX = '856214124247013'
TODAY  = date.today().isoformat()

# --------------------------------------------------------------------------
# NOT PUBLIC: EDIT THIS to take a page down
#   Empty: every page is public and sol.pizza is the whole site. To take a page
#   down, add its section's key ('menu', 'about', 'visit', 'booking', 'events' or
#   'private-dining', as in SECTIONS; 'menu' takes Food, Wine and Bar). It stays in
#   the repo and on the full-site preview, but the public build leaves it out, in
#   both languages: no page in dist/, no share card, tab, footer link, home or 404
#   button, sitemap entry or structured data, and its addresses (and the old ones in
#   src/_redirects that lead to it) go to the home page with a 302. While any page
#   is hidden the header has a Work with us tab. To put it back, delete the key.
#   Either way, open a pull request, check its Preview URL and merge.
# --------------------------------------------------------------------------
HIDDEN = []

# Build mode. Public, the default: npm run build, and Workers Builds on main and
# on every other branch (pull request previews). Full, the whole site whatever
# HIDDEN says, every section still waiting for content (gate()) shown with a
# "Content needed" marker, and noindex so a preview stays out of search:
# npm run build:full (--full), and Workers Builds on the full-site branch and on
# the full/… branches (.github/workflows/full-preview.yml copies every claude/…
# branch to full/claude/…, so a pull request has a full preview too). --public
# overrides the branch: npm run deploy uses it, so a full build can't reach sol.pizza.
_cli = argparse.ArgumentParser(description='Build sol.pizza into dist/.')
_mode = _cli.add_mutually_exclusive_group()
_mode.add_argument('--full', action='store_true', help='the whole site, noindex (the full-site preview)')
_mode.add_argument('--public', action='store_true', help='the public site, even on the full-site branch')
ARGS = _cli.parse_args()
CI_BRANCH = os.environ.get('WORKERS_CI_BRANCH', '')
FULL = ARGS.full or (not ARGS.public and (CI_BRANCH == 'full-site' or CI_BRANCH.startswith('full/')))
HIDE = set() if FULL else set(HIDDEN)
if FULL:
    print('Build mode: FULL (%s): every page, noindex'
          % ('--full' if ARGS.full else 'WORKERS_CI_BRANCH=' + CI_BRANCH))
else:
    print('Build mode: PUBLIC: not yet public: %s' % (', '.join(HIDDEN) or 'nothing, the whole site'))


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


MENU = json.loads(read(os.path.join(HERE, 'menu-data.json')))
SUN_SPRITE = read(os.path.join(ASSETS, 'suns-sprite.svg')).strip()

# --------------------------------------------------------------------------
# fonts
#   Two typefaces (build/design/tokens.css): a display face for headings, a
#   serif for everything else (small labels are the serif in capitals).
#   Body text: EB Garamond in both languages (decided 24 Sep 2026; Gryphius MVB
#   read badly on screen). Nothing uses Gryphius MVB.
#   Headings: BN Arora on English pages (licensed for web use, confirmed 24 Sep
#   2026). Self-hosted: the file travels in build/assets.b64.json and is served
#   at BN_ARORA_URL. It has no Vietnamese letters, so Vietnamese headings use
#   Philosopher (tokens.css).
#   Adobe Fonts: Sol's web project, kit umo0non, linked on every page for Plunct,
#   the hand-written phrase (.hand) on English pages. Adobe Fonts can't be
#   self-hosted: never download, commit or deploy those files. The kit's CSS is
#   loaded without blocking the first paint.
#   Free faces (always loaded; they carry every Vietnamese letter): npm @fontsource.
# --------------------------------------------------------------------------
TYPEKIT_KIT  = 'https://use.typekit.net/umo0non.css'
BRAND_FONTS  = 'display'           # the brand faces switched on, see tokens.css
BN_ARORA_SRC = os.path.join(HERE, 'brand', 'BNArora-Regular.woff2')   # unpacked from assets.b64.json
BN_ARORA_URL = '/assets/fonts/bn-arora-400-normal.woff2'
FONT_PLAN = [
    # (npm package under @fontsource, CSS family, [(weight, style)])
    ('philosopher', 'Philosopher', [(400, 'normal')]),
    ('eb-garamond',  'EB Garamond', [(400, 'normal'), (400, 'italic'),
                                     (600, 'normal')]),   # 600: the footer column headings (printed-menu.css)
]
FONT_SUBSETS = ['latin', 'latin-ext', 'vietnamese']

# --------------------------------------------------------------------------
# site-wide facts: EDIT THESE, they appear on every page
# --------------------------------------------------------------------------
ADDRESS_EN = 'No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi'
ADDRESS_VI = 'Số 7, Ngõ 88 Quảng An, Tây Hồ, Hà Nội'
PHONE      = '+84 866 161 600'
PHONE_TEL  = 'tel:+84866161600'
EMAIL      = 'hello@sol.pizza'
MAPS_QUERY = 'Sol+Hanoi%2C+7+Ng%C3%B5+88+Qu%E1%BA%A3ng+An%2C+T%C3%A2y+H%E1%BB%93%2C+H%C3%A0+N%E1%BB%99i'
MAPS_URL   = 'https://www.google.com/maps/search/?api=1&amp;query=' + MAPS_QUERY
# Directions (the phone bar): Google Maps, from wherever the guest is to us
DIRECTIONS_URL = 'https://www.google.com/maps/dir/?api=1&amp;destination=' + MAPS_QUERY
INSTAGRAM  = 'https://www.instagram.com/solhanoi/'
INSTA_HANDLE = '@solhanoi'
COMPANY_EN = 'Aurelian Company Limited'
COMPANY_VI = 'Công ty TNHH Aurelian'

# ResDiary: paste the widget URL here (ResDiary > Promote > Widget configurator >
# Embed Code) and rebuild. The Booking page's booking box then shows the widget.
RESDIARY_URL = ''
# The widget in Vietnamese, if ResDiary gives a separate address for it (the Widget
# configurator, Vietnamese selected); empty: Vietnamese pages use RESDIARY_URL too.
RESDIARY_URL_VI = ''
# Until online booking is live, the phone number in the booking box is text to copy,
# not a button that opens another app (Linh, 23 Sep), and the phone bar has no Call
# button. Both follow RESDIARY_URL: once it is set, contact is a tap away.
CONTACT_LIVE = bool(RESDIARY_URL)
# Does the ResDiary widget take payments (deposits) inside its frame? Then the pages
# let that frame use the browser's payment feature (Permissions-Policy in _headers).
RESDIARY_PAYMENTS = False
# Zalo and WhatsApp (CONTENT-NEEDED.md), once we have the numbers: Zalo as Zalo shows
# it ('0866161600'), WhatsApp in international form without the + ('84866161600').
# With online booking live they join the phone and email on the booking page, and Zalo
# is the phone bar's button on Vietnamese pages (Call on English ones).
ZALO     = ''
WHATSAPP = ''
assert re.fullmatch(r'(0\d{9})?', ZALO), "ZALO: the number as Zalo shows it, ten digits from 0, or ''"
assert re.fullmatch(r'(84\d{9})?', WHATSAPP), "WHATSAPP: 84 then nine digits, no + or spaces, or ''"
assert all(re.fullmatch(r'(https://[^\s"<>]+)?', u) for u in (RESDIARY_URL, RESDIARY_URL_VI)), \
    "RESDIARY_URL: the widget's https:// address, or ''"

# Where the enquiry forms (groups and private dining, opening week) and the newsletter
# sign-up send their email: an inbox the team reads every day.
ENQUIRIES = EMAIL
# Sol elsewhere, after Instagram, in the footer and the structured data, as we get them
# (CONTENT-NEEDED.md): (name, address), such as ('Facebook', 'https://www.facebook.com/…').
SOCIAL = []
# The company's details for the footer's last line (CONTENT-NEEDED.md): the tax code
# (mã số thuế), and the registered address if it isn't the restaurant's, as
# ('English', 'Tiếng Việt'). Until the tax code is set the line has the company's name.
TAX_CODE = ''
REGISTERED_ADDRESS = None
# Who answers the press, on /press/ (CONTENT-NEEDED.md): ('Name', 'email'). Until then
# the page gives hello@sol.pizza.
PRESS_CONTACT = None
# The map pin (CONTENT-NEEDED.md): (latitude, longitude) of the door on Quang An, for the
# structured data search engines read. None until it's confirmed on the map.
GEO = None
# How guests can pay (CONTENT-NEEDED.md, "Payment methods"): ('English', 'Tiếng Việt'),
# e.g. ('Cash, Visa, Mastercard, bank transfer and MoMo', 'Tiền mặt, Visa, Mastercard,
# chuyển khoản và MoMo'). Visit's "Paying" answer and the structured data. Empty until
# we know.
PAYMENT_ACCEPTED = ('', '')
# Google Search Console's HTML-tag code, if the site is verified that way rather than by
# DNS (LAUNCH-CHECKLIST.md): the content="…" value. Empty: no tag.
GOOGLE_VERIFICATION = ''
assert GEO is None or (len(GEO) == 2 and 20.9 < GEO[0] < 21.2 and 105.7 < GEO[1] < 106), \
    'GEO: (latitude, longitude) in Hanoi, e.g. (21.06, 105.82)'
assert len(PAYMENT_ACCEPTED) == 2 and bool(PAYMENT_ACCEPTED[0]) == bool(PAYMENT_ACCEPTED[1]), \
    'PAYMENT_ACCEPTED: (\'English\', \'Tiếng Việt\'), both or neither'

# --------------------------------------------------------------------------
# opening and hours: EDIT THESE
#   SITE_STATE: 'preopening' until the day we open, then 'open'. It switches the
#   home page's eyebrow, facts row and lead, the booking and Visit lines, the meta
#   descriptions and the opening hours in the structured data, and takes every
#   "opening soon" line off the site.
#   OPENING_DATE: the day the doors first open, 'YYYY-MM-DD', once it is set (None
#   until then). From that day's opening time (Hanoi time) the pages switch to open
#   by themselves, in the browser, before anyone rebuilds; then set SITE_STATE =
#   'open' so the descriptions and structured data follow (LAUNCH-CHECKLIST.md).
#   HOURS: the regular week, everywhere hours appear (footer, menu sheet, home, Visit,
#   descriptions, structured data). days: 0 is Monday. Holidays and Tết go in
#   build/announcements.json.
# --------------------------------------------------------------------------
SITE_STATE   = 'preopening'
OPENING_DATE = None
HOURS = {
    'days': [1, 2, 3, 4, 5, 6],     # Tuesday to Sunday
    'opens': '17:00',
    'closes': '23:00',
    'last_orders': None,            # 'HH:MM' once the kitchen sets it (CONTENT-NEEDED.md)
}
assert SITE_STATE in ('preopening', 'open'), "SITE_STATE is 'preopening' or 'open'"
assert OPENING_DATE is None or re.fullmatch(r'\d{4}-\d{2}-\d{2}', OPENING_DATE), "OPENING_DATE is 'YYYY-MM-DD' or None"

# The wine lead and the home and wine meta descriptions spell the wine counts
# out in words ("Thirty wines", "26 wines by the glass"). They're right for the
# list as it is. If the list changes, the build stops here: update those lines
# (search this file for "Thirty" and "26 wines"), then PROSE_WINE_COUNTS.
PROSE_WINE_COUNTS = (30, 26)


# --------------------------------------------------------------------------
# bilingual helpers
# --------------------------------------------------------------------------
def t(en, vi):
    """One line in both languages. A guest page is written once per language and keeps
    its own side (localise()); the kitchen's pages carry both, and kitchen.css shows the
    one <html lang> asks for."""
    if en == vi:
        return en
    return '<span data-l="en" lang="en">%s</span><span data-l="vi" lang="vi">%s</span>' % (en, vi)


def label(en, vi):
    """An aria-label in both languages: localise() keeps the page's; on the kitchen's
    pages kitchen.js swaps it with the language."""
    return 'aria-label="%s" data-aria-en="%s" data-aria-vi="%s"' % (en, en, vi)


def esc(s):
    """Text from menu-data.json, made safe for HTML (S&M, Proper G&T)."""
    return _html.escape(s, quote=False)


def esc_attr(s):
    """Text for a double-quoted attribute (and the <title> that repeats it)."""
    return _html.escape(s, quote=True)


def nbsp(markup):
    """Tây Hồ and Sol Pizza never split across two lines in the visible text."""
    return (markup.replace('Tây Hồ', 'Tây&nbsp;Hồ').replace('T&acirc;y H&#7891;', 'T&acirc;y&nbsp;H&#7891;')
            .replace('Sol Pizza', 'Sol&nbsp;Pizza'))


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def sun(n):
    return '<svg class="sun" aria-hidden="true" focusable="false"><use href="#sun-%d"/></svg>' % n


def wine_counts():
    wines = [w for s in MENU['wine']['sections'] for w in s['items']]
    return len(wines), sum('glass' in w['marks'] for w in wines)


WINES_TOTAL, WINES_GLASS = wine_counts()
if (WINES_TOTAL, WINES_GLASS) != PROSE_WINE_COUNTS:
    raise SystemExit(
        'build/menu-data.json now has %d wines, %d by the glass. Update the wine lead and the '
        'home and wine meta descriptions in build/gen.py (search for "Thirty" and "26 wines"), '
        'then set PROSE_WINE_COUNTS = (%d, %d).'
        % (WINES_TOTAL, WINES_GLASS, WINES_TOTAL, WINES_GLASS))

# lines that repeat across pages
BOOK       = t('Book a table', 'Đặt bàn')
BOOK_SHORT = t('Book', 'Đặt bàn')
INSTA_TEXT = t('@solhanoi on Instagram', '@solhanoi trên Instagram')
INSTA_LINK = '<a href="%s">%s</a>' % (INSTAGRAM, INSTA_TEXT)
JOBS_TAB   = t('Work with us', 'Tuyển dụng')
SEE_ROLES  = t('See open roles', 'Xem vị trí tuyển dụng')
MAPS_LINK_TEXT = t('Open in Google Maps', 'Mở trong Google Maps')
DIRECTIONS = t('Directions', 'Chỉ đường')
WINE_TAB   = t('%d wines, %d by the glass' % (WINES_TOTAL, WINES_GLASS),
               '%d loại vang, %d loại theo ly' % (WINES_TOTAL, WINES_GLASS))


# --------------------------------------------------------------------------
# hours, in both languages, from HOURS
# --------------------------------------------------------------------------
EN_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
VI_DAYS = ['thứ Hai', 'thứ Ba', 'thứ Tư', 'thứ Năm', 'thứ Sáu', 'thứ Bảy', 'Chủ nhật']
EN_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
             'September', 'October', 'November', 'December']
def en_date(d, short=False):
    """Sunday 4 October, or Sun 4 Oct."""
    if short:
        return '%s %d %s' % (EN_DAYS[d.weekday()][:3], d.day, EN_MONTHS[d.month - 1][:3])
    return '%s %d %s' % (EN_DAYS[d.weekday()], d.day, EN_MONTHS[d.month - 1])


def vi_date(d, year=False):
    """Chủ nhật 04/10, or Chủ nhật 04/10/2026."""
    return '%s %02d/%02d%s' % (VI_DAYS[d.weekday()], d.day, d.month, '/%d' % d.year if year else '')


EN_DAYS_SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
VI_DAYS_CAP = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
VI_DAYS_SHORT = VI_DAYS_CAP[:6] + ['CN']
SCHEMA_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def day_runs(days):
    """Weekdays in consecutive runs: [1, 2, 3, 5] is [(1, 3), (5, 5)]."""
    runs = []
    for d in sorted(days):
        if runs and d == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], d)
        else:
            runs.append((d, d))
    return runs


def en_time(hhmm):
    """17:00 is 5pm, 17:30 is 5.30pm."""
    h, m = (int(x) for x in hhmm.split(':'))
    return '%d%s%s' % (h % 12 or 12, '.%02d' % m if m else '', 'am' if h < 12 else 'pm')


def en_days(days, short=False):
    """Tuesday to Sunday, or Tue–Sun."""
    names = EN_DAYS_SHORT if short else EN_DAYS
    return ', '.join(names[a] if a == b else '%s%s%s' % (names[a], '–' if short else ' to ', names[b])
                     for a, b in day_runs(days))


def vi_days(days, short=False):
    """Thứ Ba đến Chủ Nhật, or Thứ Ba – CN."""
    names = VI_DAYS_SHORT if short else VI_DAYS_CAP
    return ', '.join(names[a] if a == b else '%s%s%s' % (names[a], ' – ' if short else ' đến ', names[b])
                     for a, b in day_runs(days))


def en_list(items):
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


CLOSED_DAYS = [d for d in range(7) if d not in HOURS['days']]
HOURS_EN = '%s–%s' % (en_time(HOURS['opens']), en_time(HOURS['closes']))         # 5pm–11pm
HOURS_VI = '%s – %s' % (HOURS['opens'], HOURS['closes'])                          # 17:00 – 23:00
HOURS_SPAN = t(HOURS_EN, HOURS_VI)
HOURS_DAYS = t(en_days(HOURS['days']), vi_days(HOURS['days']))                   # Tuesday to Sunday
HOURS_TAB  = t('%s, %s' % (en_days(HOURS['days'], True), HOURS_EN),
               '%s, %s' % (vi_days(HOURS['days'], True), HOURS_VI))              # Tue–Sun, 5pm–11pm
HOURS_CLOSED = t('Closed %s' % en_list([EN_DAYS[d] + 's' for d in CLOSED_DAYS]),
                 'Nghỉ %s' % ' và '.join(VI_DAYS[d] for d in CLOSED_DAYS)) if CLOSED_DAYS else ''
HOURS_PLAIN = ('%s, %s' % (en_days(HOURS['days']), HOURS_EN),                     # for descriptions
               '%s, %s' % (vi_days(HOURS['days']), HOURS_VI))
LAST_ORDERS = t('Last orders %s' % en_time(HOURS['last_orders']),
                'Nhận gọi món đến %s' % HOURS['last_orders']) if HOURS['last_orders'] else ''


# --------------------------------------------------------------------------
# opening day
# --------------------------------------------------------------------------
# The instant the doors open, Hanoi time: OPENING_DATE at the opening hour.
OPENING_AT = '%sT%s:00+07:00' % (OPENING_DATE, HOURS['opens']) if OPENING_DATE else None
OPENING_DAY = date.fromisoformat(OPENING_DATE) if OPENING_DATE else None


def by_state(pre, opn, tag='span'):
    """Copy that changes when Sol opens: pre while SITE_STATE is 'preopening', opn once
    it is 'open'. With an OPENING_DATE the page carries both and the head script swaps
    them in the browser from the opening instant (html.is-open), so the site is right on
    the day before anyone rebuilds. Either side may be '' (nothing)."""
    if SITE_STATE == 'open':
        return opn
    if not OPENING_DATE:
        return pre
    return ''.join('<%s class="%s">%s</%s>' % (tag, cls, s, tag)
                   for cls, s in (('when-pre', pre), ('when-open', opn)) if s)


# --------------------------------------------------------------------------
# content still to come
# --------------------------------------------------------------------------
# Every section waiting for content goes through gate(): the public build leaves it
# out, the full build (full-site and the full/… previews) shows it with a "Content
# needed" marker. Each key is listed in CONTENT-NEEDED.md, which says what is needed,
# where it goes, in what form and who supplies it; the build stops if one isn't.
GATES = {}


def gate(key, what, full_html, public_html='', tag='div'):
    """A section that can't be public yet. key: its entry in CONTENT-NEEDED.md; what:
    one line on what is missing (English, for the reviewer); full_html: the section as
    it will look, with placeholders; public_html: what the public build shows meanwhile."""
    GATES[key] = what
    if not FULL:
        return public_html
    inner = 'span' if tag == 'span' else 'p'         # inside a line of text, the label is inline too
    return ('<%s class="gated" data-gate="%s"><%s class="gated-label">%s <code>%s</code>: %s</%s>%s</%s>'
            % (tag, key, inner, t('Content needed', 'Cần nội dung'), key, esc(what), inner, full_html, tag))


# --------------------------------------------------------------------------
# sections and tabs
# --------------------------------------------------------------------------
# The guest sections, by the key HIDDEN takes, and their addresses.
SECTIONS = {
    'menu': '/menu/',                       # Food, with Wine and Bar under it
    'about': '/about/',
    'events': '/events/',
    'private-dining': '/private-dining/',
    'visit': '/visit-us/',                  # not /visit/: browsers cache its old 301 to /booking/
    'booking': '/booking/',
}
# The sections this build has pages for. A tab whose page doesn't exist yet stays
# out of the header, the nav sheet and the footer.
BUILT = {'menu', 'about', 'events', 'private-dining', 'visit', 'booking'}
# Whole pages waiting for their content or the lawyer's approval (CONTENT-NEEDED.md):
# path: (key, what's missing). They're built every time, so a mistake in one still
# stops the build, and the full build shows them with a "Content needed" label; the
# public build leaves them out like a HIDDEN page (no file, link, sitemap entry or
# share card). To make one public, delete its line. An event's page waits by itself
# until its details are in build/events-data.json (EVENTS below).
WAITING = {
    '/gift-cards/': ('gift-cards', 'gift card values, how long a card lasts, and how to buy one'),
    '/privacy/guests/': ('legal-guest-privacy', 'the lawyer’s approval of the guest privacy notice, with the '
                                                'retention periods'),
    '/accessibility/': ('legal-accessibility', 'the lawyer’s approval of the accessibility statement, with the '
                                               'building’s access facts'),
}
# The header's tabs, the nav sheet's and the footer's: (key, href, name). Menu keeps
# its Food / Wine / Bar sub-tabs (MENU_TABS). Booking has no tab: the Book button is on
# every page. The public build shows the public ones, plus Work with us while anything
# is HIDDEN (shown_tabs()).
NAV_TABS = [('menu', '/menu/', t('Menu', 'Thực đơn')),
            ('about', '/about/', t('About', 'Giới thiệu')),
            ('events', '/events/', t('Events', 'Sự kiện')),
            ('private-dining', '/private-dining/', t('Private dining', 'Tiệc riêng')),
            ('visit', '/visit-us/', t('Visit', 'Ghé thăm'))]
MENU_TABS = [  # (key, href, name, descriptor)
    ('food', '/menu/',      t('Food', 'Món ăn'),   t('Pizza, pasta and small plates', 'Pizza, mì Ý và món khai vị')),
    ('wine', '/menu/wine/', t('Wine', 'Vang'),     WINE_TAB),
    ('bar',  '/menu/bar/',  t('Bar', 'Quầy bar'),  t('Cocktails, beer and sake', 'Cocktail, bia và sake')),
]
assert set(HIDDEN) <= set(SECTIONS), 'HIDDEN: use the keys of SECTIONS'

# Every page under a hidden section's address is hidden, in both languages: /menu/
# hides /menu/wine/ and /menu/bar/, and /vi/menu/ with them.
HIDDEN_PATHS = [SECTIONS[k] for k in SECTIONS if k in HIDE]


def live(key):
    """Is this section's page in this build and public? (The full build: every page it has.)"""
    return key in BUILT and key not in HIDE


def hidden(url):
    """Does this address (a path or a sol.pizza URL, English or /vi/) lead to a page that
    isn't public yet (HIDDEN, or WAITING for its content)?"""
    path = re.sub(r'^/vi(?=/|$)', '', urlsplit(url).path or '/') or '/'
    if not FULL and any(path in (w, w.rstrip('/')) for w in WAITING):
        return True
    return hidden_section(path)


def hidden_section(url):
    """Is this address under a section HIDDEN takes down (not one still WAITING, which
    was never public and has no address to send anywhere)?"""
    path = re.sub(r'^/vi(?=/|$)', '', urlsplit(url).path or '/') or '/'
    return any(path == p.rstrip('/') or path.startswith(p) for p in HIDDEN_PATHS)


def shown_tabs():
    """The tabs in the header and the nav sheet: the public ones, plus Work with us while
    any page is hidden (the jobs section is most of the public site then)."""
    return [tab for tab in NAV_TABS if live(tab[0])] + ([('jobs', '/jobs/', JOBS_TAB)] if HIDE else [])


def buttons(options):
    """The first two options whose page is public, as a red button and an outline one.
    options: (SECTIONS key, or None for a page that is always public, href, name)."""
    shown = [(href, name) for key, href, name in options if key is None or live(key)][:2]
    return ''.join('<a class="btn %s" href="%s"%s>%s</a>'
                   % (cls, href, ' data-track="book_click"' if href.startswith('/booking/') else '', name)
                   for cls, (href, name) in zip(('btn-red', 'btn-outline'), shown))


# --------------------------------------------------------------------------
# events: build/events-data.json (Eclipse, Sol's pop-up series)
# --------------------------------------------------------------------------
EVENTS_DATA = json.loads(read(os.path.join(HERE, 'events-data.json')))
EV_SERIES = t('Eclipse is Sol’s pop-up series.', 'Eclipse là chuỗi sự kiện pop-up của Sol.')
ORDINALS = [('First', 'nhất'), ('Second', 'hai'), ('Third', 'ba'), ('Fourth', 'tư'), ('Fifth', 'năm'),
            ('Sixth', 'sáu'), ('Seventh', 'bảy'), ('Eighth', 'tám'), ('Ninth', 'chín'), ('Tenth', 'mười')]


def _events():
    """The editions, oldest first, each checked and given: until (the end of its last
    night, Hanoi time), path, and ready (it has its details, so its page is public)."""
    out, seen = [], set()
    for e in EVENTS_DATA['editions']:
        sl = e.get('slug', '')
        assert re.fullmatch(r'[a-z0-9-]+', sl) and sl not in seen, 'events-data.json: each slug unique, a-z 0-9 -'
        seen.add(sl)
        assert isinstance(e.get('edition'), int) and e['edition'] > 0, 'events-data.json: %s: edition is 1, 2…' % sl
        days = [date.fromisoformat(d) for d in e.get('dates', [])]
        assert days and days == sorted(days), 'events-data.json: %s: dates, YYYY-MM-DD, in order' % sl
        assert not e['times'] or re.fullmatch(r'\d\d:\d\d–\d\d:\d\d', e['times']), \
            'events-data.json: %s: times is HH:MM–HH:MM (with an en dash) or ""' % sl
        assert bool(e['summary_en']) == bool(e['summary_vi']), 'events-data.json: %s: summary in both languages' % sl
        assert len(e['menu_en']) == len(e['menu_vi']), 'events-data.json: %s: menu_en and menu_vi, as many each' % sl
        assert all(c.get('name') and c.get('line_en') and c.get('line_vi') for c in e['chefs']), \
            'events-data.json: %s: each chef has name, line_en and line_vi' % sl
        assert e['price'] is None or (type(e['price']) is int and e['price'] > 0), \
            'events-data.json: %s: price in đồng (a whole number) or null' % sl
        assert not e['booking'] or e['booking'].startswith('https://'), \
            'events-data.json: %s: booking is an https:// address or ""' % sl
        # It's over at the end of its last night: 23:59 that day, or its closing time the
        # next morning if it runs past midnight (18:00–01:00)
        until = datetime.fromisoformat('%sT23:59:59+07:00' % days[-1])
        if e['times']:
            a, b = e['times'].split('–')
            if b < a:
                until = datetime.fromisoformat('%sT%s:00+07:00' % (days[-1] + timedelta(days=1), b))
        out.append(dict(e, days=days, until=until, path='/events/%s/' % sl, ready=bool(e['summary_en'])))
    out.sort(key=lambda e: e['days'][0])
    numbers = [e['edition'] for e in out]
    assert len(set(numbers)) == len(numbers), 'events-data.json: each edition has its own number'
    return out


EVENTS = _events()
NOW = datetime.now().astimezone()
# An edition without its details: its page waits (WAITING above)
for _e in EVENTS:
    if not _e['ready']:
        WAITING[_e['path']] = ('event-%s' % _e['slug'],
                               'Eclipse %d: the line on what it is, then times, guest chefs, menu, price, how to '
                               'book' % _e['edition'])


def ev_name(e):
    """First edition · Lần thứ nhất (Edition 11 · Lần thứ 11 beyond ten)."""
    n = e['edition']
    if n <= len(ORDINALS):
        return t('%s edition' % ORDINALS[n - 1][0], 'Lần thứ %s' % ORDINALS[n - 1][1])
    return t('Edition %d' % n, 'Lần thứ %d' % n)


def ev_dates(e, year=True):
    """Friday 23 and Saturday 24 October 2026 · Thứ Sáu 23/10 và Thứ Bảy 24/10/2026."""
    days = e['days']
    en = [('%s %d' % (EN_DAYS[d.weekday()], d.day)) if (d.month, d.year) == (days[-1].month, days[-1].year)
          else '%s %d %s' % (EN_DAYS[d.weekday()], d.day, EN_MONTHS[d.month - 1]) for d in days]
    en = en_list(en) + ' %s%s' % (EN_MONTHS[days[-1].month - 1], ' %d' % days[-1].year if year else '')
    vi = ['%s %02d/%02d' % (VI_DAYS_CAP[d.weekday()], d.day, d.month) for d in days]
    vi = vi[0] if len(vi) == 1 else ', '.join(vi[:-1]) + ' và ' + vi[-1]
    return t(en, vi + ('/%d' % days[-1].year if year else ''))


def ev_upcoming():
    """The editions still to come when the site is built, soonest first."""
    return [e for e in EVENTS if e['until'] > NOW]


def ev_over(e):
    """Over when the site was built: shown as past without the browser's help."""
    return e['until'] <= NOW


# The head script marks each edition that has ended (html.past-<slug>), and says
# whether any are still to come (ev-none-up when none) or over (ev-some-past): these
# rules show the right copy of each, so an edition moves to Past on time.
EV_STYLE = ''.join('html.past-%s .ev-up[data-ev="%s"],html:not(.past-%s) .ev-past[data-ev="%s"]{display:none}'
                   'html.next-%s .next-ev[data-ev="%s"]{display:block}'
                   % ((e['slug'],) * 6) for e in ev_upcoming())


# --------------------------------------------------------------------------
# photographs: build/media.json
#   The files live in Cloudflare R2 (the sol-media bucket at media.sol.pizza), never
#   in git. Each page asks Cloudflare's image transformations on sol.pizza for the
#   size the screen needs (/cdn-cgi/image/…), cropped around the photo's focus, in
#   the format the browser takes best. Always the sol.pizza address: a preview's
#   workers.dev address can't transform. A slot with no photo shows nothing on
#   sol.pizza, and a marked placeholder in the full build (the shot list).
# --------------------------------------------------------------------------
MEDIA = json.loads(read(os.path.join(HERE, 'media.json')))
MEDIA_BASE = 'https://media.sol.pizza/'
IMAGE_CDN = 'https://sol.pizza/cdn-cgi/image/'
PHOTO_WIDTHS = (480, 768, 1080, 1600, 2400)
# A phone never gets more than this: it fills a 390 px screen at 3x, and keeps the
# home page's first photo (4:5 on a phone) under about 200 KB (check/media.js checks).
PHONE_MAX = 1080
# Where photographs go: slot: (what to shoot, shape on a wide screen, shape on a phone,
# how wide it shows (the sizes attribute, as site.css lays it out; its last width is the
# phone's), how many). Shapes are (width, height). Bands across the wide canvas are at
# most 1,440 px, across the text column 1,040; cards and the press photos are a third of
# the column (331 px), galleries too (339 px), and the home page's story photo 440 px.
SLOTS = {
    'home-hero': ('The room in the evening, or the oven with its fire: the first picture on the home page',
                  (2, 1), (4, 5), '100vw', 1),
    'home-story': ('Sol Pizza then and Sol now: the old room, the new one, the team at work',
                   (4, 5), (4, 5), '(min-width: 901px) 440px, calc(100vw - 48px)', 1),
    'home-menu': ('A pizza out of the oven', (3, 2), (3, 2), '(min-width: 901px) 331px, calc(100vw - 48px)', 1),
    'home-private-dining': ('A long table set for a group', (3, 2), (3, 2),
                            '(min-width: 901px) 331px, calc(100vw - 48px)', 1),
    'home-events': ('Eclipse: a night of it (landscape: a poster would be cropped)', (3, 2), (3, 2),
                    '(min-width: 901px) 331px, calc(100vw - 48px)', 1),
    'about-room': ('The room on each floor, and the bar', (2, 1), (4, 5),
                   '(min-width: 1488px) 1440px, calc(100vw - 48px)', 1),
    'about-oven': ('The Pavesi oven, and the pizzaiolo at it', (2, 1), (4, 5),
                   '(min-width: 1488px) 1440px, calc(100vw - 48px)', 1),
    'menu-food': ('Dishes: pizza, pasta, small plates', (4, 5), (4, 5), '(min-width: 761px) 339px, 82vw', 3),
    'menu-wine': ('The wine: bottles on the bar, a glass being poured', (2, 1), (4, 5),
                  '(min-width: 1088px) 1040px, calc(100vw - 48px)', 1),
    'menu-bar': ('The bar: a cocktail being made, the draft taps', (2, 1), (4, 5),
                 '(min-width: 1088px) 1040px, calc(100vw - 48px)', 1),
    'private-dining': ('Each space, set for a group', (4, 5), (4, 5), '(min-width: 761px) 339px, 82vw', 3),
    'visit': ('The building and its door, from the lane, so guests know it', (2, 1), (4, 5),
              '(min-width: 1488px) 1440px, calc(100vw - 48px)', 1),
    'press': ('Photographs the press may use: any of the above, at full size', (4, 3), (4, 3),
              '(min-width: 901px) 331px, calc(100vw - 48px)', 9),
}
EVENT_SLOT = ('Eclipse, each edition: a night of it (landscape: a poster would be cropped)', (2, 1), (4, 5),
              '(min-width: 1488px) 1440px, calc(100vw - 48px)', 1)


def _photos():
    out, keys = [], set()
    for p in MEDIA['photos']:
        k = p.get('key', '')
        assert re.fullmatch(r'[a-z0-9][a-z0-9/_.-]*\.(jpe?g|png|webp)', k) and k not in keys, \
            'media.json: %r: key is the file\'s name in the bucket (a-z 0-9 / _ . -), once each' % k
        keys.add(k)
        assert isinstance(p.get('width'), int) and isinstance(p.get('height'), int) and p['width'] > 0 \
            and p['height'] > 0, 'media.json: %s: width and height of the original, in pixels' % k
        assert (p.get('alt_en') or '').strip() and (p.get('alt_vi') or '').strip(), \
            'media.json: %s: alt_en and alt_vi, what the photo shows, in both languages' % k
        assert (p.get('credit') or '').strip(), 'media.json: %s: credit, the photographer' % k
        f = p.get('focus', [0.5, 0.5])
        assert len(f) == 2 and all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in f), \
            'media.json: %s: focus is [x, y], each from 0 to 1' % k
        for sl in p.get('slots', []):
            assert sl in SLOTS, ('media.json: %s: no slot %r (python3 build/media_tool.py slots; an Eclipse '
                                 'edition\'s photo needs no slot: it\'s the "image" in events-data.json)' % (k, sl))
        out.append(dict(p, focus=f))
    for sl, spec in SLOTS.items():
        n = sum(sl in p.get('slots', []) for p in out)
        assert n <= spec[4], 'media.json: %d photos for %s, which takes %d' % (n, sl, spec[4])
    return out


PHOTOS = _photos()
PHOTO_BY_KEY = {p['key']: p for p in PHOTOS}
for _e in EVENTS:
    assert not _e['image'] or _e['image'] in PHOTO_BY_KEY, \
        'events-data.json: %s: image %r is not a key in build/media.json' % (_e['slug'], _e['image'])


def photos_for(slot):
    return [p for p in PHOTOS if slot in p.get('slots', [])]


def photo_url(p, w, shape=None):
    """Cloudflare's address for photo p, w pixels wide, cropped to shape around its focus."""
    opts = ['width=%d' % w]
    if shape:
        opts += ['height=%d' % round(w * shape[1] / shape[0]), 'fit=cover',
                 'gravity=%sx%s' % tuple(('%.3f' % x).rstrip('0').rstrip('.') for x in p['focus'])]
    return '%s%s,quality=75,format=auto/%s%s' % (IMAGE_CDN, ','.join(opts), MEDIA_BASE, p['key'])


def _widths(p, shape, cap=None):
    """The widths to offer, never wider than the original allows for this shape (nor than cap)."""
    most = min(p['width'], int(p['height'] * shape[0] / shape[1]), cap or PHOTO_WIDTHS[-1])
    ws = [w for w in PHOTO_WIDTHS if w <= most]
    return ws or [most]


def _phone_sizes(sizes):
    """How wide a photo shows on a phone: the sizes attribute's last, unconditional width
    (a plain length, or a calc() without commas)."""
    last = sizes.rsplit(',', 1)[-1].strip()
    assert re.fullmatch(r'\d+(px|vw)|calc\([^,()]+\)', last), 'SLOTS: sizes ends with the phone\'s width: %r' % sizes
    return last


def alt_attr(en, vi):
    """An alt text in both languages: localise() keeps the page's (like label())."""
    return 'alt="%s" data-alt-en="%s" data-alt-vi="%s"' % (esc_attr(en), esc_attr(en), esc_attr(vi))


def picture(p, spec, eager=False):
    """A photo, sized for the screen: the phone's shape (and at most PHONE_MAX wide) below
    761px, the wide one above."""
    _, wide, phone, sizes, _ = spec
    ws_wide, ws_phone = _widths(p, wide), _widths(p, phone, PHONE_MAX)
    w0 = max(w for w in ws_wide if w <= 1080) if min(ws_wide) <= 1080 else ws_wide[0]
    source = ('<source media="(max-width: 760.98px)" srcset="%s" sizes="%s" width="%d" height="%d">'
              % (', '.join('%s %dw' % (photo_url(p, w, phone), w) for w in ws_phone), _phone_sizes(sizes),
                 ws_phone[-1], round(ws_phone[-1] * phone[1] / phone[0])))
    img = ('<img src="%s" srcset="%s" sizes="%s" width="%d" height="%d" %s%s decoding="async">'
           % (photo_url(p, w0, wide), ', '.join('%s %dw' % (photo_url(p, w, wide), w) for w in ws_wide), sizes,
              w0, round(w0 * wide[1] / wide[0]), alt_attr(p['alt_en'], p['alt_vi']),
              ' fetchpriority="high"' if eager else ' loading="lazy"'))
    return '<picture>%s%s</picture>' % (source, img)


def photo_placeholder(slot, spec):
    """The full build's stand-in for a photo still to come: its shape, and what to shoot."""
    what, wide, phone, _, n = spec
    return gate('photography', 'photographs (build/media.json; CONTENT-NEEDED.md, Photography)',
                '<div class="ph ph-photo" style="--ar:%d/%d;--ar-phone:%d/%d">%s <code>%s</code>: %s (%s)</div>'
                % (wide[0], wide[1], phone[0], phone[1], t('Photo', 'Ảnh'), slot, esc(what),
                   t('%d:%d wide, %d:%d on a phone%s' % (wide + phone + ((', up to %d' % n) if n > 1 else '',)),
                     '%d:%d trên màn hình rộng, %d:%d trên điện thoại%s'
                     % (wide + phone + ((', tối đa %d ảnh' % n) if n > 1 else '',)))))


def band(slot, cls='band', eager=False, spec=None, p=None):
    """One photo across the page (a figure), or its placeholder, or nothing."""
    spec = spec or SLOTS[slot]
    p = p or next(iter(photos_for(slot)), None)
    if not p:
        return photo_placeholder(slot, spec) if FULL else ''
    return '<figure class="%s">%s</figure>' % (cls, picture(p, spec, eager))


def gallery(slot, eager=False):
    """Up to three (or the slot's number of) photos in a row, to swipe on a phone. eager: the
    first loads at once, when the gallery is near the top of its page."""
    spec = SLOTS[slot]
    ps = photos_for(slot)
    if not ps:
        return photo_placeholder(slot, spec) if FULL else ''
    return ('<div class="gallery" style="--n:%d" role="region" tabindex="0" %s>%s</div>'
            % (min(len(ps), 3), label('Photographs', 'Hình ảnh'),
               ''.join('<figure>%s</figure>' % picture(p, spec, eager and i == 0) for i, p in enumerate(ps))))


def preload(slot):
    """<link rel="preload"> for a page's first photo (the home page's), in each shape."""
    p = next(iter(photos_for(slot)), None)
    if not p:
        return ''
    _, wide, phone, sizes, _ = SLOTS[slot]
    return ''.join('<link rel="preload" as="image" imagesrcset="%s" imagesizes="%s" media="%s" fetchpriority="high">\n'
                   % (', '.join('%s %dw' % (photo_url(p, w, shape), w) for w in _widths(p, shape, cap)).replace('&', '&amp;'),
                      sz, media)
                   for shape, cap, sz, media in ((phone, PHONE_MAX, _phone_sizes(sizes), '(max-width: 760.98px)'),
                                                 (wide, None, sizes, '(min-width: 761px)')))


# --------------------------------------------------------------------------
# announcements: build/announcements.json
# --------------------------------------------------------------------------
ANNOUNCE = json.loads(read(os.path.join(HERE, 'announcements.json')))


def _announcements():
    """The announcements still to come or showing at build time. Each is in every guest
    page, hidden; the head script shows the one whose window holds the moment the page is
    opened (Hanoi time), so the bar comes and goes on time without a rebuild."""
    now, out = datetime.now().astimezone(), []
    for a in ANNOUNCE['announcements']:
        assert re.fullmatch(r'[a-z0-9-]+', a.get('id', '')), 'announcements.json: id is lowercase letters, digits and -'
        start, end = datetime.fromisoformat(a['show_from']), datetime.fromisoformat(a['show_until'])
        assert start.tzinfo and end.tzinfo and start < end, \
            'announcements.json: %s: show_from and show_until with their +07:00, from before until' % a['id']
        assert a.get('text') and a.get('text_vi'), 'announcements.json: %s: text and text_vi' % a['id']
        assert not a.get('link') or (a.get('link_text') and a.get('link_text_vi')), \
            'announcements.json: %s: a link needs link_text and link_text_vi' % a['id']
        if end > now:
            out.append(a)
    return out


ANNOUNCEMENTS = _announcements()


def announcement_bars():
    bars = []
    for a in ANNOUNCEMENTS:
        link = (' <a href="%s">%s</a>' % (esc_attr(a['link']), t(esc(a['link_text']), esc(a['link_text_vi'])))
                if a.get('link') else '')
        bars.append('<div class="ann" data-ann="%s" role="region" %s><div class="wrap ann-in"><p>%s%s</p>'
                    '<button class="ann-x" type="button" data-ann-close="%s" %s>%s</button></div></div>\n'
                    % (a['id'], label('Announcement', 'Thông báo'), t(esc(a['text']), esc(a['text_vi'])), link,
                       a['id'], label('Dismiss', 'Đóng thông báo'), CLOSE))
    return ''.join(bars)


# --------------------------------------------------------------------------
# shell
#   Every guest page is written twice: in English at /… and in Vietnamese at /vi/…
#   page() assembles it with every line in both languages, as t() writes them, and
#   write_pages() writes one language per file (localise()): its own <html lang>,
#   title, description, canonical, hreflang, share card, and links that stay in that
#   language. The EN · VI switch links to the same page in the other language.
#   The kitchen's pages (kitchen_page()) are not guest pages: one bilingual page each,
#   with the header, footer, styles and in-page EN / VI switch they had on 12 Oct 2026,
#   no /vi/ copy, and no consent banner, phone bar, announcement bar or analytics.
# --------------------------------------------------------------------------
LANGS = ('en', 'vi')
OG_LOCALE = {'en': 'en_GB', 'vi': 'vi_VN'}
CONSENT_VERSION = 1           # raise it when the banner's wording changes: everyone is asked again (head script, site.js)
FONT_PRELOADS = {             # above the fold: the heading face and the text face
    'en': [BN_ARORA_URL, '/assets/fonts/eb-garamond-latin-400-normal.woff2'],
    'vi': ['/assets/fonts/philosopher-latin-400-normal.woff2', '/assets/fonts/philosopher-vietnamese-400-normal.woff2',
           '/assets/fonts/eb-garamond-latin-400-normal.woff2', '/assets/fonts/eb-garamond-vietnamese-400-normal.woff2'],
}


def lang_path(path, lang):
    """The address of a page in a language: /menu/ is /vi/menu/ in Vietnamese, / is /vi/."""
    return path if lang == 'en' else '/vi' + path


def _head_script():
    """Before first paint, on every guest page:
    - language: an old ?lang=vi link (remembered, as it always was) or a #vi / #en link
      (such as /privacy/#vi) opens the page in that language; on the home page, the
      choice made with the EN · VI switch last time. Nothing reads the browser's language.
      The address it goes to always stays on this site: /vi//example.com/#en goes to
      /example.com/, never to //example.com/ (another site).
    - cookies: html.consent-ask while there is no choice (or it is a year old, or the
      banner's wording has changed since), which shows the banner (site.css).
    - opening day: html.is-open from OPENING_AT (by_state()).
    - announcements: html.ann-<id> for the one showing now, unless it was dismissed.
    - events: html.past-<slug> for each edition that has ended since the build, next-<slug>
      for the first still to come; ev-none-up when none is, ev-some-past when any has
      ended (EV_STYLE). Editions over at build time are written as past already."""
    ann = ','.join('["%s",%d,%d]' % (a['id'], datetime.fromisoformat(a['show_from']).timestamp() * 1000,
                                     datetime.fromisoformat(a['show_until']).timestamp() * 1000)
                   for a in ANNOUNCEMENTS)
    evs = ','.join('["%s",%d]' % (e['slug'], e['until'].timestamp() * 1000) for e in ev_upcoming())
    return ("(function(){var d=document.documentElement,l=location,n=Date.now(),s=null;d.className+=' js';"
            "try{s=window.localStorage}catch(e){}"
            "function g(k){try{return s.getItem(k)}catch(e){return null}}"
            "function p(k,v){try{s.setItem(k,v)}catch(e){}}"
            "var a=l.pathname,v=/^\\/vi(\\/|$)/.test(a),q=/[?&]lang=(en|vi)(?:&|$)/.exec(l.search),"
            "h=/^#(en|vi)$/.exec(l.hash),w=q?q[1]:h?h[1]:null;"
            "if(q)p('sol-lang',q[1]);if(!w&&a==='/')w=g('sol-lang');"
            "if(w&&(w==='vi')!==v){l.replace((w==='vi'?'/vi'+a:a.slice(3).replace(/^\\/+/,'/')||'/')"
            "+l.search.replace(/([?&])lang=(en|vi)(&|$)/,'$1').replace(/[?&]$/,'')+(h?'':l.hash));return}"
            "var c=null;try{c=JSON.parse(g('sol-consent'))}catch(e){}"
            "if(!c||c.v!==%d||!(n-Date.parse(c.t)<31536e6))d.className+=' consent-ask';"
            "%s"
            "[%s].forEach(function(x){if(n>=x[1]&&n<x[2]&&!g('sol-ann-'+x[0]))d.className+=' ann-'+x[0]});"
            "var u=0,o=0;[%s].forEach(function(x){if(n>x[1]){d.className+=' past-'+x[0];o++}"
            "else if(!u++)d.className+=' next-'+x[0]});"
            "if(!u)d.className+=' ev-none-up';if(o)d.className+=' ev-some-past'"
            "})();"
            % (CONSENT_VERSION,
               "if(n>=Date.parse('%s'))d.className+=' is-open';" % OPENING_AT
               if SITE_STATE == 'preopening' and OPENING_AT else '', ann, evs))


HEAD_SCRIPT = _head_script()
# Each announcement shows only while the head script asks for it.
ANN_STYLE = ''.join('html.ann-%s .ann[data-ann="%s"]{display:block}' % (a['id'], a['id']) for a in ANNOUNCEMENTS) \
    + EV_STYLE


def og_image(name, lang='en'):
    """A share card's address. name: a card in build/og/ ('home', 'menu', …), each
    rendered in both languages (og-home.png, og-home-vi.png), or a full URL."""
    if name.startswith('https://'):
        return name
    return '%s/og-%s%s.png' % (SITE, name, '' if lang == 'en' else '-vi')


def head(rec, lang):
    """A guest page's <head> in one language. rec: what page() registered."""
    i = LANGS.index(lang)
    path, title, desc = rec['path'], rec['title'][i], rec['desc'][i]
    og_title, og_desc = rec['og_text'][i] if rec['og_text'] else (title, desc)
    url = SITE + lang_path(path, lang)
    lines = [
        '<!DOCTYPE html>',
        '<html lang="%s" data-brand-fonts="%s"%s>' % (lang, BRAND_FONTS,
                                                      ' class="is-open"' if SITE_STATE == 'open' else ''),
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        '<script>%s</script>' % HEAD_SCRIPT,
        '<title>%s</title>' % title,
        '<meta name="description" content="%s">' % desc,
        '<link rel="preconnect" href="https://use.typekit.net" crossorigin>',
        # The Adobe kit (Plunct) mustn't hold up the first paint: fetch it as a
        # preload and apply it once it arrives.
        '<link rel="preload" href="%s" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">' % TYPEKIT_KIT,
        '<noscript><link rel="stylesheet" href="%s"></noscript>' % TYPEKIT_KIT,
        '<link rel="stylesheet" href="/assets/fonts.css">',     # inlined by optimise()
        '<link rel="stylesheet" href="/assets/tokens.css">',
        '<link rel="stylesheet" href="/assets/printed-menu.css">',
        '<link rel="stylesheet" href="/assets/site.css">',
    ] + (['<style>%s</style>' % ANN_STYLE] if ANN_STYLE else []) + [
        '<script src="/assets/site.js" defer></script>',
    ] + ['<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' % f for f in FONT_PRELOADS[lang]]
    if rec['index']:
        lines += ['<link rel="canonical" href="%s">' % url]
        lines += ['<link rel="alternate" hreflang="%s" href="%s%s">' % (code, SITE, lang_path(path, code))
                  for code in LANGS]
        lines += ['<link rel="alternate" hreflang="x-default" href="%s%s">' % (SITE, path)]
    lines += [
        '<meta property="og:type" content="%s">' % rec['ogtype'],
        '<meta property="og:site_name" content="Sol">',
        '<meta property="og:title" content="%s">' % og_title,
        '<meta property="og:description" content="%s">' % og_desc,
    ]
    if rec['og']:
        lines += ['<meta property="og:image" content="%s">' % og_image(rec['og'], lang),
                  '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">']
    lines += [
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:locale" content="%s">' % OG_LOCALE[lang],
        '<meta property="og:locale:alternate" content="%s">' % OG_LOCALE[LANGS[1 - i]],
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="theme-color" content="#f9e9d3">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
    ]
    if path == '/' and GOOGLE_VERIFICATION:
        lines.append('<meta name="google-site-verification" content="%s">' % esc_attr(GOOGLE_VERIFICATION))
    lines += [x(lang) if callable(x) else x for x in rec['extra'] if x]
    if rec['index'] and path != '/':
        lines.append(breadcrumbs(path, lang))
    lines.append('</head>')
    return '\n'.join(lines) + '\n'


def breadcrumbs(path, lang):
    """BreadcrumbList for a page below the home page: Sol › Menu › Wine, each step a page
    of this build, named as its title is (before the " — ")."""
    titles = {r['path']: r['title'] for r in PAGES if not r['kitchen'] and not r['hidden']}
    i = LANGS.index(lang)
    steps, parts = [('/', 'Sol')], [x for x in path.strip('/').split('/') if x]
    for n in range(1, len(parts) + 1):
        p = '/' + '/'.join(parts[:n]) + ('/' if n < len(parts) or path.endswith('/') else '')
        if p in titles:
            steps.append((p, re.sub(r'<[^>]+>', '', titles[p][i]).split(' — ')[0]))
    if len(steps) < 2:
        return ''
    return ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': n + 1, 'name': _html.unescape(name), 'item': SITE + lang_path(p, lang)}
        for n, (p, name) in enumerate(steps)]})


# --------------------------------------------------------------------------
# share cards: build/og/
#   One template (build/og/card.html) and the words below, a card per page per
#   language: og-<name>.png in English, og-<name>-vi.png in Vietnamese. The build
#   writes each card's page into build/og/html/; `npm run og` (check/og.js) renders
#   them to build/og/png/ in the site's own fonts and notes in build/og/cards.json
#   what each was rendered from; `npm run pack-assets` packs the PNGs into
#   build/assets.b64.json. The build stops if a card's words have changed since it
#   was rendered. No counts or "opening soon" on a card: they'd go stale.
# --------------------------------------------------------------------------
OG_CARDS = {  # name: ((English eyebrow, title), (Vietnamese eyebrow, title))
    'home':  (('Tây Hồ, Hanoi', 'Italian-American,<br>cooked over wood.'),
              ('Tây Hồ, Hà Nội', 'Ẩm thực Ý–Mỹ,<br>nấu bằng lửa củi.')),
    'menu':  (('The menu · Wood-fired, made in-house', 'What we’re<br>cooking.'),
              ('Thực đơn · Lò củi, làm tại nhà hàng', 'Chúng tôi<br>nấu gì.')),
    'wine':  (('The wine list · By the glass and the bottle', 'Ask what’s<br>open tonight.'),
              ('Danh sách vang · Theo ly và theo chai', 'Hỏi xem tối nay<br>mở chai nào.')),
    'story': (('Our story · Sol, Tây Hồ', 'Closing one thing<br>to build another.'),
              ('Câu chuyện của chúng tôi · Sol, Tây Hồ', 'Khép lại một điều,<br>để dựng nên điều mới.')),
    'visit': (('Tây Hồ, Hanoi', 'Find us, and<br>book a table.'),
              ('Tây Hồ, Hà Nội', 'Tìm chúng tôi<br>và đặt bàn.')),
    'jobs':  (('Work with us · Tây Hồ, Hanoi', 'Come and build<br>the new Sol.'),
              ('Tuyển dụng · Tây Hồ, Hà Nội', 'Cùng xây dựng<br>Sol mới.')),
    'private-dining': (('Private dining · Tây Hồ, Hanoi', 'Groups and<br>private dining.'),
                       ('Tiệc riêng · Tây Hồ, Hà Nội', 'Nhóm đông<br>và tiệc riêng.')),
    'events': (('Events · Tây Hồ, Hanoi', 'Eclipse,<br>Sol’s pop-up series.'),
               ('Sự kiện · Tây Hồ, Hà Nội', 'Eclipse, chuỗi<br>pop-up của Sol.')),
}
OG_DIR = os.path.join(HERE, 'og')


def og_cards():
    """Write each card's page into build/og/html/ for `npm run og`, and stop if a card in
    build/og/png/ was rendered from other words, or isn't the one packed after rendering
    (build/og/cards.json: what each was rendered from, and the hash of its PNG)."""
    template = read(os.path.join(OG_DIR, 'card.html'))
    rendered = json.loads(read(os.path.join(OG_DIR, 'cards.json'))) \
        if os.path.exists(os.path.join(OG_DIR, 'cards.json')) else {}
    stale = []
    for name, sides in OG_CARDS.items():
        for lang, (eyebrow, title) in zip(LANGS, sides):
            card = 'og-%s%s' % (name, '' if lang == 'en' else '-vi')
            html = template.format(lang=lang, eyebrow=eyebrow, title=title,
                                   title_font='"BN Arora",Georgia,serif' if lang == 'en'
                                   else '"Philosopher",Georgia,serif',
                                   title_size=100 if lang == 'en' else 88)
            write(os.path.join(OG_DIR, 'html', card + '.html'), html)
            png = os.path.join(OG_DIR, 'png', card + '.png')
            note = rendered.get(card + '.png')
            note = note if isinstance(note, dict) else {}
            if note.get('from') != hashlib.sha1(html.encode('utf-8')).hexdigest() or not os.path.exists(png) \
                    or note.get('png') != hashlib.sha1(open(png, 'rb').read()).hexdigest():
                stale.append(card + '.png')
    if stale:
        raise SystemExit('Share cards out of date (their words or design changed since they were rendered, or '
                         'they were rendered and not packed): %s. Run `npm run og`, then `npm run pack-assets`, '
                         'and commit build/assets.b64.json and build/og/cards.json (build/README.md, "Share '
                         'cards").' % ', '.join(stale))


CARET  = ('<svg class="caret" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" '
          'aria-hidden="true" focusable="false"><path d="M3 6l5 5 5-5"/></svg>')
BURGER = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
          'stroke-linecap="square" aria-hidden="true" focusable="false"><path d="M3 6.5h18M3 12h18M3 17.5h18"/></svg>')
CLOSE  = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
          'stroke-linecap="square" aria-hidden="true" focusable="false"><path d="M5 5l14 14M19 5L5 19"/></svg>')
HOME_LABEL = label('Sol, home', 'Sol, trang chủ')


def logo(w, h):
    return '<img src="/assets/sol-primary-red.svg" alt="Sol" width="%d" height="%d">' % (w, h)


def lang_switch(en_href, vi_href):
    """EN · VI, as links to this page in each language (the current one marked). Both
    versions are in the page; localise() keeps the one for the page's language."""
    def a(code, href, current):
        return ('<a href="%s" hreflang="%s" lang="%s" data-lang-link="%s"%s>%s</a>'
                % (href, code, code, code, ' aria-current="true"' if current else '', code.upper()))

    def group(cur):
        return ('<div class="lang" role="group" %s>%s<span aria-hidden="true">·</span>%s</div>'
                % (label('Language', 'Ngôn ngữ'), a('en', en_href, cur == 'en'), a('vi', vi_href, cur == 'vi')))
    return t(group('en'), group('vi'))


def tab_current(key, cur):
    """aria-current for a header tab. cur: menu section (food / wine / bar), a SECTIONS key,
    jobs / role, or None. Menu is the current page on Food (/menu/) and the current section
    on Wine and Bar; Work with us (the public build's tab while a page is hidden) is the
    current page on /jobs/ and the current section on the role pages."""
    if key == cur or (key == 'menu' and cur == 'food'):
        return ' aria-current="page"'
    if (key == 'menu' and cur in ('wine', 'bar')) or (key == 'jobs' and cur == 'role'):
        return ' aria-current="true"'
    return ''


def header(cur, en_href, vi_href):
    """The masthead and the bar under it. Wide screens (1024px and up): the big logo at
    the top, then the bar, which stays at the top of the window as the page scrolls, with
    a small logo once the big one has gone, the tabs, EN · VI and the red Book button.
    Narrower: the slim bar (EN · VI, logo, menu button) and the phone bar at the foot of
    the window (actionbar()). Menu pages show Food / Wine / Bar under the bar; elsewhere
    they open under Menu on a wide screen (site.js)."""
    menu_page = cur in ('food', 'wine', 'bar')
    sw = lang_switch(en_href, vi_href)

    def subnav(cls):
        return ('<nav class="subnav%s" %s><div class="wrap"><ul>%s</ul></div></nav>'
                % (cls, label('Menu sections', 'Các mục thực đơn'),
                   ''.join('<li><a href="%s"%s>%s<span>%s</span></a></li>'
                           % (href, ' aria-current="page"' if key == cur else '', name, sub)
                           for key, href, name, sub in MENU_TABS)))

    def tabs(caret):
        return ''.join('<li><a href="%s"%s%s>%s%s</a></li>'
                       % (href, ' data-menu-link' if caret and key == 'menu' and not menu_page else '',
                          tab_current(key, cur), name, CARET if caret and key == 'menu' and not menu_page else '')
                       for key, href, name in shown_tabs())

    return """<header class="site-top">
  <div class="mbar">
    {sw}
    <a href="/" {home}>{logo_s}</a>
    <button class="burger" type="button" {open_l} aria-expanded="false" aria-controls="navsheet" data-sheet-open>{burger}</button>
  </div>
  <div class="masthead"><a href="/" {home}>{logo_l}</a></div>
</header>
<div class="sitebar-mark" aria-hidden="true"></div>
<nav class="sitebar" data-sitebar {main_l}>
  <div class="wrap sitebar-in">
    <a class="sitebar-logo" href="/" {home}>{logo_xs}</a>
    <ul class="nav-links">{tabs}</ul>
    <div class="sitebar-end">{sw}{book}</div>
  </div>
{dropdown}</nav>
{static}<div class="navsheet" id="navsheet" role="dialog" aria-modal="true" {sheet_l} tabindex="-1" hidden>
  <div class="navsheet-top"><span></span><a href="/" {home}>{logo_s}</a>
    <button class="navsheet-close" type="button" {close_l} data-sheet-close>{close}</button></div>
  <ul class="navsheet-pages">{sheet_tabs}</ul>
  <div class="navsheet-foot">
    {book_long}
    <div class="navsheet-meta"><span>{hours}</span>{sw}</div>
  </div>
</div>
""".format(sw=sw, home=HOME_LABEL, logo_s=logo(74, 26), logo_l=logo(165, 58), logo_xs=logo(60, 21),
           open_l=label('Open navigation', 'Mở menu điều hướng'), burger=BURGER,
           main_l=label('Main', 'Điều hướng chính'), tabs=tabs(True),
           # Book: only while the booking page is public (HIDDEN)
           book=('<a class="btn btn-red btn-sm" href="/booking/#book" data-track="book_click">%s</a>' % BOOK_SHORT
                 if live('booking') else ''),
           book_long=('<a class="btn btn-red" href="/booking/#book" data-track="book_click">%s</a>' % BOOK
                      if live('booking') else ''),
           dropdown=('  ' + subnav(' subnav-drop') + '\n') if live('menu') and not menu_page else '',
           static=(subnav(' subnav-static') + '\n') if menu_page else '',
           sheet_l=label('Navigation', 'Điều hướng'), sheet_tabs=tabs(False),
           close_l=label('Close navigation', 'Đóng menu điều hướng'), close=CLOSE, hours=HOURS_TAB)


def company_line():
    """The footer's last line: the company, its tax code and registered address once set
    (TAX_CODE, REGISTERED_ADDRESS), and Tây Hồ."""
    parts = ['© 2026 %s' % COMPANY_VI]
    if TAX_CODE:
        parts.append(t('Tax code %s' % TAX_CODE, 'MST %s' % TAX_CODE))
    else:
        parts.append(gate('company-tax-code', 'the company’s tax code (mã số thuế), TAX_CODE in gen.py',
                          t('Tax code [to come]', 'MST [sẽ cập nhật]'), tag='span'))
    parts.append(t(*REGISTERED_ADDRESS) if REGISTERED_ADDRESS else t('Tây Hồ, Hanoi', 'Tây Hồ, Hà Nội'))
    return ' · '.join(p for p in parts if p)


def footer(news=True):
    more = ([(href, name) for key, href, name in NAV_TABS if live(key)]
            + ([('/booking/', t('Booking', 'Đặt bàn'))] if live('booking') else [])
            + [(href, name) for href, name in (('/press/', t('Press', 'Báo chí')),
                                               ('/gift-cards/', t('Gift cards', 'Thẻ quà tặng'))) if not hidden(href)]
            + [('/jobs/', JOBS_TAB)]
            # Privacy: the guests' notice once it's public, the applicants' beside it
            + ([('/privacy/guests/', t('Privacy', 'Quyền riêng tư')),
                ('/privacy/', t('Applicant privacy', 'Bảo mật cho ứng viên'))] if not hidden('/privacy/guests/')
               else [('/privacy/', t('Privacy', 'Bảo mật'))])
            + [('/privacy/cookies/', t('Cookies', 'Cookie'))]
            + ([('/accessibility/', t('Accessibility', 'Hỗ trợ tiếp cận'))] if not hidden('/accessibility/') else []))
    return """<footer class="site-footer">
  <div class="wrap"><div class="footer-inner">
    <a class="footer-logo" href="/" {home}>{logo}</a>
    {news}
    <div class="footer-cols"><section><h2>{find}</h2><p>{addr}</p><p><a href="{maps}">{maps_t}</a></p></section><section><h2>{open}</h2><p>{days}</p><p>{hours}</p>{last}{closed}</section><section><h2>{talk}</h2><p><a href="{tel}">{phone}</a></p><p><a href="mailto:{email}">{email}</a></p><p>{insta}</p>{social}</section><nav {more_l}><h2>{more_h}</h2><ul>{more}</ul></nav></div>
    <p class="legal">{legal}<span class="legal-settings"> · <button class="linkish" type="button" data-consent-open>{settings}</button></span></p>
  </div></div>
</footer>
""".format(home=HOME_LABEL, logo=logo(91, 32), find=t('Find us', 'Tìm chúng tôi'),
           addr=t(ADDRESS_EN, ADDRESS_VI), maps=MAPS_URL, maps_t=MAPS_LINK_TEXT,
           open=t('Open', 'Giờ mở cửa'), days=HOURS_DAYS, hours=HOURS_SPAN,
           last='<p>%s</p>' % LAST_ORDERS if LAST_ORDERS else '',
           closed='<p>%s</p>' % HOURS_CLOSED if HOURS_CLOSED else '',
           talk=t('Talk to us', 'Liên hệ'), tel=PHONE_TEL, phone=PHONE, email=EMAIL,
           insta=INSTA_LINK, more_l=label('More', 'Thêm'), more_h=t('More', 'Thêm'),
           more=''.join('<li><a href="%s">%s</a></li>' % m for m in more),
           social=''.join('<p><a href="%s">%s</a></p>' % (esc_attr(url), esc(name)) for name, url in SOCIAL),
           legal=company_line(),
           settings=t('Cookie settings', 'Cài đặt cookie'), news=newsletter() if news else '')


def mailto(to, subject, body):
    """A mailto: link's address, its subject and body encoded as encodeURIComponent would."""
    return 'mailto:%s?subject=%s&amp;body=%s' % (to, encode_uri_component(subject),
                                                 encode_uri_component(body.replace('\n', '\r\n')))


def newsletter(cls='footer-news', btn='btn btn-outline btn-sm'):
    """The newsletter sign-up, in every guest page's footer (on the home page, in the page
    instead): an email from the guest's own address, which is also their consent; the
    team keeps the list (README.md)."""
    def button(body, text):
        return ('<a class="%s" href="%s" data-track="newsletter_signup">%s</a>'
                % (btn, mailto(ENQUIRIES, 'Newsletter', body), text))
    return ('<section class="%s" aria-labelledby="news-h"><h2 id="news-h">%s</h2><p>%s</p>%s</section>'
            % (cls, t('News from Sol', 'Tin từ Sol'),
               t('Events, new dishes and the next Eclipse, by email, now and then.',
                 'Sự kiện, món mới và Eclipse kế tiếp, thỉnh thoảng gửi qua email.'),
               t(button('Please add this email address to Sol’s newsletter.', 'Sign up by email'),
                 button('Vui lòng thêm địa chỉ email này vào danh sách nhận tin của Sol.', 'Đăng ký qua email'))))


def zalo_url():
    return 'https://zalo.me/%s' % ZALO


def whatsapp_url():
    return 'https://wa.me/%s' % WHATSAPP


def actionbar():
    """The phone bar (narrow screens): Book (while the booking page is public), then, once
    online booking is live (CONTACT_LIVE), Call on English pages and Zalo on Vietnamese
    ones (Call until there's a Zalo number), then Directions. Not on /booking/ (it is the
    booking page) or the role pages (they have the Apply bar)."""
    book = ('<a class="btn btn-red" href="/booking/#book" data-track="book_click">%s</a>' % BOOK_SHORT
            if live('booking') else '')
    call = ''
    if CONTACT_LIVE:
        call_en = '<a class="btn btn-outline" href="%s" data-track="call_click">Call</a>' % PHONE_TEL
        call_vi = ('<a class="btn btn-outline" href="%s" data-track="zalo_click">Zalo</a>' % zalo_url() if ZALO
                   else '<a class="btn btn-outline" href="%s" data-track="call_click">Gọi</a>' % PHONE_TEL)
        call = t(call_en, call_vi)
    return ('<nav class="actionbar" %s>%s%s<a class="btn btn-outline" href="%s" data-track="directions_click">%s</a>'
            '</nav>\n' % (label('Quick actions', 'Thao tác nhanh'), book, call, DIRECTIONS_URL, DIRECTIONS))


def consent_banner():
    """The cookie choice (site.js). Shown while there is no choice (html.consent-ask) and
    reopened from the footer's Cookie settings (html.consent-open). Accept all, Reject all
    and Settings carry the same weight; nothing optional loads before a choice."""
    def choice(name, title_html, text_html):
        return ('<label class="consent-choice"><input type="checkbox" name="%s"><span><b>%s</b> %s</span></label>'
                % (name, title_html, text_html))
    return """<div class="consent" id="consent" role="region" aria-labelledby="consent-h">
  <div class="wrap consent-in">
    <p class="label" id="consent-h">{h}</p>
    <p class="consent-text">{text} <a href="/privacy/cookies/">{notice}</a></p>
    <div class="consent-settings" id="consent-settings" hidden>{analytics}{ads}</div>
    <div class="consent-actions"><button class="btn btn-outline btn-sm" type="button" data-consent="all">{all}</button><button class="btn btn-outline btn-sm" type="button" data-consent="none">{none}</button><button class="btn btn-outline btn-sm" type="button" data-consent="settings" aria-expanded="false" aria-controls="consent-settings">{settings}</button><button class="btn btn-outline btn-sm" type="button" data-consent="save" hidden>{save}</button></div>
  </div>
</div>
""".format(h=t('Cookies', 'Cookie'),
           text=t('We’d like to use analytics cookies to see how the site is used, and advertising cookies to '
                  'see whether our ads work. The site works the same without them, and you can change your '
                  'mind any time under Cookie settings.',
                  'Chúng tôi muốn dùng cookie phân tích để biết trang web được sử dụng ra sao, và cookie quảng '
                  'cáo để biết quảng cáo của chúng tôi có hiệu quả không. Trang web vẫn hoạt động như bình '
                  'thường nếu không có chúng, và bạn có thể đổi lựa chọn bất cứ lúc nào ở mục Cài đặt cookie.'),
           notice=t('Cookie notice', 'Thông báo về cookie'),
           analytics=choice('analytics', t('Analytics', 'Phân tích'),
                            t('Google Analytics: which pages are read, and how people find us.',
                              'Google Analytics: những trang nào được đọc, và khách tìm đến chúng tôi bằng cách nào.')),
           ads=choice('ads', t('Advertising', 'Quảng cáo'),
                      t('Meta Pixel: whether our ads on Facebook and Instagram bring people to the site.',
                        'Meta Pixel: quảng cáo của chúng tôi trên Facebook và Instagram có đưa khách đến trang '
                        'web không.')),
           all=t('Accept all', 'Đồng ý tất cả'), none=t('Reject all', 'Từ chối tất cả'),
           settings=t('Settings', 'Tùy chọn'), save=t('Save choices', 'Lưu lựa chọn'))


PAGES = []      # every page this build makes, in order: what page() and kitchen_page() registered


def page(path, body_class, title, desc, main, cur=None, og=None, ogtype='website', extra='', body_attrs='',
         index=True, verbatim=False, og_text=None, bar=True, switch=None, news=True):
    """A guest page, written in English at path and in Vietnamese at /vi/path. title and
    desc are (English, Vietnamese) pairs; og_text, when the share card's words differ from
    them: ((English title, description), (Vietnamese title, description)).
    og: the share card's name in build/og/ ('home', …) or a full URL. bar: the phone bar.
    news: the newsletter sign-up in the footer (the home page has it in the page).
    switch: where EN · VI lead, if not to this page in each language (the 404 page).
    verbatim: leave main's text exactly as it is (the privacy notice). A page that isn't
    public yet (HIDDEN) is built but not written, so a mistake in it still stops the
    public build."""
    en_href, vi_href = switch or (lang_path(path, 'en'), lang_path(path, 'vi'))
    if path in WAITING:         # a whole page waiting for its content: labelled in the full build
        key, what = WAITING[path]
        GATES[key] = what
        if FULL:
            main = re.sub(r'(<main\b[^>]*>)', lambda m: m.group(1) + (
                '<div class="wrap"><p class="gated-label gated-page">%s <code>%s</code>: %s</p></div>'
                % (t('Content needed', 'Cần nội dung'), key, esc(what))), main, count=1)
    body = '<body class="%s%s"%s>\n%s\n' % (body_class, ' has-actionbar' if bar else '', body_attrs, SUN_SPRITE)
    body += nbsp('<a class="skip" href="#main">%s</a>\n' % t('Skip to content', 'Chuyển đến nội dung chính')
                 + consent_banner() + announcement_bars() + header(cur, en_href, vi_href))
    body += main if verbatim else nbsp(main)
    body += nbsp(footer(news) + (actionbar() if bar else ''))
    bad = re.search(r'="[^"<>]*<span data-l=', body)
    if bad:
        raise SystemExit('%s: t() inside an attribute (use label(), or one element per language): …%s…'
                         % (path, body[max(0, bad.start() - 60):bad.end() + 40]))
    for words in title + desc:              # they go into attributes (content="…") as they are
        assert '"' not in words and '<' not in words, '%s: a title or description with " or <: %s' % (path, words)
    body += '</body>\n</html>\n'
    # extra: <head> lines, as a string, a function of the language, or a list of either
    extra = extra if isinstance(extra, list) else [extra]
    rec = dict(path=path, kitchen=False, title=title, desc=desc, og=og, ogtype=ogtype, extra=extra,
               index=index, og_text=og_text, body=body, hidden=hidden(path))
    PAGES.append(rec)
    return rec


def out_file(path):
    """The file in dist/ that answers an address: / is index.html, /menu/ is
    menu/index.html, /jobs/sous-chef is jobs/sous-chef.html (html_handling serves it)."""
    if path.endswith('/'):
        return os.path.join(DIST, *path.strip('/').split('/'), 'index.html') if path != '/' \
            else os.path.join(DIST, 'index.html')
    return os.path.join(DIST, *path.strip('/').split('/')) + ('' if path.endswith('.html') else '.html')


# --------------------------------------------------------------------------
# one language per file
# --------------------------------------------------------------------------
_DATA_L = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\b([^>]*?)\sdata-l="(en|vi)"([^>]*)>')
_ARIA = re.compile(r'aria-label="[^"]*" data-aria-en="([^"]*)" data-aria-vi="([^"]*)"')
_ALT = re.compile(r'alt="[^"]*" data-alt-en="([^"]*)" data-alt-vi="([^"]*)"')
_A_TAG = re.compile(r'<a\b[^>]*>')


def _close_tag(html, tag, start):
    """Where the element whose start tag ends at start closes: (start, end) of its end tag."""
    depth = 1
    for m in re.finditer(r'<(/?)%s\b[^>]*>' % tag, html[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start + m.start(), start + m.end()
    raise SystemExit('build: <%s data-l> without its </%s>' % (tag, tag))


def _keep_lang(html, lang):
    """Keep one language of every data-l element: the other's are dropped, and a t() span
    (<span data-l="en" lang="en">) gives way to its text."""
    out, i = [], 0
    while True:
        m = _DATA_L.search(html, i)
        if not m:
            out.append(html[i:])
            return ''.join(out)
        out.append(html[i:m.start()])
        tag, el_lang = m.group(1), m.group(3)
        close_at, i = _close_tag(html, tag, m.end())
        if el_lang != lang:
            continue
        inner = _keep_lang(html[m.end():close_at], lang)
        attrs = m.group(2) + m.group(4)
        if tag == 'span' and attrs.strip() == 'lang="%s"' % el_lang:
            out.append(inner)
        else:
            # A block keeps its lang: it may sit inside one in the other language (the
            # Vietnamese note above an English job description).
            out.append('<%s%s>%s%s' % (tag, attrs, inner, html[close_at:i]))


def localise(body, lang, guest_paths):
    """A page's <body> in one language: one side of every t() pair and data-l block, one
    aria-label, and on a Vietnamese page every link to a guest page sent to its /vi/
    address (links with an hreflang, like the EN · VI switch, go where they say)."""
    body = _keep_lang(body, lang)
    body = _ARIA.sub(lambda m: 'aria-label="%s"' % m.group(1 if lang == 'en' else 2), body)
    body = _ALT.sub(lambda m: 'alt="%s"' % m.group(1 if lang == 'en' else 2), body)
    if lang == 'en':
        return body

    def fix(m):
        tag = m.group(0)
        h = re.search(r'\shref="(/[^"]*)"', tag)
        if not h or ' hreflang="' in tag:
            return tag
        parts = urlsplit(h.group(1))
        if parts.path not in guest_paths:
            return tag
        return tag.replace(h.group(0), ' href="%s"' % lang_path(h.group(1), 'vi'), 1)
    return _A_TAG.sub(fix, body)


def write_pages():
    """Write every page registered, each guest page in both languages; the ones not public
    yet (HIDDEN) are skipped. Returns the files written."""
    guest_paths = {r['path'] for r in PAGES if not r['kitchen'] and not r['hidden']}
    written = []
    for r in PAGES:
        if r['hidden']:
            continue
        if r['kitchen']:
            write(out_file(r['path']), r['doc'])
            written.append(out_file(r['path']))
            continue
        for lang in LANGS:
            out = out_file(lang_path(r['path'], lang))
            write(out, head(r, lang) + localise(r['body'], lang, guest_paths))
            written.append(out)
    return written


# --------------------------------------------------------------------------
# the kitchen's shell (kitchen_page())
#   The kitchen's three pages keep the shell every page had on 12 Oct 2026: both
#   languages in the page and the in-page EN / VI switch (kitchen.js), the header
#   with About · Menu · Booking, and the footer as it was, styled by the frozen
#   build/design/kitchen/kitchen.css. No consent banner, phone bar, announcement bar
#   or analytics, and no /vi/ copy: a /vi/dough/ page would sit outside the Worker's
#   password check (run_worker_first), and the build stops if one is ever written.
# --------------------------------------------------------------------------
# Applies the language before first paint: a ?lang=vi link (remembered), a
# #vi / #en link (this page only), else the saved choice.
LANG_SCRIPT = ("try{var q=/[?&]lang=(en|vi)(?:&|$)/.exec(location.search),"
               "h=/^#(en|vi)\\b/.exec(location.hash),"
               "l=q?q[1]:h?h[1]:localStorage.getItem('sol-lang');"
               "if(l==='vi'||l==='en')document.documentElement.lang=l;"
               "if(q)localStorage.setItem('sol-lang',l)}catch(e){}")
KITCHEN_PRELOADS = [BN_ARORA_URL, '/assets/fonts/eb-garamond-latin-400-normal.woff2']
KITCHEN_TABS = [('about', '/about/', t('About', 'Giới thiệu')),
                ('menu', '/menu/', t('Menu', 'Thực đơn')),
                ('booking', '/booking/', t('Booking', 'Đặt bàn'))]


def kitchen_head(path, title, desc, extra):
    (title_en, title_vi), (desc_en, desc_vi) = title, desc
    lines = [
        '<!DOCTYPE html>',
        '<html lang="en" data-brand-fonts="%s">' % BRAND_FONTS,
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<script>%s</script>' % LANG_SCRIPT,
        '<title data-en="%s" data-vi="%s">%s</title>' % (title_en, title_vi, title_en),
        '<meta name="description" content="%s" data-en="%s" data-vi="%s">' % (desc_en, desc_en, desc_vi),
        '<link rel="preconnect" href="https://use.typekit.net" crossorigin>',
        '<link rel="preload" href="%s" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">' % TYPEKIT_KIT,
        '<noscript><link rel="stylesheet" href="%s"></noscript>' % TYPEKIT_KIT,
        '<link rel="stylesheet" href="/assets/fonts.css">',     # inlined by optimise()
        '<link rel="stylesheet" href="/assets/kitchen.css">',
        '<script src="/assets/kitchen.js" defer></script>',
    ] + ['<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' % f for f in KITCHEN_PRELOADS]
    lines += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Sol">',
        '<meta property="og:title" content="%s">' % title_en,
        '<meta property="og:description" content="%s">' % desc_en,
        '<meta property="og:url" content="%s">' % (SITE + path),
        '<meta property="og:locale" content="en_GB">',
        '<meta property="og:locale:alternate" content="vi_VN">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="theme-color" content="#f9e9d3">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        extra,
        '</head>',
    ]
    return '\n'.join(lines) + '\n'


def kitchen_lang_switch():
    return ('<div class="lang" role="group" %s><button type="button" data-set-lang="en" aria-pressed="true">EN</button>'
            '<span aria-hidden="true">·</span><button type="button" data-set-lang="vi" aria-pressed="false" lang="vi">VI</button></div>'
            % label('Language', 'Ngôn ngữ'))


def kitchen_header():
    tabs_shown = [tab for tab in KITCHEN_TABS if live(tab[0])] + ([('jobs', '/jobs/', JOBS_TAB)] if HIDE else [])

    def subtabs():
        return ''.join('<li><a href="%s">%s<span>%s</span></a></li>' % (href, name, sub)
                       for key, href, name, sub in MENU_TABS)

    def tabs(caret):
        return ''.join('<li><a href="%s"%s>%s%s</a></li>'
                       % (href, ' data-menu-link' if caret and key == 'menu' else '',
                          name, CARET if caret and key == 'menu' else '')
                       for key, href, name in tabs_shown)

    subnav = ('  <nav class="subnav" %s><div class="wrap"><ul>%s</ul></div></nav>\n'
              % (label('Menu sections', 'Các mục thực đơn'), subtabs())) if live('menu') else ''

    return """<header class="site-header" data-site-header>
  <div class="mbar">
    {lang}
    <a href="/" {home}>{logo_s}</a>
    <button class="burger" type="button" {open_l} aria-expanded="false" aria-controls="navsheet" data-sheet-open>{burger}</button>
  </div>
  <div class="masthead"><a href="/" {home}>{logo_l}</a></div>
  <div class="wrap">
    <nav class="navbar" {main_l}>
      {lang}
      <ul class="nav-links">{tabs}</ul>
    </nav>
  </div>
{subnav}</header>
<div class="navsheet" id="navsheet" role="dialog" aria-modal="true" {sheet_l} tabindex="-1" hidden>
  <div class="navsheet-top"><span></span><a href="/" {home}>{logo_s}</a>
    <button class="navsheet-close" type="button" {close_l} data-sheet-close>{close}</button></div>
  <ul class="navsheet-pages">{sheet_tabs}</ul>
  <div class="navsheet-foot">
    <div class="navsheet-meta"><span>{hours}</span>{lang}</div>
  </div>
</div>
""".format(lang=kitchen_lang_switch(), home=HOME_LABEL, logo_s=logo(74, 26), logo_l=logo(165, 58),
           open_l=label('Open navigation', 'Mở menu điều hướng'), burger=BURGER,
           main_l=label('Main', 'Điều hướng chính'), tabs=tabs(True), subnav=subnav,
           sheet_l=label('Navigation', 'Điều hướng'), sheet_tabs=tabs(False),
           close_l=label('Close navigation', 'Đóng menu điều hướng'), close=CLOSE, hours=HOURS_TAB)


def kitchen_footer():
    more = [(href, name) for key, href, name in KITCHEN_TABS if live(key)] + [
        ('/jobs/', JOBS_TAB), ('/privacy/', t('Privacy', 'Bảo mật'))]
    return """<footer class="site-footer">
  <div class="wrap"><div class="footer-inner">
    <a class="footer-logo" href="/" {home}>{logo}</a>
    <div class="footer-cols"><section><h2>{find}</h2><p>{addr}</p><p><a href="{maps}">{maps_t}</a></p></section><section><h2>{open}</h2><p>{days}</p><p>{hours}</p>{closed}</section><section><h2>{talk}</h2><p><a href="{tel}">{phone}</a></p><p><a href="mailto:{email}">{email}</a></p><p>{insta}</p></section><nav {more_l}><h2>{more_h}</h2><ul>{more}</ul></nav></div>
    <p class="legal">{legal}</p>
  </div></div>
</footer>
""".format(home=HOME_LABEL, logo=logo(91, 32), find=t('Find us', 'Tìm chúng tôi'),
           addr=t(ADDRESS_EN, ADDRESS_VI), maps=MAPS_URL, maps_t=MAPS_LINK_TEXT,
           open=t('Open', 'Giờ mở cửa'), days=HOURS_DAYS, hours=HOURS_SPAN,
           closed='<p>%s</p>' % HOURS_CLOSED if HOURS_CLOSED else '',
           talk=t('Talk to us', 'Liên hệ'), tel=PHONE_TEL, phone=PHONE, email=EMAIL,
           insta=INSTA_LINK, more_l=label('More', 'Thêm'), more_h=t('More', 'Thêm'),
           more=''.join('<li><a href="%s">%s</a></li>' % m for m in more),
           legal=t('© 2026 Công ty TNHH Aurelian · Tây Hồ, Hanoi',
                   '© 2026 Công ty TNHH Aurelian · Tây Hồ, Hà Nội'))


# ==========================================================================
# STRUCTURED DATA (home and Booking)
# ==========================================================================
def home_desc():
    """The home page's meta description, (English, Vietnamese), as SITE_STATE and
    OPENING_DATE stand when the site is built (search engines read this one)."""
    lead = ('Wood-fired pizza, pasta made in-house and 26 wines by the glass',
            'Pizza lò củi, mì Ý làm tại nhà hàng và 26 loại vang theo ly')
    if SITE_STATE == 'open':
        return ('%s at No 7, Lane 88 Quang An, Tây Hồ, Hanoi.' % lead[0],
                '%s, tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội.' % lead[1])
    if OPENING_DAY:
        return ('%s. Sol opens on %s at No 7, Lane 88 Quang An, Tây Hồ, Hanoi.' % (lead[0], en_date(OPENING_DAY)),
                '%s. Sol khai trương %s tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội.' % (lead[1], vi_date(OPENING_DAY)))
    return ('%s. Sol opens soon at No 7, Lane 88 Quang An, Tây Hồ, Hanoi.' % lead[0],
            '%s. Sol sắp khai trương tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội.' % lead[1])


HOME_DESC = home_desc()

RESTAURANT = {
    '@context': 'https://schema.org',
    '@type': 'Restaurant',
    '@id': 'https://sol.pizza/#restaurant',
    'name': 'Sol',
    'alternateName': 'Sol Hanoi',
    'url': 'https://sol.pizza/',
    'description': HOME_DESC[0],
    'servesCuisine': ['Italian-American', 'Pizza'],
    'priceRange': '$$',
    'image': 'https://sol.pizza/og-home.png',
    'logo': 'https://sol.pizza/favicon.svg',
    'email': EMAIL,
    'telephone': '+84866161600',
    'address': {
        '@type': 'PostalAddress',
        'streetAddress': 'No 7, Lane 88 Quang An Street',
        'addressLocality': 'Tây Hồ',
        'addressRegion': 'Hanoi',
        'addressCountry': 'VN',
    },
    'hasMenu': 'https://sol.pizza/menu/',
    'acceptsReservations': 'https://sol.pizza/booking/#book',
    'sameAs': [INSTAGRAM] + [u for _, u in SOCIAL],
    'parentOrganization': {'@type': 'Organization', 'name': COMPANY_VI},
}
# Opening hours from HOURS: once open, or from the opening day once it is set; none before.
if SITE_STATE == 'open' or OPENING_DATE:
    RESTAURANT['openingHoursSpecification'] = [dict(
        {'@type': 'OpeningHoursSpecification', 'dayOfWeek': [SCHEMA_DAYS[d] for d in HOURS['days']],
         'opens': HOURS['opens'], 'closes': HOURS['closes']},
        **({'validFrom': OPENING_DATE} if SITE_STATE != 'open' else {}))]
# These two point at the Menu and Booking pages: only while those are public.
if not live('menu'):
    del RESTAURANT['hasMenu']
if not live('booking'):
    del RESTAURANT['acceptsReservations']


def fit(text, most=160):
    """A description made from data (a summary, a role), cut at a word to fit search
    results (check_search() allows 200 at most, and notes over 160)."""
    if len(text) <= most:
        return text
    return text[:most - 1].rsplit(' ', 1)[0].rstrip(' ,.;:–—') + '…'


def ld(obj):
    """A JSON-LD block (structured data for search engines). Every < is escaped (still
    JSON), so nothing in the data can end the script or open a comment."""
    return ('<script type="application/ld+json">\n%s\n</script>\n'
            % json.dumps(obj, ensure_ascii=False, indent=1).replace('<', '\\u003c'))


ADDRESS_LD = {
    'en': {'@type': 'PostalAddress', 'streetAddress': 'No 7, Lane 88 Quang An Street', 'addressLocality': 'Tây Hồ',
           'addressRegion': 'Hanoi', 'addressCountry': 'VN'},
    'vi': {'@type': 'PostalAddress', 'streetAddress': 'Số 7, Ngõ 88 Quảng An', 'addressLocality': 'Tây Hồ',
           'addressRegion': 'Hà Nội', 'addressCountry': 'VN'},
}


def restaurant_ld(lang):
    """The restaurant, in the page's language: what search engines show for Sol (the
    name, address, hours once set, menu, booking, photos, the map pin once confirmed,
    Eclipse editions coming up)."""
    r = dict(RESTAURANT, url=SITE + lang_path('/', lang), description=HOME_DESC[LANGS.index(lang)],
             address=ADDRESS_LD[lang], currenciesAccepted='VND',
             hasMap=MAPS_URL.replace('&amp;', '&'), sameAs=[INSTAGRAM] + [u for _, u in SOCIAL])
    photos = [photo_url(p, 1600) for slot in ('home-hero', 'about-room', 'press') for p in photos_for(slot)]
    r['image'] = list(dict.fromkeys(photos))[:5] + [og_image('home', lang)]
    if GEO:
        r['geo'] = {'@type': 'GeoCoordinates', 'latitude': GEO[0], 'longitude': GEO[1]}
    if PAYMENT_ACCEPTED[0]:
        r['paymentAccepted'] = PAYMENT_ACCEPTED[LANGS.index(lang)]
    if 'hasMenu' in r:
        r['hasMenu'] = [{'@id': SITE + lang_path(p, lang) + '#menu'} for p in MENU_PATHS]
    if 'acceptsReservations' in r:
        r['acceptsReservations'] = SITE + lang_path('/booking/', lang)
    if live('events'):
        upcoming = [night for e in ev_upcoming() for night in event_ld(e, lang, alone=False)]
        if upcoming:
            r['event'] = upcoming
    return r


def schema(lang):
    return ld(restaurant_ld(lang))


def website_ld(lang):
    """The site's name for search results: Sol (and its other names)."""
    return ld({'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Sol',
               'alternateName': ['Sol Hanoi', 'sol.pizza'], 'url': SITE + '/', 'inLanguage': ['en', 'vi']})


# ==========================================================================
# HOME  /
# The hero (Book and the menu), then the opening date or today's hours, three ways
# in (Menu, Private dining, Events), the story in a few lines, the next Eclipse,
# press quotes once we have them, the newsletter, and a visit block to finish.
# ==========================================================================
def today_line():
    """Before opening: the opening date (or "soon"). Open: today's hours, worked out in
    the browser on Hanoi time (site.js, [data-today]); without it, the week's hours."""
    soon = t('Opening %s' % en_date(OPENING_DAY), 'Khai trương %s' % vi_date(OPENING_DAY)) if OPENING_DAY \
        else t('Opening soon', 'Sắp khai trương')
    today = ('<span data-today="%s">'
             '<span class="today-week">%s</span>'
             '<span class="today-open" hidden>%s</span>'
             '<span class="today-closed" hidden>%s</span></span>'
             % (','.join(str(d) for d in HOURS['days']), t(week_plain('en'), week_plain('vi')),
                t('Open today, %s' % HOURS_EN, 'Hôm nay mở cửa %s' % HOURS_VI),
                t('Closed today · %s' % week_plain('en'), 'Hôm nay nghỉ · %s' % week_plain('vi'))))
    return '<p class="today">%s</p>' % by_state(soon, today)


def week_plain(lang):
    return ('%s, %s' % (en_days(HOURS['days']), HOURS_EN) if lang == 'en'
            else '%s, %s' % (vi_days(HOURS['days']), HOURS_VI))


def home_paths():
    """Three ways in: the first three of these whose pages are public."""
    paths = [
        ('menu', '/menu/', t('Menu', 'Thực đơn'),
         t('Pizza from the wood oven, pasta made in-house and %d wines by the glass.' % WINES_GLASS,
           'Pizza từ lò củi, mì Ý làm tại nhà hàng và %d loại vang theo ly.' % WINES_GLASS),
         t('See the menu', 'Xem thực đơn')),
        ('private-dining', '/private-dining/', t('Private dining', 'Tiệc riêng'),
         t('Seven or more, or a night that’s all yours.',
           'Từ bảy người trở lên, hay một buổi tối chỉ dành riêng cho bạn.'),
         t('Tell us about it', 'Cho chúng tôi biết')),
        ('events', '/events/', t('Events', 'Sự kiện'), EV_SERIES, t('See what’s on', 'Xem lịch sự kiện')),
        ('visit', '/visit-us/', t('Visit', 'Ghé thăm'),
         t('No 7, Lane 88 Quang An, Tây Hồ: how to find us.', 'Số 7, ngõ 88 Quảng An, Tây Hồ: đường đến Sol.'),
         t('Find us', 'Tìm chúng tôi')),
    ]
    def photo(key):
        # The Visit card (it shows only when one of the first three is off) takes Visit's photo
        slot = 'visit' if key == 'visit' else 'home-' + key
        spec = (SLOTS['visit'][0],) + SLOTS['home-menu'][1:] if key == 'visit' else SLOTS[slot]
        p = next(iter(photos_for(slot)), None)
        return picture(p, spec) if p else (photo_placeholder(slot, spec) if FULL else '')
    cards = ['<li class="card">%s<div class="card-body"><h2>%s</h2><p>%s</p><a class="link-sc" href="%s">%s</a></div></li>'
             % (photo(key), name, line, href, link) for key, href, name, line, link in paths if live(key)][:3]
    return '<div class="wrap"><ul class="cards home-paths">%s</ul></div>' % ''.join(cards)


def next_event():
    """The next Eclipse, after dark: a block for each edition still to come, the head script
    showing the first that isn't over (html.next-<slug>; without JavaScript, the first)."""
    if not live('events'):
        return ''
    blocks = []
    for n, e in enumerate(ev_upcoming()):
        line = t(esc(e['summary_en']), esc(e['summary_vi'])) if e['ready'] else '%s %s' % (
            EV_SERIES, t('Details soon.', 'Thông tin chi tiết sẽ sớm được cập nhật.'))
        href = e['path'] if (e['ready'] or FULL) else '/events/'
        blocks.append('<section class="after-dark next-ev%s" data-ev="%s" aria-labelledby="s-next-%s"><div class="wrap '
                      'measure"><p class="eyebrow">Eclipse · %s</p><h2 class="h-lg" id="s-next-%s">%s</h2><p>%s</p>'
                      '<div class="actions"><a class="btn btn-red" href="%s">%s</a></div></div></section>'
                      % (' is-next' if n == 0 else '', e['slug'], e['slug'], ev_name(e), e['slug'], ev_dates(e), line,
                         href, t('More on Eclipse', 'Xem thêm về Eclipse')))
    return '\n'.join(blocks)


def build_home():
    opening = ''
    if SITE_STATE != 'open':
        when = t(en_date(OPENING_DAY, True), vi_date(OPENING_DAY)) if OPENING_DAY else t('Soon', 'Sắp tới')
        opening = '<div%s><dt>%s</dt><dd>%s</dd></div>' % (' class="when-pre"' if OPENING_DAY else '',
                                                          t('Opening', 'Khai trương'), when)
    facts = opening + ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % f for f in [
        (t('Where', 'Địa điểm'), t('Lane 88 Quang An, Tây Hồ', 'Ngõ 88 Quảng An, Tây Hồ')),
        (t('Kitchen', 'Bếp'), t('Wood-fired Italian-American', 'Lò củi, ẩm thực Ý–Mỹ')),
        (t('Hours', 'Giờ mở cửa'), HOURS_TAB),
    ])
    story = by_state(
        t('Sol Pizza closed last year. Sol opens on the same stretch of Tây Hồ with more room: '
          'a bigger kitchen, a proper bar and a Pavesi wood-fired oven built in Italy.',
          'Sol Pizza đã đóng cửa năm ngoái. Sol sẽ mở lại ngay trên con phố ấy ở Tây Hồ, với nhiều '
          'không gian hơn: căn bếp rộng hơn, một quầy bar đúng nghĩa và chiếc lò củi Pavesi chế '
          'tác tại Ý.'),
        t('Sol Pizza closed last year. Sol is open on the same stretch of Tây Hồ with more room: '
          'a bigger kitchen, a proper bar and a Pavesi wood-fired oven built in Italy.',
          'Sol Pizza đã đóng cửa năm ngoái. Sol đã mở cửa ngay trên con phố ấy ở Tây Hồ, với nhiều '
          'không gian hơn: căn bếp rộng hơn, một quầy bar đúng nghĩa và chiếc lò củi Pavesi chế '
          'tác tại Ý.'))
    press = gate('home-press', 'press or review quotes: the quote, who said it, where and when, and their OK to use it',
                 '<figure class="quote"><blockquote><p>%s</p></blockquote><figcaption>%s</figcaption></figure>'
                 % (t('[A quote from a review, to come]', '[Trích dẫn từ một bài đánh giá, sẽ cập nhật]'),
                    t('[Who, where, when]', '[Ai, ở đâu, khi nào]')))
    main = """<main id="main">
<section class="hero wrap">
  <p class="eyebrow">{eyebrow}</p>
  <h1 class="hero-title">{h1}</h1>
  <p class="hand hero-hand">{hand}</p>
  <div class="actions">{actions}</div>
  {today}
</section>
{hero_photo}
{paths}
<section class="home-story wrap{story_cls}" aria-labelledby="s-story">
  {story_photo}<div class="home-story-text"><header class="section-intro">{sun}<p class="eyebrow">{story_eyebrow}</p><h2 class="h-lg" id="s-story">{story_h}</h2><p>{story}</p></header>
  {story_link}</div>
</section>
{next_event}
<div class="wrap">{press}</div>
<div class="wrap">{news}</div>
<section class="home-visit wrap" aria-labelledby="s-visit">
  <header class="section-head">{sun2}<h2 id="s-visit">{visit_h}</h2></header>
  <dl class="facts">{facts}</dl>
  <div class="actions">{visit_actions}</div>
</section>
</main>
""".format(
        eyebrow=t('Italian-American · Tây Hồ, Hanoi', 'Ẩm thực Ý–Mỹ · Tây Hồ, Hà Nội'),
        # lang="vi": BN Arora has no Vietnamese letters, so site.css sets the name in Philosopher
        h1=t('Sol is back in <span lang="vi">Tây Hồ</span>.', 'Sol trở lại Tây Hồ.'),
        hand=t('sunshine, after dark', 'ánh nắng, sau hoàng hôn'),
        # Book a table and See the menu; while those pages aren't public, See open
        # roles and Instagram
        actions=buttons([('booking', '/booking/', BOOK), ('menu', '/menu/', t('See the menu', 'Xem thực đơn')),
                         (None, '/jobs/', SEE_ROLES), (None, INSTAGRAM, INSTA_TEXT)]),
        today=today_line(),
        # the first picture: as wide as the window, loaded first, never faded in
        hero_photo=band('home-hero', 'band band-hero', eager=True),
        paths=home_paths(),
        story_photo=band('home-story', 'home-story-photo'),
        story_cls=' has-photo' if photos_for('home-story') or FULL else '',
        sun=sun(2), story_eyebrow=t('Our story', 'Câu chuyện của chúng tôi'),
        story_h=t('We closed Sol Pizza to build Sol.', 'Chúng tôi đóng cửa Sol Pizza để xây dựng Sol.'),
        story=story,
        story_link=('<p class="home-story-link"><a class="link-sc" href="/about/">%s</a></p>'
                    % t('Read our story', 'Đọc câu chuyện của chúng tôi') if live('about') else ''),
        next_event=next_event(),
        press=press,
        news=newsletter('home-news offer', 'btn btn-red'),
        sun2=sun(6), visit_h=t('Visit', 'Ghé thăm'),
        facts=facts,
        visit_actions=''.join([
            '<a class="btn btn-outline" href="%s" data-track="directions_click">%s</a>' % (DIRECTIONS_URL, DIRECTIONS),
            ('<a class="btn btn-outline" href="/visit-us/">%s</a>' % t('Hours and address', 'Giờ mở cửa và địa chỉ')
             if live('visit') else '')]),
    )
    return page('/', 'page-home',
                ('Sol — Italian-American restaurant in Tây Hồ, Hanoi',
                 'Sol — Nhà hàng Ý–Mỹ tại Tây Hồ, Hà Nội'),
                HOME_DESC, main, og='home', extra=[preload('home-hero'), schema, website_ld], news=False)


# ==========================================================================
# MENU  /menu/  /menu/wine/  /menu/bar/   (from build/menu-data.json)
# ==========================================================================
MENU_EYEBROW = t('Menu', 'Thực đơn')
TAGS_VI = MENU['food']['tag_labels_vi']
MARKS_VI = {lg['mark']: lg['mark_vi'] for lg in MENU['wine']['legend']}


# The food characters, each beside the page title of what it shows: (file, width, height).
# Fixed-colour SVGs, used as supplied (never recoloured, stretched or redrawn),
# on the cream page only: never on red or wood brown. 32–96px.
TOMATOES = ('tomatoes.svg', 96, 52)     # Food
GRAPE    = ('grape.svg', 53, 88)        # Wine


def page_title(eyebrow, h1, lead, art=None):
    title = '<h1>%s</h1>' % h1
    if art:
        img, w, h = art
        title = ('<div class="title-art" style="--art-w:%dpx"><h1>%s</h1><img src="/assets/%s" alt="" '
                 'width="%d" height="%d"></div>' % (w, h1, img, w, h))
    return ('<header class="page-title"><p class="eyebrow">%s</p>%s<p class="page-lead">%s</p></header>'
            % (eyebrow, title, lead))


def note_box(label_html, text):
    return '<aside class="note-box"><p class="label">%s</p><p>%s</p></aside>' % (label_html, text)


# Prices (menu-data.json): whole đồng, written 185,000 on English pages and 185.000 on
# Vietnamese ones, the currency said once at the top of the page. A page's "A first
# draft" note goes once every item on it has its price.
MENU_UPDATED = date.fromisoformat(MENU['updated']) if MENU.get('updated') else None
for _sec in [x for k in ('food', 'bar') for x in MENU[k]['sections']]:
    for _d in _sec['items']:
        assert _d.get('price') is None or (type(_d['price']) is int and _d['price'] > 0), \
            'menu-data.json: %s: price is whole đồng (185000)' % _d['name']
for _sec in MENU['wine']['sections']:
    for _w in _sec['items']:
        assert all(_w.get(k) is None or (type(_w[k]) is int and _w[k] > 0) for k in ('glass', 'bottle')), \
            'menu-data.json: %s: glass and bottle are whole đồng' % _w['name']
        assert not _w.get('glass') or 'glass' in _w['marks'], \
            'menu-data.json: %s: a glass price, but it isn\'t marked "glass"' % _w['name']


def price_tag(d):
    """A dish's or drink's price, after its name."""
    return '<span class="price">%s</span>' % t(vnd(d['price'], ','), vnd(d['price'], '.')) if d.get('price') else ''


def wine_price(w):
    """A wine's prices, by the glass and the bottle, under its details."""
    parts = ([t('glass %s' % vnd(w['glass'], ','), 'ly %s' % vnd(w['glass'], '.'))] if w.get('glass') else []) + \
            ([t('bottle %s' % vnd(w['bottle'], ','), 'chai %s' % vnd(w['bottle'], '.'))] if w.get('bottle') else [])
    return '<p class="item-price">%s</p>' % ' · '.join(parts) if parts else ''


def priced(items, wine=False):
    """(any item priced, every item priced)"""
    has = [bool(w.get('glass') or w.get('bottle')) if wine else bool(w.get('price')) for w in items]
    return any(has), all(has)


def currency_note():
    return '<p class="currency">%s</p>' % t('Prices in Vietnamese đồng (VND).', 'Giá tính bằng đồng (VND).')


def menu_section(sec, sun_n, body):
    sid = 's-' + slug(sec['name'])
    intro = sec.get('intro', '')
    intro_html = '<p>%s</p>' % t(esc(intro), esc(sec.get('intro_vi') or intro)) if intro else ''
    return ('<section class="menu-section" aria-labelledby="%s"><header class="section-head">%s'
            '<h2 id="%s">%s</h2>%s</header>%s</section>'
            % (sid, sun(sun_n), sid, t(esc(sec['name']), esc(sec.get('name_vi') or sec['name'])),
               intro_html, body))


def item(name, desc, desc_vi, after_name='', cls='', price='', price_line=''):
    """A dish, drink or wine. price: after the name and its marks (price_tag()), at the
    line's end; price_line: under the details (wine_price())."""
    if price:
        li = ('<li%s><p class="item-name has-price"><span>%s%s</span> %s</p>'
              % (cls, esc(name), after_name, price))
    else:
        li = '<li%s><p class="item-name">%s%s</p>' % (cls, esc(name), after_name)
    if desc:
        li += '<p class="item-desc">%s</p>' % t(esc(desc), esc(desc_vi or desc))
    return li + price_line + '</li>'


def good_to_know(drinks=False):
    """Allergies and the house rules, at the foot of each menu page. drinks: the wine and
    bar pages, which add the line on alcohol (Law 44/2019 on alcohol)."""
    g = MENU['good_to_know']
    rules = list(zip(g['rules'], g['rules_vi'])) + ([(g['drinks'], g['drinks_vi'])] if drinks else [])
    updated = ('<p class="menu-updated">%s</p>' % t('Menu updated %d %s %d.' % (
        MENU_UPDATED.day, EN_MONTHS[MENU_UPDATED.month - 1], MENU_UPDATED.year),
        'Thực đơn cập nhật ngày %02d/%02d/%d.' % (MENU_UPDATED.day, MENU_UPDATED.month, MENU_UPDATED.year))
        if MENU_UPDATED else '')
    return ('<section class="good-to-know" %s><div><h2>%s</h2><p>%s</p></div><div><h2>%s</h2><ul>%s</ul></div></section>%s'
            % (label('Good to know', 'Thông tin hữu ích'), t('Allergies', 'Dị ứng thực phẩm'),
               t(esc(g['allergies']), esc(g['allergies_vi'])), t('Good to know', 'Thông tin hữu ích'),
               ''.join('<li>%s</li>' % t(esc(en), esc(vi)) for en, vi in rules), updated))


MENU_PATHS = ('/menu/', '/menu/wine/', '/menu/bar/')


def menu_ld(key, path, lang):
    """A menu page as a Menu: its sections and items, in the page's language, with each
    price once set (VND), and Veg as a vegetarian diet."""
    vi = lang == 'vi'
    data = MENU[key]

    def offers(d):
        if key == 'wine':
            return [{'@type': 'Offer', 'price': str(d[k]), 'priceCurrency': 'VND', 'name': name}
                    for k, name in (('glass', 'ly' if vi else 'glass'), ('bottle', 'chai' if vi else 'bottle'))
                    if d.get(k)]
        return [{'@type': 'Offer', 'price': str(d['price']), 'priceCurrency': 'VND'}] if d.get('price') else []

    sections = []
    for sec in data['sections']:
        items = []
        for d in sec['items']:
            field = 'details' if key == 'wine' else 'description'
            text = (d.get(field + '_vi') or d.get(field)) if vi else d.get(field)
            it = {'@type': 'MenuItem', 'name': d['name']}
            if text:
                it['description'] = text
            if offers(d):
                it['offers'] = offers(d)
            if 'Veg' in d.get('tags', []):
                it['suitableForDiet'] = 'https://schema.org/VegetarianDiet'
            items.append(it)
        sections.append({'@type': 'MenuSection', 'name': (sec.get('name_vi') or sec['name']) if vi else sec['name'],
                         'hasMenuItem': items})
    name = {'food': ('Food', 'Món ăn'), 'wine': ('Wine', 'Vang'), 'bar': ('Bar', 'Quầy bar')}[key][1 if vi else 0]
    return ld({'@context': 'https://schema.org', '@type': 'Menu', '@id': SITE + lang_path(path, lang) + '#menu',
               'name': 'Sol: %s' % name, 'url': SITE + lang_path(path, lang), 'inLanguage': lang,
               'hasMenuSection': sections})


def menu_page(path, key, body_class, title, desc, main, og):
    return page(path, body_class + ' section-menu', title, desc, '<main id="main" class="wrap">\n' + main + '\n</main>\n',
                cur=key, og=og, body_attrs=' data-menu="%s"' % key, extra=lambda lang: menu_ld(key, path, lang))


def build_food():
    food = MENU['food']
    some, every = priced([d for sec in food['sections'] for d in sec['items']])
    # The marks that need explaining, in each language: Veg is vegetarian (Chay and Cay,
    # and Spicy, say it already)
    legend = ''.join(
        '<p class="legend" data-l="%s" lang="%s">%s</p>' % (lang, lang, items) for lang, items in (
            ('en', ''.join('<span><b>%s</b>%s</span>' % (tag, m) for tag, m in food['tag_meaning'].items()
                           if m.lower() != tag.lower())),
            ('vi', ''.join('<span><b>%s</b>%s</span>' % (TAGS_VI.get(tag, tag), m)
                           for tag, m in food['tag_meaning_vi'].items() if m.lower() != TAGS_VI.get(tag, tag).lower())))
        if items)
    parts = [
        page_title(MENU_EYEBROW, t('What we’re cooking', 'Chúng tôi nấu gì'),
                   t('Pizza from the wood oven, pasta made in-house and small plates to start.',
                     'Pizza từ lò củi, mì Ý làm tại nhà hàng và món khai vị để mở đầu.'), TOMATOES),
        legend,
        currency_note() if some else '',
    ]
    parts.append('<div class="menu-photos">%s</div>' % gallery('menu-food', eager=True)
                 if photos_for('menu-food') or FULL else '')
    if not every:
        parts.append(note_box(t('A first draft', 'Bản nháp đầu tiên'),
                 t('These are the dishes we cooked at Sol Pizza, and they’re where Sol starts. Expect '
                   'changes as the new kitchen settles in%s.' % ('' if some else ', and prices here once they’re set'),
                   'Đây là những món chúng tôi từng nấu tại Sol Pizza, và là điểm khởi đầu của Sol. '
                   'Các món sẽ còn thay đổi khi căn bếp mới đi vào nếp%s.'
                   % ('' if some else ', và giá sẽ được đăng ở đây khi đã chốt'))))
    for i, sec in enumerate(food['sections']):
        items = ''.join(
            item(d['name'], d['description'], d.get('description_vi'),
                 ''.join('&ensp;<span class="tag">%s</span>' % t(tag, TAGS_VI.get(tag, tag)) for tag in d['tags']),
                 price=price_tag(d))
            for d in sec['items'])
        parts.append(menu_section(sec, 1 + i, '<ul class="menu-grid">%s</ul>' % items))
    top = food['toppings']
    parts.append(menu_section(
        {'name': 'Toppings', 'name_vi': 'Topping thêm', 'intro': top['intro'], 'intro_vi': top['intro_vi']},
        1 + len(food['sections']),
        '<p class="inline-list">%s</p>' % t(' · '.join(esc(x) for x in top['items']),
                                            ' · '.join(esc(x) for x in top['items_vi']))))
    parts.append(good_to_know())
    return menu_page('/menu/', 'food', 'page-menu-food',
                     ('Menu — Sol, Tây Hồ', 'Thực đơn — Sol, Tây Hồ'),
                     ('Pizza from the Pavesi wood oven, pasta made in-house and small plates to start.',
                      'Pizza từ lò củi Pavesi, mì Ý làm tại nhà hàng và món khai vị để mở đầu.'),
                     '\n'.join(parts), 'menu')


def wine_count_line(wines):
    n, g = len(wines), sum('glass' in w['marks'] for w in wines)
    en = '%d wine%s' % (n, '' if n == 1 else 's')
    vi = '%d loại vang' % n
    if g:
        en += ', %d by the glass' % g
        vi += ', %d loại theo ly' % g
    return t(en, vi)


def build_wine():
    wine = MENU['wine']
    some, every = priced([w for sec in wine['sections'] for w in sec['items']], wine=True)
    legend = ''.join('<span><b>%s</b>%s</span>' % (t(lg['mark'], lg['mark_vi']), t(lg['meaning'], lg['meaning_vi']))
                     for lg in wine['legend'])
    parts = [
        page_title(MENU_EYEBROW, t('The wine list', 'Danh sách vang'),
                   t('Thirty wines, from Burgundy and Tuscany to Moldova and the Czech Republic. '
                     'Twenty-six of them are open by the glass.',
                     'Ba mươi loại vang, từ Bourgogne và Toscana đến Moldova và Cộng hòa Séc. '
                     'Hai mươi sáu loại trong số đó có phục vụ theo ly.'), GRAPE),
        '<p class="legend">%s</p>' % legend,
        currency_note() if some else '',
        band('menu-wine', eager=True),
        '' if every else note_box(t('A first draft', 'Bản nháp đầu tiên'),
                 t('This is the Sol Pizza list while the new one is being built. Vintages change and '
                   'bottles run out, so ask what’s open tonight.',
                   'Đây là danh sách của Sol Pizza trong lúc danh sách mới đang được xây dựng. Niên '
                   'vụ thay đổi, chai có thể hết, nên hãy hỏi xem tối nay có những chai nào đang mở.')),
    ]
    for i, sec in enumerate(wine['sections']):
        rows = []
        for w in sec['items']:
            marks = ''
            if w['marks']:
                marks = '&ensp;<span class="marks">%s</span>' % t(' · '.join(w['marks']),
                                                              ' · '.join(MARKS_VI[m] for m in w['marks']))
            rows.append(item(w['name'], w['details'], w.get('details_vi'), marks, ' class="wine"',
                             price_line=wine_price(w)))
        sid = 's-' + slug(sec['name'])        # the count line stands in for an intro
        parts.append('<section class="menu-section" aria-labelledby="%s"><header class="section-head">%s'
                     '<h2 id="%s">%s</h2><p>%s</p></header><ul class="menu-grid">%s</ul></section>'
                     % (sid, sun(3 + i), sid, t(esc(sec['name']), esc(sec['name_vi'])),
                        wine_count_line(sec['items']), ''.join(rows)))
    parts += [
        '<section class="offer" aria-labelledby="wine-night"><h2 id="wine-night">%s</h2><p class="hand">%s</p><p>%s</p></section>'
        % (t('Wine night', 'Đêm vang'), t('every Thursday', 'thứ Năm hằng tuần'),
           t('50% off every wine by the glass.', 'Giảm 50% mọi loại vang theo ly.')),
        '<section class="closing"><h2>%s</h2><p>%s</p></section>'
        % (t('Can’t see what you like?', 'Chưa thấy chai bạn thích?'),
           t('Tell us what you drink and roughly what you’d like to spend, and we’ll find you '
             'something.%s' % ('' if every else ' Prices are on the printed list in the room.'),
             'Hãy cho chúng tôi biết bạn thích uống gì và tầm giá mong muốn, chúng tôi sẽ tìm cho '
             'bạn một chai phù hợp.%s' % ('' if every else ' Giá có trên danh sách in tại nhà hàng.'))),
        good_to_know(drinks=True),
    ]
    return menu_page('/menu/wine/', 'wine', 'page-menu-wine',
                     ('Wine list — Sol, Tây Hồ', 'Danh sách vang — Sol, Tây Hồ'),
                     ('Thirty wines, twenty-six of them by the glass, from Burgundy and Tuscany to '
                      'Moldova and the Czech Republic. Wine night every Thursday.',
                      'Ba mươi loại vang, hai mươi sáu loại có theo ly, từ Bourgogne và Toscana đến '
                      'Moldova và Cộng hòa Séc. Đêm vang vào thứ Năm hằng tuần.'),
                     '\n'.join(parts), 'wine')


def build_bar():
    bar = MENU['bar']
    some, _ = priced([d for sec in bar['sections'] for d in sec['items']])
    parts = [page_title(MENU_EYEBROW, t('The bar', 'Quầy bar'),
                        t('Cocktails, Bia Craft on draft, sake and everything else. It’s a full bar, '
                          'so ask for anything.',
                          'Cocktail, bia tươi Bia Craft, sake và mọi thứ còn lại. Quầy bar đầy đủ, '
                          'bạn cứ gọi món mình thích.')),
             currency_note() if some else '', band('menu-bar', eager=True)]
    for i, sec in enumerate(bar['sections']):
        if all(not d['description'] for d in sec['items']) and sec['name'] == 'Soft drinks' \
                and not any(d.get('price') for d in sec['items']):
            body = '<p class="inline-list">%s</p>' % ' · '.join(esc(d['name']) for d in sec['items'])
        else:
            body = '<ul class="menu-grid">%s</ul>' % ''.join(
                item(d['name'], d['description'], d.get('description_vi'), price=price_tag(d)) for d in sec['items'])
        parts.append(menu_section(sec, 5 + i, body))
    parts += [
        '<section class="offer" aria-labelledby="happy-hour"><h2 id="happy-hour">%s</h2><p class="hand">%s</p><p>%s</p></section>'
        % ('Happy hour', t('5–7pm', '17:00 – 19:00'),
           t('Tuesday to Sunday: 50% off house wine, sake and draft beer.',
             'Thứ Ba đến Chủ Nhật: giảm 50% vang quán, sake và bia tươi.')),
        good_to_know(drinks=True),
    ]
    return menu_page('/menu/bar/', 'bar', 'page-menu-bar',
                     ('Bar — Sol, Tây Hồ', 'Quầy bar — Sol, Tây Hồ'),
                     ('Cocktails, Bia Craft on draft, sake and soft drinks. Happy hour 5–7pm, Tuesday '
                      'to Sunday.',
                      'Cocktail, bia tươi Bia Craft, sake và đồ uống không cồn. Happy hour 17:00 – '
                      '19:00, từ thứ Ba đến Chủ Nhật.'),
                     '\n'.join(parts), 'menu')


# ==========================================================================
# ABOUT  /about/   the restaurant introduction (/story/ redirects here)
# Copy that was on home and /story/, in this order: "What Sol is" (its heading
# is the page title), the three boxes, the home pull quote, then the Story page
# as it was, under one heading.
# ==========================================================================
def prose_section(sid, sun_n, heading, paras, style='', level=2, cls=''):
    return ('<section class="prose-section wrap" aria-labelledby="%s"%s><header class="section-head">%s'
            '<h%d id="%s">%s</h%d></header><div class="prose%s">%s</div></section>'
            % (sid, style, sun(sun_n), level, sid, heading, level, cls, ''.join(paras)))


def build_about():
    # Heading and text only: the Envoy (wood brown) and the food characters (Sol
    # red) can't share a row, and neither may be recoloured.
    trio = [
        (t('The oven', 'Lò nướng'),
         t('A Pavesi wood-fired oven, built in Italy and shipped to Tây Hồ. Slow-fermented dough, '
           'baked fast over real fire.',
           'Lò củi Pavesi, chế tác tại Ý và đưa về Tây Hồ. Bột ủ chậm, nướng nhanh trên lửa thật.')),
        (t('The room', 'Không gian'),
         t('Two floors, under 200 square metres. A bar you can eat at, and a terrace for when the '
           'weather behaves.',       # CONFIRM: there is a terrace
           'Hai tầng, dưới 200 mét vuông, quầy bar có thể ngồi ăn và một khoảng hiên cho những '
           'ngày Hà Nội dịu trời.')),
        (t('The table', 'Bàn ăn'),
         t('Italian-American means generous: plates for the middle of the table, and nobody '
           'counting slices.',
           'Ẩm thực Ý–Mỹ nghĩa là hào phóng. Món đặt giữa bàn, và không ai phải đắn đo.')),
    ]
    intro = [
        t('Italian-American food began with immigrants: Italian technique, American appetite and '
          'whatever the market had that morning. Ours has Đà Lạt spinach and Phú Quốc pepper in '
          'it, and imported flour, cheese and tomatoes we won’t compromise on.',
          'Ẩm thực Ý–Mỹ bắt đầu từ những người nhập cư: kỹ thuật Ý, khẩu vị Mỹ và bất cứ thứ gì '
          'chợ có vào sáng hôm đó. Món của chúng tôi có rau chân vịt Đà Lạt, tiêu Phú Quốc, cùng '
          'bột mì, phô mai và cà chua nhập khẩu — những nguyên liệu chúng tôi không bao giờ thỏa '
          'hiệp về chất lượng.'),
    ]
    # Until we open; with an OPENING_DATE it goes by itself on the day (by_state()).
    if SITE_STATE != 'open':
        intro.append((t('We’re still building: the oven is in and the team is coming together. Underneath it '
                        'all is one rule — food quality is non-negotiable.',
                        'Chúng tôi vẫn đang hoàn thiện: lò đã về và đội ngũ đang dần đầy đủ. Nền tảng của tất cả '
                        'là một nguyên tắc — chất lượng món ăn là điều không thể thỏa hiệp.'),
                      ' when-pre' if OPENING_DATE else ''))
    intro = [x if isinstance(x, tuple) else (x, '') for x in intro]
    # "Build it with us" while a hiring round is open (build/jobs-data.json); the head
    # script (ROUND_SCRIPT) takes it off at the round's closing instant.
    join = ''
    if datetime.now().astimezone() < CLOSES:
        join = ('<div class="wrap round-live"><section class="offer" aria-labelledby="s-join"><h3 id="s-join">%s</h3>'
                '<p>%s</p><a class="btn btn-red" href="/jobs/">%s</a></section></div>' % (
                    t('Build it with us', 'Cùng chúng tôi dựng nên Sol'),
                    t('We’re hiring for the kitchen and the floor before we open. If you want to be on the '
                      'first team in the new room, start here.',
                      'Chúng tôi đang tuyển cho cả bếp và khu phục vụ trước ngày khai trương. Nếu bạn muốn là '
                      'một phần của đội ngũ đầu tiên, các vị trí đang mở ở đây.'),
                    SEE_ROLES))
    main = '\n'.join([
        '<main id="main">',
        '<div class="wrap"><header class="page-title"><p class="eyebrow">%s</p><h1>%s</h1>%s</header></div>' % (
            t('What Sol is', 'Sol là gì'),
            t('A neighbourhood restaurant built around pizza.',
              'Một nhà hàng của khu phố, lấy pizza làm trung tâm.'),
            ''.join('<p class="page-lead%s">%s</p>' % (cls, p) for p, cls in intro)),
        '<div class="wrap"><ul class="trio">%s</ul></div>' % ''.join(
            '<li><h2>%s</h2><p>%s</p></li>' % box for box in trio),
        band('about-room', 'band wrap-wide'),
        '<figure class="pullquote wrap">%s<blockquote><p>%s</p></blockquote>%s</figure>' % (
            sun(2),
            t('We’d rather cook a short menu well than a long one adequately.',
              'Chúng tôi thà nấu ít món cho thật ngon, còn hơn nhiều món mà tàm tạm.'),
            sun(6)),
        # The story, under one heading: its sections are h3s.
        '<section class="story" aria-labelledby="s-story">',
        '<div class="wrap"><header class="section-intro"><p class="eyebrow">%s</p><h2 class="h-lg" id="s-story">%s</h2><p>%s</p></header></div>' % (
            t('Our story', 'Câu chuyện của chúng tôi'),
            t('We closed Sol Pizza to build Sol.', 'Chúng tôi đóng cửa Sol Pizza để xây dựng Sol.'),
            t('Sol Pizza ran in Tây Hồ until last year. Sol is everything it taught us, with the room '
              'to do it properly.',
              'Sol Pizza hoạt động ở Tây Hồ cho đến năm ngoái. Sol là những gì chúng tôi học được từ '
              'đó, với đủ không gian để làm cho tử tế.')),
        prose_section('s-sol-pizza', 1, 'Sol Pizza', [
            '<p>%s</p>' % t(
                'We ran Sol Pizza until we could see what it wanted to become — and that the room '
                'wouldn’t let it. A small kitchen sets a hard ceiling. So does an oven that’s nearly right.',
                'Chúng tôi vận hành Sol Pizza cho đến khi nhìn thấy rõ nó muốn trở thành điều gì — và '
                'rằng không gian đó không cho phép. Một căn bếp nhỏ đặt ra giới hạn cứng. Một chiếc lò '
                'gần đúng cũng vậy.'),
            '<p>%s</p>' % t('Closing was the harder decision, and the right one.',
                            'Đóng cửa là quyết định khó khăn hơn, và là quyết định đúng.'),
            gate('about-closing', 'a line or two on what closing Sol Pizza meant to Arman and the team',
                 '<p>%s</p>' % t('[What closing Sol Pizza meant to us, to come]',
                                 '[Việc đóng cửa Sol Pizza có ý nghĩa thế nào với chúng tôi, sẽ cập nhật]')),
        ], level=3),
        # The Solar Envoy, once on the page: large and faint behind the text about the
        # building and its oven (site.css).
        prose_section('s-the-building', 2, t('The building', 'Tòa nhà'), [
            '<img class="envoy" src="/assets/envoy-at-the-oven.svg" alt="" width="150" height="225" loading="lazy">',
            '<p>%s</p>' % t(
                'Sol takes the first two floors of a building on Quang An — under 200 square metres, '
                'small enough to run properly and big enough for what the old place couldn’t do.',
                'Sol chiếm hai tầng đầu của một tòa nhà trên phố Quảng An — dưới 200 mét vuông, đủ '
                'nhỏ để vận hành chỉn chu và đủ lớn để làm những điều nơi cũ không thể.'),
            '<p>%s</p>' % t(
                'At its centre is a Pavesi wood-fired oven, built in Italy and shipped to Hanoi. The '
                'rest of the kitchen is arranged around it.',
                'Trung tâm của tất cả là chiếc lò củi Pavesi, chế tác tại Ý và đưa về Hà Nội. Mọi thứ '
                'còn lại trong bếp đều được sắp xếp quanh nó.'),
        ], level=3, cls=' has-envoy'),
        band('about-oven', 'band wrap-wide'),
        gate('about-dough', 'the kitchen’s lines on the dough: its flours, how long it ferments, how it’s baked',
             prose_section('s-the-dough', 3, t('The dough', 'Bột bánh'), [
                 '<p>%s</p>' % t('[The flours, the fermentation and the bake, in the kitchen’s words, to come]',
                                 '[Bột mì, thời gian ủ và cách nướng, theo lời của bếp, sẽ cập nhật]')], level=3)),
        '<figure class="pullquote wrap">%s<blockquote><p>%s</p></blockquote>%s</figure>' % (
            sun(4),
            t('A restaurant is a room, a team and a menu. Get the room right and the other two get easier.',
              'Một nhà hàng là một không gian, một đội ngũ và một thực đơn. Làm đúng không gian, hai '
              'điều còn lại sẽ dễ hơn.'),
            sun(7)),
        # CONFIRM: ships without Long; Arman to say whether to add "and Long runs the floor."
        prose_section('s-team', 8, t('The team', 'Đội ngũ'), [
            '<p style="text-align:center">%s</p>' % t('Ngọc runs the kitchen.', 'Ngọc phụ trách bếp.'),
            gate('about-team', 'a portrait and two or three lines on each person, in English and Vietnamese',
                 '<ul class="cards team-cards">%s</ul>' % ''.join(
                     '<li class="card"><div class="ph" style="aspect-ratio:4/5">%s</div><div class="card-body">'
                     '<h4>%s</h4><p>%s</p></div></li>' % (t('Portrait', 'Chân dung'), name, t('[A few lines, to come]',
                                                                                             '[Vài dòng giới thiệu, sẽ cập nhật]'))
                     for name in ('Ngọc', t('[Name]', '[Tên]'), t('[Name]', '[Tên]')))),
        ], style=' style="margin-top:0"', level=3),
        join,
        '</section>',
        '</main>', ''])
    return page('/about/', 'page-about',
                ('About — Sol, Tây Hồ', 'Giới thiệu — Sol, Tây Hồ'),
                ('We closed Sol Pizza to build Sol: a bigger kitchen, a proper bar and a Pavesi '
                 'wood-fired oven on Quang An.',
                 'Chúng tôi đóng cửa Sol Pizza để xây dựng Sol: căn bếp rộng hơn, một quầy bar đúng '
                 'nghĩa và lò củi Pavesi trên phố Quảng An.'),
                main, cur='about', og='story', extra=ROUND_SCRIPT if join else '')


# ==========================================================================
# BOOKING  /booking/   the booking box: where every Book button leads (/booking/#book)
# VISIT    /visit-us/  hours, address, contact and good to know
# (/visit/ redirects to /booking/: browsers cache that 301, so Visit has a new address)
# ==========================================================================
def from_opening():
    """", from the day we open" while we're not open yet (English, Vietnamese)."""
    return ((', from the day we open', ', kể từ ngày khai trương') if SITE_STATE != 'open' else ('', ''))


def mailform(kind, subject, fields, submit):
    """A form that writes an email, for an enquiry (no server keeps it): the guest's email
    app opens with the details filled in, to ENQUIRIES, the subject in English (the inbox
    is sorted by it) and the details in the page's language (site.js builds it, and fires
    enquiry_submit). Without JavaScript, just the address to write to.
    The address is always on the form too, for a computer with no email app, and after
    Send the message is on the page to copy.
    fields: (name, label, type, required); type is an <input> type or 'textarea'."""
    rows = []
    for name, text, kind_, required in fields:
        fid = 'f-%s-%s' % (kind, name)
        auto = {'name': ' autocomplete="name"', 'phone': ' autocomplete="tel"', 'email': ' autocomplete="email"'}
        attrs = '%s%s%s' % (' required' if required else '', auto.get(name, ''),
                            ' min="1" inputmode="numeric"' if kind_ == 'number' else '')
        control = ('<textarea id="%s" name="%s" rows="3"%s></textarea>' % (fid, name, attrs) if kind_ == 'textarea'
                   else '<input id="%s" name="%s" type="%s"%s>' % (fid, name, kind_, attrs))
        rows.append('<div class="field%s"><label for="%s"><span class="field-name">%s</span>%s</label>%s</div>'
                    % (' field-wide' if kind_ == 'textarea' else '', fid, text,
                       '' if required else ' <span class="opt">%s</span>' % t('(optional)', '(không bắt buộc)'),
                       control))
    mail = '<a href="mailto:%s">%s</a>' % (ENQUIRIES, ENQUIRIES)
    # No action: site.js writes the email. (A mailto: action is "mixed content" to
    # browsers, and sends forms garbled.) Without JavaScript (rare) the fields stay
    # hidden and the note gives the address (site.css: html:not(.js)); onsubmit stops a
    # form ever sending itself to the page, should site.js fail to load.
    return ('<form class="mailform" onsubmit="return false" '
            'data-mailform="%s" data-category="%s" data-to="%s" data-subject="%s">'
            '<div class="mailform-fields">%s</div>'
            '<div class="actions"><button class="btn btn-red" type="submit">%s</button></div>'
            '<p class="mailform-note">%s</p>'
            '<div class="mailform-done" hidden><p tabindex="-1">%s</p><textarea readonly rows="8" %s></textarea></div>'
            '</form>'
            % (kind, esc_attr(subject.rstrip(' —')), ENQUIRIES, esc_attr(subject), ''.join(rows), submit,
               t('This opens your email app with the details filled in: send it from there. Or write to us at %s.' % mail,
                 'Nút này mở ứng dụng email với nội dung đã điền sẵn: bạn chỉ cần gửi đi. Hoặc viết cho chúng tôi '
                 'qua %s.' % mail),
               t('Your email app should have opened with your message. If it didn’t, copy the message below and '
                 'send it to %s.' % mail,
                 'Ứng dụng email của bạn lẽ ra đã mở với nội dung điền sẵn. Nếu chưa thấy, hãy sao chép nội dung dưới '
                 'đây và gửi tới %s.' % mail),
               label('Your message', 'Nội dung email')))


def groups_line():
    """Seven or more: to the group enquiry on /private-dining/ while that page is public,
    else by email."""
    if live('private-dining'):
        return t('Seven or more? <a href="/private-dining/#enquire">Tell us about your group</a> and we’ll look '
                 'after you personally.',
                 'Nhóm từ bảy người trở lên? <a href="/private-dining/#enquire">Hãy cho chúng tôi biết về nhóm của '
                 'bạn</a>, chúng tôi sẽ sắp xếp riêng.')
    return t('Seven or more? Email us and we’ll look after you personally.',
             'Nhóm từ bảy người trở lên: vui lòng gửi email, chúng tôi sẽ sắp xếp riêng cho bạn.')


def build_booking():
    if RESDIARY_URL:
        booking_p = t('Book online below, or call or email us.',
                      'Đặt bàn trực tuyến ngay bên dưới, hoặc gọi điện hay gửi email cho chúng tôi.')
        contact = [('<a href="%s" data-track="call_click">%s</a>' % (PHONE_TEL, PHONE)),
                   ('<a href="mailto:%s">%s</a>' % (EMAIL, EMAIL))]
        if ZALO:
            contact.insert(1, '<a href="%s" data-track="zalo_click">Zalo</a>' % zalo_url())
        # The widget, one frame per language (its title in that language), and always
        # under it a way round it: whether a frame loaded can't be told
        widget = ''.join('<div class="book-widget" data-l="%s" lang="%s"><iframe src="%s" title="%s" loading="lazy"%s>'
                         '</iframe></div>' % (lang, lang, esc_attr(url), title,
                                              ' allow="payment"' if RESDIARY_PAYMENTS else '')
                         for lang, url, title in (('en', RESDIARY_URL, 'Book a table at Sol'),
                                                  ('vi', RESDIARY_URL_VI or RESDIARY_URL, 'Đặt bàn tại Sol')))
        widget += '\n  <p class="book-fallback">%s</p>\n  ' % t('Trouble with the booking form? %s.' % ' · '.join(contact),
                                                             'Không đặt được qua biểu mẫu? %s.' % ' · '.join(contact))
    else:
        # Before opening, and from opening day (by_state(): in the browser on the day)
        booking_p = by_state(
            t('Online booking opens closer to the day we open. Until then, call or email us '
              'and we’ll hold you a table for opening week.',
              'Chúng tôi sẽ mở đặt bàn trực tuyến khi gần đến ngày khai trương. Từ nay đến lúc '
              'đó, bạn cứ gọi điện hoặc gửi email, chúng tôi sẽ giữ bàn cho bạn trong tuần '
              'khai trương.'),
            t('Call or email us and we’ll hold you a table.',
              'Hãy gọi điện hoặc gửi email, chúng tôi sẽ giữ bàn cho bạn.'))
        widget = '<!-- ResDiary: set RESDIARY_URL in build/gen.py and its widget appears here. -->\n  '
    # Until online booking is live: the number and address as text to copy, not buttons
    # that open another app (Linh, 23 Sep). The Instagram handle as text too, for guests
    # who'd rather send a message (Anh Hoang, 24 Sep). CONTACT_LIVE makes them links.
    if CONTACT_LIVE:
        phone = '<a href="%s" data-track="call_click">%s</a>' % (PHONE_TEL, PHONE)
        email = '<a href="mailto:%s">%s</a>' % (EMAIL, EMAIL)
        insta = '<a href="%s">%s</a>' % (INSTAGRAM, INSTA_HANDLE)
    else:
        phone, email, insta = PHONE, EMAIL, INSTA_HANDLE
    rows = [(t('Phone', 'Điện thoại'), phone)]
    if CONTACT_LIVE and ZALO:
        rows.append(('Zalo', '<a href="%s" data-track="zalo_click">%s</a>' % (zalo_url(), ZALO)))
    if CONTACT_LIVE and WHATSAPP:
        rows.append(('WhatsApp', '<a href="%s" data-track="whatsapp_click">+%s</a>' % (whatsapp_url(), WHATSAPP)))
    rows += [('Email', email), ('Instagram', insta)]
    # Before online booking: a table for opening week, by email (until opening day:
    # by_state() takes it off in the browser on the day)
    hold = ''
    if not RESDIARY_URL and SITE_STATE != 'open':
        hold = ('<div class="wrap"><section class="form-section" aria-labelledby="s-hold"><header class="section-head">%s'
                '<h2 id="s-hold">%s</h2><p>%s</p></header>%s</section></div>' % (
                    sun(2), t('Hold me a table for opening week', 'Giữ bàn cho tôi trong tuần khai trương'),
                    t('Tell us who’s coming and when, and we’ll write back to confirm.',
                      'Hãy cho chúng tôi biết bạn đi mấy người và vào tối nào, chúng tôi sẽ trả lời để xác nhận.'),
                    mailform('opening-week', 'Opening week — ', [
                        ('name', t('Name', 'Họ tên'), 'text', True),
                        ('phone', t('Phone or Zalo', 'Điện thoại hoặc Zalo'), 'tel', True),
                        ('email', 'Email', 'email', False),
                        ('guests', t('Number of guests', 'Số khách'), 'number', True),
                        ('night', t('Which night, and roughly what time', 'Tối nào, khoảng mấy giờ'), 'text', True),
                        ('notes', t('Anything else', 'Thông tin thêm'), 'textarea', False),
                    ], t('Send by email', 'Gửi qua email'))))
        hold = by_state(hold, '', tag='div')
    terms = gate('booking-terms', 'the booking terms: cancellations, deposits, how long a table is held, the largest '
                 'party that can book online',
                 '<section class="prose-section" aria-labelledby="s-terms"><header class="section-head"><h2 id="s-terms">%s'
                 '</h2></header><dl class="gtk-items">%s</dl></section>' % (
                     t('Before you book', 'Trước khi đặt bàn'),
                     ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (k, t('[to come]', '[sẽ cập nhật]')) for k in (
                         t('Cancellations', 'Hủy bàn'), t('Deposits', 'Đặt cọc'),
                         t('How long a table is yours', 'Thời gian giữ bàn'),
                         t('Booking online', 'Đặt bàn trực tuyến')))), tag='div')
    frm = from_opening()
    main = """<main id="main">
<div class="wrap">{title}</div>
<div class="wrap"><div class="offer booking">
  {widget}<dl class="book-contact">{rows}</dl>
  <p class="offer-note">{groups}</p>
</div></div>
{hold}<div class="wrap">{terms}</div>
<div class="wrap"><p class="booking-visit">{hours} · {addr}{visit}</p></div>
</main>
""".format(
        title=page_title(t('Reservations', 'Đặt chỗ'), BOOK, booking_p).replace(
            '<header class="page-title">', '<header class="page-title" id="book">', 1),
        widget=widget, rows=''.join('<div><dt>%s</dt><dd>%s</dd></div>' % r for r in rows),
        groups=groups_line(), hold=hold, terms=terms,
        hours=t(*HOURS_PLAIN) + by_state(t(', from the day we open', ', kể từ ngày khai trương'), ''),
        addr=t(ADDRESS_EN, ADDRESS_VI),
        visit=('<br><a class="link-sc" href="/visit-us/">%s</a>'
               % t('Hours, address and getting here', 'Giờ mở cửa, địa chỉ và đường đến') if live('visit') else ''),
    )
    how = ('Book online, or call or email us.', 'Đặt bàn trực tuyến, hoặc gọi điện hay gửi email.') if RESDIARY_URL \
        else ('Call or email to hold a table.', 'Gọi điện hoặc gửi email để giữ bàn.')
    return page('/booking/', 'page-booking',
                ('Booking — Sol, Tây Hồ', 'Đặt bàn — Sol, Tây Hồ'),
                ('No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi. %s%s. %s' % (HOURS_PLAIN[0], frm[0], how[0]),
                 'Số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. %s%s. %s' % (HOURS_PLAIN[1], frm[1], how[1])),
                main, cur='booking', og='visit', bar=False,
                # iOS would turn the booking box's phone number back into a link
                extra=['' if CONTACT_LIVE else '<meta name="format-detection" content="telephone=no">\n', schema])


def build_private_dining():
    """/private-dining/: groups of seven or more, and private events. What we know (the
    enquiry, by email) is public; the spaces, set menus and minimum spend wait for their
    figures (CONTENT-NEEDED.md)."""
    def placeholder(sid, heading, rows):
        return ('<section class="prose-section" aria-labelledby="%s"><header class="section-head"><h2 id="%s">%s</h2>'
                '</header><dl class="gtk-items">%s</dl></section>'
                % (sid, sid, heading,
                   ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (k, t('[to come]', '[sẽ cập nhật]')) for k in rows)))
    main = '\n'.join([
        '<main id="main">',
        '<div class="wrap">%s</div>' % page_title(
            t('Private dining', 'Tiệc riêng'), t('Groups and private dining', 'Nhóm đông và tiệc riêng'),
            t('For seven or more, or a night that’s all yours: tell us what you have in mind, and we’ll come back '
              'to you.',
              'Từ bảy người trở lên, hay một buổi tối chỉ dành riêng cho bạn: hãy cho chúng tôi biết bạn muốn tổ '
              'chức thế nào, chúng tôi sẽ liên hệ lại.')),
        '<div class="wrap">%s</div>' % gallery('private-dining', eager=True),
        '<div class="wrap">%s%s%s</div>' % (
            gate('private-dining-spaces', 'the spaces on each floor and how many each seats',
                 placeholder('s-spaces', t('The spaces', 'Không gian'),
                             [t('Ground floor', 'Tầng 1'), t('Upstairs', 'Tầng 2'),
                              t('The whole restaurant', 'Cả nhà hàng')])),
            gate('private-dining-menus', 'set menus for groups',
                 placeholder('s-set-menus', t('Set menus', 'Thực đơn set'),
                             [t('Menus and prices', 'Thực đơn và giá')])),
            gate('private-dining-minimum', 'the minimum spend for a private space',
                 placeholder('s-minimum', t('Minimum spend', 'Mức chi tối thiểu'),
                             [t('For a private space', 'Cho một không gian riêng')]))),
        '<div class="wrap"><section class="form-section" id="enquire" aria-labelledby="s-enquire"><header class="section-head">'
        '%s<h2 id="s-enquire">%s</h2><p>%s</p></header>%s</section></div>' % (
            sun(5), t('Tell us about it', 'Cho chúng tôi biết về buổi tiệc'),
            t('The date, how many of you, and anything we should know. We’ll write back with what we can do.',
              'Ngày nào, bao nhiêu người, và những điều chúng tôi nên biết. Chúng tôi sẽ phản hồi và cho bạn biết '
              'những gì chúng tôi có thể sắp xếp.'),
            mailform('private-dining', 'Private dining — ', [
                ('name', t('Name', 'Họ tên'), 'text', True),
                ('phone', t('Phone or Zalo', 'Điện thoại hoặc Zalo'), 'tel', True),
                ('email', 'Email', 'email', False),
                ('date', t('Date', 'Ngày'), 'date', True),
                ('guests', t('Number of guests', 'Số khách'), 'number', True),
                ('occasion', t('The occasion', 'Dịp tổ chức'), 'text', False),
                ('budget', t('Budget per person', 'Ngân sách mỗi người'), 'text', False),
                ('notes', t('Anything else', 'Thông tin thêm'), 'textarea', False),
            ], t('Send by email', 'Gửi qua email'))),
        '</main>', ''])
    return page('/private-dining/', 'page-private-dining',
                ('Private dining — Sol, Tây Hồ', 'Tiệc riêng — Sol, Tây Hồ'),
                ('Groups of seven or more and private dining at Sol, No 7, Lane 88 Quang An, Tây Hồ, Hanoi. Tell us '
                 'what you have in mind.',
                 'Nhóm từ bảy người trở lên và tiệc riêng tại Sol, số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Hãy cho '
                 'chúng tôi biết bạn muốn tổ chức thế nào.'),
                main, cur='private-dining', og='private-dining')


# ==========================================================================
# EVENTS  /events/  and a page for each edition, /events/<slug>/
# (build/events-data.json). Each edition shows as coming up until the end of its
# last night, then as past: the head script switches it in the browser (EV_STYLE),
# so the list is right without a rebuild.
# ==========================================================================
def event_ld(e, lang, alone=True):
    """An Eclipse edition as Events, one per night, in the page's language: only once it
    has its details and its page (an edition still waiting shows its dates and nothing
    more). alone: blocks of their own (with @context); otherwise inside the restaurant's."""
    if not e['ready']:
        return []
    vi = lang == 'vi'
    a, b = e['times'].split('–') if e['times'] else (None, None)
    url = SITE + lang_path(e['path'], lang)
    pic = PHOTO_BY_KEY.get(e['image'])
    nights = []
    for day in e['days']:
        d = {'@type': 'Event', 'name': 'Eclipse %d' % e['edition'],
             'description': e['summary_vi'] if vi else e['summary_en'],
             'startDate': day.isoformat() + ('T%s:00+07:00' % a if a else ''),
             # past midnight (18:00–01:00), it ends the next morning
             'endDate': (day + timedelta(days=1 if b and b < a else 0)).isoformat() + ('T%s:00+07:00' % b if b else ''),
             'eventStatus': 'https://schema.org/EventScheduled',
             'eventAttendanceMode': 'https://schema.org/OfflineEventAttendanceMode',
             'location': {'@type': 'Place', 'name': 'Sol', 'address': ADDRESS_LD[lang]},
             'organizer': {'@type': 'Organization', 'name': 'Sol', 'url': SITE + lang_path('/', lang)},
             'url': url,
             'image': [photo_url(pic, 1600, (2, 1))] if pic else [og_image('events', lang)]}
        if e['chefs']:
            d['performer'] = [{'@type': 'Person', 'name': c['name']} for c in e['chefs']]
        if e['price']:
            d['offers'] = {'@type': 'Offer', 'price': str(e['price']), 'priceCurrency': 'VND',
                           'url': e['booking'] or url}
        nights.append(dict({'@context': 'https://schema.org'}, **d) if alone else d)
    return nights


def per_person(n):
    return t('%s VND a person' % vnd(n, ','), '%s đồng/người' % vnd(n, '.'))


def ev_item(e, cls):
    """An edition in the /events/ list: its name, dates, the line on it (or "details
    soon") and its page, if it has one. cls: ev-up (coming up) or ev-past."""
    more = ('<a class="link-sc" href="%s">%s</a>' % (e['path'], t('More', 'Xem thêm'))
            if e['ready'] or FULL else '')
    line = (t(esc(e['summary_en']), esc(e['summary_vi'])) if e['ready']
            else t('Details soon.', 'Thông tin chi tiết sẽ sớm được cập nhật.') if cls == 'ev-up' else '')
    switch = '' if (cls == 'ev-past' and ev_over(e)) else ' data-ev="%s"' % e['slug']
    return ('<li class="ev %s"%s><p class="label">Eclipse · %s</p><h3>%s</h3>%s%s</li>'
            % (cls, switch, ev_name(e), ev_dates(e), '<p>%s</p>' % line if line else '', more))


def build_events():
    up = ev_upcoming()
    past_now = [e for e in EVENTS if e['until'] <= NOW]
    # Coming up: the editions still to come at build time; each also sits in Past,
    # hidden until it ends (EV_STYLE).
    upcoming = ''.join(ev_item(e, 'ev-up') for e in up)
    past = ''.join(ev_item(e, 'ev-past') for e in reversed(EVENTS))       # the latest first; those still to
                                                                          # come show here once over
    main = '\n'.join([
        '<main id="main">',
        '<div class="wrap">%s</div>' % page_title(t('Events', 'Sự kiện'), 'Eclipse', EV_SERIES),
        '<div class="wrap"><section class="ev-section" aria-labelledby="s-ev-up"><header class="section-head">%s'
        '<h2 id="s-ev-up">%s</h2></header><ul class="ev-list">%s</ul><p class="ev-none-msg%s">%s</p></section>'
        % (sun(4), t('Coming up', 'Sắp diễn ra'), upcoming, '' if up else ' is-shown',
           t('Nothing announced just now. Sign up for news by email, at the foot of the page, to hear about the '
             'next one.',
             'Hiện chưa có lịch mới. Hãy đăng ký nhận tin qua email ở cuối trang để biết về lần tiếp theo.')),
        '<section class="ev-section ev-past-section%s" aria-labelledby="s-ev-past"><header class="section-head">'
        '<h2 id="s-ev-past">%s</h2></header><ul class="ev-list">%s</ul></section></div>'
        % (' has-past' if past_now else '', t('Past editions', 'Các lần trước'), past),
        '</main>', ''])
    # the editions still to come, as Events, in the page's language
    events = [lambda lang, e=e: ''.join(ld(night) for night in event_ld(e, lang)) for e in up]
    return page('/events/', 'page-events', ('Events — Sol, Tây Hồ', 'Sự kiện — Sol, Tây Hồ'),
                ('Eclipse, Sol’s pop-up series, at No 7, Lane 88 Quang An, Tây Hồ, Hanoi: what’s coming up, and '
                 'what’s been.',
                 'Eclipse, chuỗi sự kiện pop-up của Sol tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội: những gì sắp '
                 'diễn ra và đã diễn ra.'),
                main, cur='events', og='events', extra=events)


def build_event(e):
    """An edition's page: what it is, when, the chefs, the menu, the price and how to
    book. It waits (WAITING) until it has its line (summary_en and summary_vi)."""
    name = 'Eclipse %d' % e['edition']
    when = ev_dates(e)
    if e['times']:                      # 18:00–23:00: 6pm–11pm · 18:00 – 23:00
        a, b = e['times'].split('–')
        when += ' · %s' % t('%s–%s' % (en_time(a), en_time(b)), '%s – %s' % (a, b))
    facts = [(t('When', 'Thời gian'), when),
             (t('Where', 'Địa điểm'), t('Sol, %s' % ADDRESS_EN, 'Sol, %s' % ADDRESS_VI))]
    if e['price']:
        facts.append((t('Price', 'Giá'), per_person(e['price'])))
    summary = t(esc(e['summary_en']), esc(e['summary_vi'])) if e['ready'] else t('[to come]', '[sẽ cập nhật]')
    if e['booking']:
        book = ('<a class="btn btn-red" href="%s" data-track="book_click" data-booking="%s">%s</a>'
                % (esc_attr(e['booking']), e['slug'], t('Book', 'Đặt chỗ')))
    else:
        book = ('<a class="btn btn-red" href="%s" data-track="book_click" data-booking="%s">%s</a>'
                % (mailto(ENQUIRIES, name, ''), e['slug'], t('Book by email', 'Đặt chỗ qua email')))
    pic = PHOTO_BY_KEY.get(e['image'])
    parts = [
        '<main id="main">',
        '<div class="wrap">%s</div>' % page_title(ev_name(e), 'Eclipse', summary),
        band('event', 'band wrap-wide', eager=True, spec=EVENT_SLOT, p=pic) if pic or FULL else '',
        '<div class="wrap"><dl class="facts ev-facts">%s</dl></div>' % ''.join(
            '<div><dt>%s</dt><dd>%s</dd></div>' % f for f in facts),
    ]
    if e['chefs']:
        parts.append(prose_section('s-chefs', 2, t('In the kitchen', 'Trong bếp'), [
            '<p><b>%s</b> %s</p>' % (esc(c['name']), t(esc(c['line_en']), esc(c['line_vi']))) for c in e['chefs']]))
    if e['menu_en']:
        parts.append(prose_section('s-menu', 5, t('The menu', 'Thực đơn'), [
            '<ul class="ev-menu">%s</ul>' % ''.join('<li>%s</li>' % t(esc(en), esc(vi))
                                                    for en, vi in zip(e['menu_en'], e['menu_vi']))]))
    over = '%s <a href="/events/">%s</a>' % (t('This edition is over.', 'Eclipse lần này đã kết thúc.'),
                                             t('All editions', 'Xem tất cả các lần Eclipse'))
    if ev_over(e):          # over when built: just that
        parts += ['<div class="wrap"><p class="ev-over">%s</p></div>' % over, '</main>', '']
    else:                   # the Book box until it's over, then the note (the head script)
        parts += [
            '<div class="wrap"><section class="offer ev-up" data-ev="%s" aria-labelledby="s-ev-book"><h2 id="s-ev-book">'
            '%s</h2><p>%s</p>%s</section>' % (e['slug'], t('Book', 'Đặt chỗ'), when, book),
            '<p class="ev-past ev-over" data-ev="%s">%s</p></div>' % (e['slug'], over),
            '</main>', '']
    return page(e['path'], 'page-event', ('%s — Sol, Tây Hồ' % name, '%s — Sol, Tây Hồ' % name),
                (esc_attr(fit('%s, %s. %s' % (name, re.sub('<[^>]+>', '', _keep_lang(ev_dates(e), 'en')),
                                              e['summary_en'] or 'Sol’s pop-up series.'))),
                 esc_attr(fit('%s, %s. %s' % (name, re.sub('<[^>]+>', '', _keep_lang(ev_dates(e), 'vi')),
                                              e['summary_vi'] or 'Chuỗi sự kiện pop-up của Sol.')))),
                '\n'.join(parts), cur='events', og='events',
                extra=[lambda lang: ''.join(ld(night) for night in event_ld(e, lang))])


# Visit & FAQ: the questions guests ask before they come, each answered once we have
# the facts (CONTENT-NEEDED.md, "Getting here"). (gate key, what's missing, question,
# answer): an answer of None keeps the question in the full previews only, marked;
# write the answer as t('English', 'Tiếng Việt') and it goes live.
VISIT_FAQ = [
    ('visit-capacity', 'how many seats in all, and the largest table',
     t('Big groups', 'Nhóm đông'), None),
    ('visit-getting-here', 'motorbike and car parking, and where Grab drops off',
     t('Getting here and parking', 'Đường đến và chỗ gửi xe'), None),
    ('visit-access', 'the lift, steps, and the toilets: step-free or not',
     t('Step-free access and the lift', 'Lối vào không bậc thềm và thang máy'), None),
    ('visit-payment', 'how guests can pay: cash, which cards, transfer, e-wallets (PAYMENT_ACCEPTED in gen.py)',
     t('Paying', 'Thanh toán'),
     t(esc(PAYMENT_ACCEPTED[0]) + '.', esc(PAYMENT_ACCEPTED[1]) + '.') if PAYMENT_ACCEPTED[0] else None),
    ('visit-corkage', 'whether guests can bring their own wine, and the corkage fee',
     t('Bringing your own wine', 'Mang rượu vang riêng'), None),
    ('visit-dress', 'whether there is a dress code',
     t('What to wear', 'Trang phục'), None),
    ('visit-dogs', 'whether dogs are welcome, inside or out',
     t('Dogs', 'Mang theo chó'), None),
    ('visit-smoking', 'whether there is anywhere to smoke',
     t('Smoking', 'Hút thuốc'), None),
]


def visit_faq():
    """Good to know: the answers we have, then (full build only) the questions waiting."""
    have = [(q, a) for _, _, q, a in VISIT_FAQ if a]
    rows = [(t('Children', 'Trẻ em'),
             t('Very welcome. We have high chairs, and the kitchen will happily make something plain.',
               'Rất hoan nghênh. Có ghế ăn cho bé, và bếp sẵn sàng làm món đơn giản.'))] + have
    waiting = ''.join(gate(key, what, '<dl class="gtk-items"><div><dt>%s</dt><dd>%s</dd></div></dl>'
                           % (q, t('[to come]', '[sẽ cập nhật]')))
                      for key, what, q, a in VISIT_FAQ if not a)
    return ('<dl class="gtk-items">%s</dl>%s'
            % (''.join('<div><dt>%s</dt><dd>%s</dd></div>' % r for r in rows), waiting))


def build_visit():
    frm = from_opening()
    hours_rows = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % row for row in (
        [(t(en_list([EN_DAYS[d] for d in CLOSED_DAYS]), ' và '.join(VI_DAYS_CAP[d] for d in CLOSED_DAYS)),
          t('Closed', 'Đóng cửa'))] if CLOSED_DAYS else []) + [(HOURS_DAYS, HOURS_SPAN)])
    main = """<main id="main">
<div class="wrap">{title}</div>
<div class="wrap"><div class="visit-info">
  <section aria-labelledby="v-hours"><h2 class="label" id="v-hours">{l_hours}</h2><dl class="hours">{hours_rows}</dl>{last}{from_open}</section>
  <section aria-labelledby="v-addr"><h2 class="label" id="v-addr">{l_addr}</h2><p>{addr}</p><a class="link-sc" href="{maps}">{maps_t}</a></section>
  <section aria-labelledby="v-contact"><h2 class="label" id="v-contact">{l_talk}</h2><p><a href="{tel}">{phone}</a><br><a href="mailto:{email}">{email}</a><br>{insta}</p></section>
</div></div>
{photo}
<section class="prose-section wrap" aria-labelledby="s-gtk"><header class="section-head">{sun}<h2 id="s-gtk">{gtk}</h2></header>{faq}</section>
{book_box}</main>
""".format(
        title=page_title(t('Visit', 'Ghé thăm'), t('Find us', 'Tìm chúng tôi'),
                         t('Sol is on the first two floors of No 7, Lane 88 Quang An.%s'
                           % by_state(' We’re opening soon.', ''),
                           'Sol nằm ở hai tầng đầu của tòa nhà số 7, ngõ 88 Quảng An.%s'
                           % by_state(' Chúng tôi sắp khai trương.', ''))),
        l_hours=t('Opening hours', 'Giờ mở cửa'), hours_rows=hours_rows,
        last=('<p class="small">%s</p>' % LAST_ORDERS if LAST_ORDERS else
              gate('visit-last-orders', 'the time of last orders (HOURS in gen.py)',
                   '<p class="small">%s</p>' % t('Last orders [to come]', 'Nhận gọi món đến [sẽ cập nhật]'))),
        from_open=by_state('<p class="small">%s</p>' % t('From the day we open.', 'Từ ngày chúng tôi khai trương.'), '',
                           tag='div'),
        l_addr=t('Address', 'Địa chỉ'), addr=t(ADDRESS_EN, ADDRESS_VI),
        maps=MAPS_URL, maps_t=MAPS_LINK_TEXT,
        l_talk=t('Talk to us', 'Liên hệ'), tel=PHONE_TEL, phone=PHONE, email=EMAIL, insta=INSTA_LINK,
        sun=sun(3), gtk=t('Good to know', 'Thông tin hữu ích'), faq=visit_faq(), photo=band('visit', 'band wrap-wide', eager=True),
        # Book a table: while the booking page is public (HIDDEN)
        book_box=('<div class="wrap"><section class="offer" aria-labelledby="s-book"><h2 id="s-book">%s</h2><p>%s</p>'
                  '<a class="btn btn-red" href="/booking/#book" data-track="book_click">%s</a></section></div>\n' % (
                      BOOK, groups_line(), BOOK) if live('booking') else ''),
    )
    return page('/visit-us/', 'page-visit',
                ('Visit — Sol, Tây Hồ', 'Ghé thăm — Sol, Tây Hồ'),
                ('Sol is at No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi. Open %s%s.' % (HOURS_PLAIN[0], frm[0]),
                 'Sol ở số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Mở cửa %s%s.' % (HOURS_PLAIN[1], frm[1])),
                main, cur='visit', og='visit')


# ==========================================================================
# WORK WITH US  /jobs/
# The opening team (build/jobs-data.json): a card each on /jobs/, grouped Front
# of house / Kitchen, and a page each at /jobs/<slug>/ in both languages, its
# job description word for word from build/jobs/<slug>.md. The round's closing
# instant is in the data once; after it, the cards and pages say the round has
# closed and hide their Apply buttons (ROUND_SCRIPT).
# Filled roles are listed under "Recently filled" and link to their pages, which
# are re-wrapped from src/jobs/*.html with the copy untouched (ROLES).
# ==========================================================================
ROLES = [
    dict(slug='restaurant-accountant', src='restaurant-accountant.html',
         name_en='Restaurant Accountant', name_vi='Kế toán nhà hàng',
         status='filled', filled_en='September 2026', filled_vi='Tháng 9 năm 2026'),
    dict(slug='sous-chef', src='sous-chef.html',
         name_en='Sous Chef', name_vi='Bếp phó',
         status='filled', filled_en='September 2026', filled_vi='Tháng 9 năm 2026'),
    dict(slug='restaurant-supervisor', src='restaurant-supervisor.html',
         name_en='Restaurant Supervisor', name_vi='Giám sát nhà hàng',
         status='filled', filled_en='September 2026', filled_vi='Tháng 9 năm 2026'),
]

# Promises nothing the opening-team job descriptions don't (checked 24 Sep 2026):
# the service charge starts once we open, and WSET funding is in none of them.
BENEFITS = [
    ('A share of the 5% service charge and the tip pool for floor and kitchen roles, paid quarterly, '
     'starting once we open.',
     'Một phần trong 5% phí phục vụ và quỹ tip cho các vị trí phục vụ và bếp, trả hàng quý, bắt đầu '
     'khi nhà hàng mở cửa.'),
    ('A 13th-month bonus based on company KPIs, and a salary review every year based on performance.',
     'Thưởng tháng 13 theo KPI công ty, và xét tăng lương hàng năm theo hiệu quả công việc.'),
    ('Full statutory insurance — BHXH, BHYT and BHTN — from the day your labour contract starts.',
     'Đầy đủ bảo hiểm theo luật — BHXH, BHYT, BHTN — từ ngày hợp đồng lao động bắt đầu.'),
    ('12 days’ paid annual leave, plus one extra day for every 3 years with us, subject to company policy.',
     '12 ngày nghỉ phép có lương mỗi năm, cộng thêm một ngày cho mỗi 3 năm làm việc, theo chính sách công ty.'),
    ('11 paid public holidays a year, including Tết. Holiday work is paid at the statutory premium.',
     '11 ngày nghỉ lễ có lương mỗi năm, bao gồm Tết. Làm việc ngày lễ được trả theo mức phụ trội luật định.'),
    ('A staff meal from our kitchen before dinner service, and a staff discount at Sol and ASU House Bakery.',
     'Bữa ăn nhân viên do bếp nấu trước ca tối, và ưu đãi giảm giá tại Sol và ASU House Bakery.'),
]


def role_path(r):
    return '/jobs/' + r['slug']          # Cloudflare serves jobs/<slug>.html here


# --------------------------------------------------------------------------
# the opening team: build/jobs-data.json and build/jobs/<slug>.md
# --------------------------------------------------------------------------
JOBS = json.loads(read(os.path.join(HERE, 'jobs-data.json')))
ROUND = JOBS['round']
JOBS_EMAIL = 'jobs@sol.pizza'
CLOSES = datetime.fromisoformat(ROUND['closes'])       # Hanoi time, with its offset
STARTS = date.fromisoformat(ROUND['starts'])
SERVICE = ROUND['service_charge']



def vnd(n, sep):
    return '{:,}'.format(n).replace(',', sep)


def band_en(lo_hi, dash=' – '):
    return dash.join(vnd(n, ',') for n in lo_hi)


def band_vi(lo_hi):
    return ' – '.join(vnd(n, '.') for n in lo_hi)


def band_vi_cut(lo_hi, unit):
    """band_vi() and its unit for a narrow card: it may break after the dash, nowhere else."""
    return '<span class="nowrap">%s –</span> <span class="nowrap">%s %s</span>' % (vnd(lo_hi[0], '.'), vnd(lo_hi[1], '.'), unit)


def trieu(lo_hi):
    """11–14 triệu, 6,5–7,5 triệu: millions, the Vietnamese way."""
    return '–'.join(('%g' % (n / 1e6)).replace('.', ',') for n in lo_hi) + ' triệu'


def encode_uri_component(s):
    """JavaScript's encodeURIComponent, for the Apply links' no-JS href."""
    return quote(s, safe="-_.!~*'()")


def jd_inline(s, link):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: link(m.group(1), m.group(2)), s)


def parse_jd(block):
    """One language of a job description, in the Markdown build/jobs/<slug>.md uses:
    '# ' title, a line (eyebrow), a two-column table (the facts), a bold line (the
    standfirst), then '## ' and '### ' headings, paragraphs and '- ' lists."""
    lines = block.split('\n')
    jd = dict(title=lines[0].strip(), facts=[], blocks=[])
    para, items = [], []

    def flush():
        if para:
            jd['blocks'].append(('p', ' '.join(para)))
            para.clear()
        if items:
            jd['blocks'].append(('ul', list(items)))
            items.clear()

    for line in lines[1:]:
        line = line.strip()
        if not line:
            flush()
        elif line.startswith('|'):
            flush()
            cells = [c.strip() for c in line.strip('|').split('|')]
            if any(cells) and not re.fullmatch(r'[-: |]*', line):
                jd['facts'].append((cells[0].replace('**', ''), cells[1]))
        elif line.startswith('### '):
            flush()
            jd['blocks'].append(('h3', line[4:]))
        elif line.startswith('## '):
            flush()
            jd['blocks'].append(('h2', line[3:]))
        elif line.startswith('- '):
            if para:
                flush()
            items.append(line[2:])
        else:
            if items:
                flush()
            para.append(line)
    flush()
    kind, jd['eyebrow'] = jd['blocks'].pop(0)
    kind2, standfirst = jd['blocks'].pop(0)
    assert kind == kind2 == 'p' and jd['facts'] and re.fullmatch(r'\*\*[^*]+\*\*', standfirst), \
        'build/jobs: "%s" should open with its eyebrow line, the facts table and a bold standfirst' % jd['title']
    jd['standfirst'] = standfirst[2:-2]
    return jd


def jd_html(blocks, link):
    out = []
    for kind, val in blocks:
        if kind == 'ul':
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % jd_inline(i, link) for i in val))
        else:
            out.append('<%s>%s</%s>' % (kind, jd_inline(val, link), kind))
    return '\n'.join(out)


def read_jd(slug):
    text = read(os.path.join(HERE, 'jobs', slug + '.md'))
    parts = [p for p in re.split(r'(?m)^# ', text) if p.strip()]
    assert len(parts) == 2, 'build/jobs/%s.md: expected an English and a Vietnamese block' % slug
    return parse_jd(parts[0]), parse_jd(parts[1])


def check_jd(r):
    """The ads quote these numbers and dates: stop if a job description has drifted from
    build/jobs-data.json. Checked where they show: the facts table's base salary,
    openings, closing and start dates, and every salary band anywhere in the text
    (each must be the base, the service charge estimate or the total).
    JOBS_ALLOW_DATE_DRIFT=1 lets the dates differ, to try the closed state."""
    total = [b + s for b, s in zip(r['base'], SERVICE)]
    texts = read(os.path.join(HERE, 'jobs', r['slug'] + '.md')).split('\n# ', 1)
    openings = str(r['openings']) if r['openings'] else None
    problems, dates = [], []
    for lang, jd, text, band, cur, keys in (
            ('English', r['jd'][0], texts[0], band_en, 'VND',
             ('Base salary', 'Openings', 'Applications close', 'Start')),
            ('Vietnamese', r['jd'][1], texts[1], band_vi, 'VNĐ',
             ('Lương cơ bản', 'Số lượng tuyển', 'Hạn nộp hồ sơ', 'Ngày bắt đầu'))):
        facts = dict(jd['facts'])
        bands = ['%s %s' % (band(x), cur) for x in (r['base'], SERVICE, total)]
        if not facts.get(keys[0], '').startswith(bands[0]):
            problems.append('%s facts: base salary "%s", data says %s' % (lang, facts.get(keys[0]), bands[0]))
        problems += ['%s: "%s" is not the base salary, service charge or total' % (lang, m)
                     for m in re.findall(r'\d[\d.,]* – \d[\d.,]* VN[DĐ]', text) if m not in bands]
        problems += ['%s: no "%s"' % (lang, b) for b in bands if b not in text]
        if facts.get(keys[1]) != openings:
            problems.append('%s facts: openings %s, data says %s' % (lang, facts.get(keys[1]), openings))
        if lang == 'English':
            close, start = '%s %d' % (en_date(CLOSES), CLOSES.year), '%s %d' % (en_date(STARTS), STARTS.year)
        else:
            close, start = vi_date(CLOSES, True), vi_date(STARTS, True)
        if facts.get(keys[2], '').lower() != close.lower():
            dates.append('%s facts: closes "%s", data says %s' % (lang, facts.get(keys[2]), close))
        if not facts.get(keys[3], '').lower().startswith(start.lower()):
            dates.append('%s facts: starts "%s", data says %s' % (lang, facts.get(keys[3]), start))
    if dates and os.environ.get('JOBS_ALLOW_DATE_DRIFT') == '1':
        print('note: build/jobs/%s.md: %s (allowed by JOBS_ALLOW_DATE_DRIFT)' % (r['slug'], '; '.join(dates)))
        dates = []
    if problems or dates:
        raise SystemExit('build/jobs/%s.md no longer matches build/jobs-data.json: %s. Make the two agree '
                         '(the ads quote the same numbers and dates).' % (r['slug'], '; '.join(problems + dates)))


OPEN_ROLES = [dict(r, jd=read_jd(r['slug'])) for r in JOBS['roles']]
for _r in OPEN_ROLES:
    _r['name_en'], _r['name_vi'] = _r['jd'][0]['title'], _r['jd'][1]['title']
    check_jd(_r)


def open_role_path(r):
    return '/jobs/%s/' % r['slug']


# Before first paint: once the round has closed, <html class="round-closed"> shows
# the closed notes and hides the Apply buttons (site.css). Without JS the pages
# still show the closing date.
ROUND_SCRIPT = ("<script>try{if(Date.now()>Date.parse('%s'))"
                "document.documentElement.classList.add('round-closed')}catch(e){}</script>" % ROUND['closes'])

# After the page: the Apply links' subject and body, built with encodeURIComponent
# in the page's language and rebuilt when EN / VI switches it (once the round has
# closed, the job description's own jobs@sol.pizza link is a plain address); and on
# phones, the Apply bar while the Apply button at the top is scrolled past and the
# one at the end not yet reached. The observers' margins stretch the viewport far
# down (top) and far up (end), so a jump to a #link or the footer can't skip a change.
APPLY_SCRIPT = """<script>
(function () {
  var root = document.documentElement, links = document.querySelectorAll('a[data-apply]');
  function build() {
    var lang = root.lang === 'vi' ? 'vi' : 'en', closed = root.classList.contains('round-closed');
    for (var i = 0; i < links.length; i++) {
      var a = links[i], body = a.getAttribute('data-body-' + lang).replace(/\\r?\\n/g, '\\r\\n');
      a.href = closed && !a.classList.contains('apply-btn') ? 'mailto:%(email)s' :
               'mailto:%(email)s?subject=' + encodeURIComponent(a.getAttribute('data-subject')) +
               '&body=' + encodeURIComponent(body);
    }
  }
  build();
  if (window.MutationObserver) new MutationObserver(build).observe(root, {attributes: true, attributeFilter: ['lang']});
  var bar = document.querySelector('.apply-bar'), top = document.querySelector('[data-apply-top]'),
      end = document.querySelector('[data-apply-end]');
  if (!bar || !top || !end || !('IntersectionObserver' in window)) return;
  var above = false, reached = false;
  function show() { bar.classList.toggle('is-shown', above && !reached); }
  new IntersectionObserver(function (e) { above = !e[e.length - 1].isIntersecting; show(); },
                           {rootMargin: '0px 0px 100000px 0px'}).observe(top);
  new IntersectionObserver(function (e) { reached = e[e.length - 1].isIntersecting; show(); },
                           {rootMargin: '100000px 0px 0px 0px'}).observe(end);
})();
</script>""" % dict(email=JOBS_EMAIL)


def apply_attrs(r):
    """href (English, for no JS) plus what APPLY_SCRIPT needs to build it in either language."""
    subject = '%s — ' % r['name_en']              # English in both languages: the inbox is sorted by it

    def body(q, labels, cv):
        name, phone, answer = labels
        return '\n'.join([name, phone, '', q, '', answer, '', '', cv])

    en = body(r['question'], ('Name:', 'Phone / Zalo:', 'My answer:'), r.get('cv_line') or ROUND['cv_line'])
    vi = body(r['question_vi'], ('Họ tên:', 'Số điện thoại / Zalo:', 'Câu trả lời của bạn:'),
              r.get('cv_line_vi') or ROUND['cv_line_vi'])
    href = 'mailto:%s?subject=%s&amp;body=%s' % (JOBS_EMAIL, encode_uri_component(subject),
                                                 encode_uri_component(en.replace('\n', '\r\n')))

    def attr(s):
        return _html.escape(s, quote=True).replace('\n', '&#10;')

    return 'href="%s" data-apply data-subject="%s" data-body-en="%s" data-body-vi="%s"' % (
        href, attr(subject), attr(en), attr(vi))


def named(en, vi, r):
    """A link label with the role's name for screen readers: six cards share the same labels."""
    hidden = '<span class="visually-hidden">: %s</span>'
    return t(en + hidden % esc(r['name_en']), vi + hidden % esc(r['name_vi']))


def apply_button(r, cls='btn btn-red', label=None):
    return '<a class="%s apply-btn" %s>%s</a>' % (cls, apply_attrs(r), label or t('Apply', 'Ứng tuyển'))


def closed_text():
    return t('Applications for this round closed on %s. Thank you to everyone who applied.' % en_date(CLOSES),
             'Đợt tuyển dụng này đã đóng vào %s. Cảm ơn tất cả các bạn đã ứng tuyển.' % vi_date(CLOSES, True))


def role_card(r):
    short_vi = re.sub(r'\s*\(%s\)$' % re.escape(r['name_en']), '', r['name_vi'])
    meta = ('<p class="role-meta">%s</p>' % t('Openings: %d' % r['openings'], 'Số lượng: %d' % r['openings'])
            if r['openings'] else '')
    pay = t('Base salary <span class="nowrap">%s VND</span> gross a month<br>'
            '+ service charge &amp; tips, est. <span class="nowrap">%s</span> a month'
            % (band_en(r['base'], '–'), band_en(SERVICE, '–')),
            'Lương cơ bản %s gross/tháng<br>'
            '+ phí phục vụ &amp; tip ước tính %s'
            % (band_vi_cut(r['base'], 'VNĐ'), band_vi_cut(SERVICE, 'VNĐ/tháng')))
    nowrap = '<span class="nowrap">%s</span>'
    dates = t('%s · %s' % (nowrap % ('Applications close ' + en_date(CLOSES, True)),
                           nowrap % ('Start ' + en_date(STARTS, True))),
              '%s · %s' % (nowrap % ('Hạn nộp: ' + vi_date(CLOSES)), nowrap % ('Bắt đầu: ' + vi_date(STARTS))))
    return ('<article class="role" id="role-%s">%s<h4>%s</h4><p class="role-vi" data-l="en" lang="vi">%s</p>'
            '<p>%s</p><p class="role-pay">%s</p><p class="role-dates">%s</p><p class="round-note">%s</p>'
            '<div class="role-links"><a class="link-sc" href="%s">%s</a>%s</div></article>'
            % (r['slug'], meta, t(esc(r['name_en']), esc(r['name_vi'])), esc(short_vi),
               t(esc(r['card']), esc(r['card_vi'])), pay, dates, closed_text(), open_role_path(r),
               named('Read the role', 'Xem mô tả công việc', r),
               apply_button(r, 'btn btn-red btn-sm', named('Apply', 'Ứng tuyển', r))))


def build_jobs():
    closed = datetime.now().astimezone() >= CLOSES
    groups = []
    for sec in JOBS['sections']:
        cards = [role_card(r) for r in OPEN_ROLES if r['section'] == sec['key']]
        groups.append('  <div class="role-group"><h3 class="label">%s</h3><div class="role-list role-list-3">%s</div></div>'
                      % (t(sec['name'], sec['name_vi']), ''.join(cards)))
    roles = '\n'.join(groups)
    filled = ''.join('<li><span><a href="%s">%s</a></span><span>%s</span></li>'
                     % (role_path(r), t(r['name_en'], r['name_vi']), t(r['filled_en'], r['filled_vi']))
                     for r in ROLES if r['status'] == 'filled')
    main = """<main id="main">
<div class="wrap">{title}</div>
<section class="prose-section wrap" aria-labelledby="s-roles"><header class="section-head">{sun1}<h2 id="s-roles">{where}</h2></header>
{roles}
  <div class="filled"><h3 class="label">{recent}</h3><ul>{filled}</ul></div>
</section>
<section class="split about wrap"><div><p class="eyebrow">{k_about}</p><h2 class="h-lg">{h_about}</h2></div><div class="split-body"><p>{a1}</p><p>{a2}</p></div></section>
<section class="prose-section wrap" aria-labelledby="s-benefits"><header class="section-head">{sun5}<h2 id="s-benefits">{h_ben}</h2></header><ul class="benefit-list">{benefits}</ul></section>
<div class="wrap"><section class="offer" aria-labelledby="s-apply"><h2 id="s-apply">{h_apply}</h2><p>{apply}</p>
  <a class="btn btn-red" href="mailto:jobs@sol.pizza">{email_jobs}</a><p class="privacy-links"><a href="/privacy/" lang="en" hreflang="en">Applicant privacy notice</a> · <a href="/vi/privacy/" lang="vi" hreflang="vi">Thông báo bảo mật ứng viên</a></p></section></div>
{script}
</main>
""".format(
        # While the round is open: hiring now; once it has closed (ROUND_SCRIPT, or a build
        # after the closing instant), the closed line.
        title=page_title(t('Work with us · Tây Hồ, Hanoi', 'Tuyển dụng · Tây Hồ, Hà Nội') if closed
                         else t('We’re hiring · Tây Hồ, Hanoi', 'Tuyển dụng · Tây Hồ, Hà Nội'),
                         t('Come and build the new Sol.', 'Cùng xây dựng Sol mới.'),
                         closed_text() if closed else
                         '<span class="round-live">%s</span><span class="round-note">%s</span>' % (
                             t('We’re hiring now for our opening, in the kitchen and on the floor, and '
                               'every application gets a reply.',
                               'Chúng tôi sắp khai trương. Bếp và khu phục vụ đang tuyển ngay bây giờ, và '
                               'mọi hồ sơ đều nhận được phản hồi.'), closed_text())),
        sun1=sun(1), where=t('Where we need you', 'Chúng tôi cần bạn ở đâu'), roles=roles,
        recent=t('Recently filled', 'Vừa tuyển xong'), filled=filled,
        k_about=t('About Sol', 'Về Sol'),
        h_about=t('A new home, the same standards.', 'Ngôi nhà mới, vẫn những tiêu chuẩn ấy.'),
        a1=t('Sol is a modern Italian-American restaurant in Tây Hồ, with pizza at its heart, a '
             'carefully chosen wine list and a warm, relaxed room.',
             'Sol là nhà hàng Ý–Mỹ hiện đại ở Tây Hồ, với pizza làm trung tâm, danh sách vang được '
             'chọn lọc kỹ và không gian ấm áp, thư giãn.'),
        a2=t('This year we start again in a new building, with a refreshed brand and a bigger team — '
             'and the belief we started with: food quality is non-negotiable. We’re looking for people '
             'who care about good food, real hospitality and doing things properly.',
             'Năm nay chúng tôi bắt đầu lại trong một tòa nhà mới, với thương hiệu được làm mới và '
             'đội ngũ lớn hơn — cùng niềm tin từ ngày đầu: chất lượng món ăn là điều không thể thỏa '
             'hiệp. Chúng tôi tìm những người quan tâm đến món ăn ngon, lòng hiếu khách chân thành '
             'và làm mọi việc cho tử tế.'),
        sun5=sun(5), h_ben=t('What you get, in any role', 'Quyền lợi, dù bạn ở vị trí nào'),
        benefits=''.join('<li>%s%s</li>' % (sun(i + 1), t(en, vi)) for i, (en, vi) in enumerate(BENEFITS)),
        h_apply=t('How to apply', 'Cách ứng tuyển'),
        apply=t('Email your CV to jobs@sol.pizza with the role in the subject line. We read every '
                'application within 5 working days and reply to everyone, including the people we '
                'can’t take forward.',
                'Gửi CV tới jobs@sol.pizza với tên vị trí ở dòng tiêu đề. Chúng tôi đọc mọi hồ sơ trong '
                'vòng 5 ngày làm việc và trả lời tất cả ứng viên, kể cả những bạn chúng tôi chưa thể '
                'mời vào vòng tiếp theo.'),
        email_jobs=t('Email jobs@sol.pizza', 'Gửi email tới jobs@sol.pizza'),
        script=APPLY_SCRIPT,
    )
    page('/jobs/', 'page-jobs',
         ('Work with us — Sol, Tây Hồ', 'Tuyển dụng — Sol, Tây Hồ'),
         ('Work with Sol in Tây Hồ, Hanoi. Applications for our opening team closed on %s %d.'
          % (en_date(CLOSES), CLOSES.year),
          'Làm việc cùng Sol tại Tây Hồ, Hà Nội. Đợt tuyển đội ngũ khai trương đã đóng vào %s.'
          % vi_date(CLOSES, True)) if closed else
         ('We’re hiring a Host and our opening team for the floor and the kitchen. Every application '
          'gets a reply.',
          'Chúng tôi đang tuyển Lễ tân (Host) và đội ngũ khai trương cho khu phục vụ và bếp. Mọi hồ '
          'sơ đều được phản hồi.'),
         main, cur='jobs', og='jobs', extra=ROUND_SCRIPT, body_attrs=' data-page="index"')
    for r in OPEN_ROLES:
        build_open_role(r)
    for r in ROLES:
        build_role(r)


def build_open_role(r):
    """/jobs/<slug>/: the job description word for word, English and Vietnamese."""
    total = [b + s for b, s in zip(r['base'], SERVICE)]
    # Estimated service charge and the typical total, beside the base salary
    added = {
        'en': [('Service charge &amp; tips', 'Est. %s VND per month, starting once we open' % band_en(SERVICE)),
               ('Typical monthly total', '%s VND' % band_en(total))],
        'vi': [('Phí phục vụ &amp; tip', 'Ước tính %s VNĐ/tháng, bắt đầu khi nhà hàng mở cửa' % band_vi(SERVICE)),
               ('Tổng thu nhập hằng tháng (ước tính)', '%s VNĐ' % band_vi(total))],
    }

    def mail_link(text, href):
        # The job description's jobs@sol.pizza: the same prefilled email as the Apply buttons
        if href == 'mailto:' + JOBS_EMAIL:
            return '<a %s>%s</a>' % (apply_attrs(r), text)
        return '<a href="%s">%s</a>' % (esc(href), text)

    facts, prose = [], []
    for lang, jd in zip(('en', 'vi'), r['jd']):
        rows = [(esc(k), jd_inline(v, mail_link)) for k, v in jd['facts']]
        base = [i for i, (k, _) in enumerate(jd['facts']) if k in ('Base salary', 'Lương cơ bản')]
        assert len(base) == 1, 'build/jobs/%s.md: no base salary row in the facts' % r['slug']
        rows[base[0] + 1:base[0] + 1] = added[lang]
        facts.append('<dl class="gtk-items role-facts" data-l="%s" lang="%s">%s</dl>'
                     % (lang, lang, ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % kv for kv in rows)))
        # The role in short stays open; the full description folds, as on the other
        # role pages; How to apply and Our process (the last two sections) stay open.
        h2 = [i for i, (kind, _) in enumerate(jd['blocks']) if kind == 'h2']
        assert len(h2) >= 4, 'build/jobs/%s.md: expected The role in short … How to apply, Our process' % r['slug']
        start, stop = h2[1], h2[-2]
        prose.append(
            '<div class="prose" data-l="%s" lang="%s">\n<p><strong>%s</strong></p>\n%s\n'
            '<details class="full"><summary>%s</summary><div class="fullbody">\n%s\n</div></details>\n%s\n</div>'
            % (lang, lang, jd_inline(jd['standfirst'], mail_link),
               jd_html(jd['blocks'][:start], mail_link),
               'Read the full job description' if lang == 'en' else 'Xem toàn bộ mô tả công việc',
               jd_html(jd['blocks'][start:stop], mail_link), jd_html(jd['blocks'][stop:], mail_link)))
    en, vi = r['jd']
    main = ('<main id="main" class="wrap">\n'
            '<aside class="note-box round-note"><p>%s</p></aside>\n'
            '<header class="page-title"><p class="eyebrow">%s</p><h1>%s</h1>'
            '<div class="actions" data-apply-top>%s</div></header>\n'
            '%s\n%s\n'
            '<div class="actions role-end" data-apply-end>%s<a class="btn btn-outline" href="/jobs/">%s</a></div>\n'
            '<div class="apply-bar">%s</div>\n%s\n</main>\n'
            % (closed_text(), t(esc(en['eyebrow']), esc(vi['eyebrow'])), t(esc(r['name_en']), esc(r['name_vi'])),
               apply_button(r), '\n'.join(facts), '\n'.join(prose), apply_button(r),
               SEE_ROLES, apply_button(r), APPLY_SCRIPT))

    # Search and sharing. The share card is in Vietnamese: the ads bring Vietnamese speakers.
    posting = {
        '@context': 'https://schema.org',
        '@type': 'JobPosting',
        'title': r['name_en'],
        'description': '\n'.join([
            '<p>%s</p>' % esc(en['eyebrow']),
            '<table>%s</table>' % ''.join('<tr><th>%s</th><td>%s</td></tr>' % (esc(k), jd_inline(v, lambda x, h: x))
                                          for k, v in en['facts']),
            '<p><strong>%s</strong></p>' % jd_inline(en['standfirst'], lambda x, h: x),
            jd_html(en['blocks'], lambda x, h: x)]),
        'datePosted': ROUND['posted'],
        'validThrough': ROUND['closes'],
        'employmentType': 'FULL_TIME',
        'hiringOrganization': {'@type': 'Organization', 'name': 'Sol', 'legalName': 'Công ty TNHH Aurelian',
                               'sameAs': SITE, 'logo': SITE + '/favicon.svg'},
        'jobLocation': {'@type': 'Place', 'address': {
            '@type': 'PostalAddress', 'streetAddress': 'Số 7, ngõ 88 Quảng An', 'addressLocality': 'Tây Hồ',
            'addressRegion': 'Hà Nội', 'addressCountry': 'VN'}},
        'baseSalary': {'@type': 'MonetaryAmount', 'currency': 'VND', 'value': {
            '@type': 'QuantitativeValue', 'minValue': r['base'][0], 'maxValue': r['base'][1], 'unitText': 'MONTH'}},
        'directApply': False,
    }
    if r['openings']:
        posting['totalJobOpenings'] = r['openings']
    ld = '<script type="application/ld+json">\n%s\n</script>' % json.dumps(
        posting, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    og_title = 'Tuyển %s — Sol, Tây Hồ' % r['name_en']
    og_desc = 'Lương cơ bản %s + phí phục vụ ước tính %s/tháng. Hạn nộp %s.' % (
        trieu(r['base']), trieu(SERVICE), vi_date(CLOSES, True).split(' ')[-1])
    desc_en = ('%s at Sol, Tây Hồ, Hanoi. Base salary %s VND a month, plus service charge and tips, est. '
               '%s VND a month. Applications close %s %d.'
               % (r['name_en'], band_en(r['base'], '–'), band_en(SERVICE, '–'), en_date(CLOSES), CLOSES.year))
    desc_vi = 'Tuyển %s tại Sol, Tây Hồ, Hà Nội. %s' % (r['name_vi'], og_desc)
    page(open_role_path(r), 'page-role',
         (esc_attr('%s — Sol, Tây Hồ' % r['name_en']), esc_attr('%s — Sol, Tây Hồ' % r['name_vi'])),
         (esc_attr(fit(desc_en, 200)), esc_attr(fit(desc_vi, 200))), main, cur='role', og='jobs',
         # The Vietnamese page's share card speaks to the ads' Vietnamese readers
         og_text=((esc_attr('%s — Sol, Tây Hồ' % r['name_en']), esc_attr(desc_en)),
                  (esc_attr(og_title), esc_attr(og_desc))), bar=False,
         extra=ROUND_SCRIPT + '\n' + ld,
         body_attrs=' data-page="role" data-role="%s" data-slug="%s"' % (esc_attr(r['name_en']), r['slug']))


def build_role(r):
    """An existing role page in the site shell, its copy untouched."""
    h = read(os.path.join(SRC, 'jobs', r['src']))
    hero = re.search(r'<div class="hero"><div class="wrap">(.*?)</div></div>\s*<main', h, re.S).group(1)
    inner = re.search(r'<main><div class="wrap">(.*?)</div></main>', h, re.S).group(1)
    title = re.search(r'<title>(.*?)</title>', h, re.S).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h).group(1)

    def grab(pat):
        m = re.search(pat, hero, re.S)
        return m.group(1).strip() if m else ''

    eyebrow = grab(r'<p class="eyebrow">(.*?)</p>')
    subtitle = grab(r'<p class="subtitle">(.*?)</p>')
    standfirst = grab(r'<p class="standfirst">(.*?)</p>')
    facts = re.findall(r'<div><dt>(.*?)</dt><dd>(.*?)</dd></div>', grab(r'<dl class="facts">(.*?)</dl>'))
    filled = r['status'] == 'filled'
    # Deadlines and start dates are stale once a role is filled.
    drop = {'Closes'} | ({'Starts'} if filled else set())
    facts = [(k, v) for k, v in facts if k not in drop]

    inner = re.sub(r'<div class="others">.*?</div></div>', '', inner, flags=re.S)
    if filled:
        inner = re.sub(r'<section class="apply" id="apply">.*?</section>', '', inner, flags=re.S)
    inner = inner.replace('class="kicker"', 'class="eyebrow"').replace(' class="lede"', '')

    banner = ''
    if filled:
        banner = '<aside class="note-box"><p>%s</p></aside>\n' % t(
            'This role has been filled. Thank you to everyone who applied.',
            'Vị trí này đã tuyển xong. Cảm ơn tất cả các bạn đã ứng tuyển.')
    main = ('<main id="main" class="wrap">\n' + banner +
            '<header class="page-title"><p class="eyebrow" lang="en">%s</p><h1>%s</h1>%s</header>\n'
            % (eyebrow, t(r['name_en'], r['name_vi']),
               '<p class="page-lead" lang="en">%s</p>' % subtitle if subtitle else '') +
            '<dl class="gtk-items" lang="en">%s</dl>\n'
            % ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % f for f in facts) +
            '<div class="prose" lang="en">\n'
            '<p class="vi-note" data-l="vi" lang="vi">Bản mô tả công việc này chỉ có bằng tiếng Anh.</p>\n'
            '<p>%s</p>\n%s\n</div>\n</main>\n' % (standfirst, inner.strip()))
    if filled:
        # The source page's title and description still advertise the role
        # ("…is hiring… Applications close…"); say it's filled instead.
        titles = ('%s — Sol, Tây Hồ' % r['name_en'], '%s — Sol, Tây Hồ' % r['name_vi'])
        descs = ('The %s role at Sol, Tây Hồ, Hanoi. This role has been filled.' % r['name_en'],
                 'Mô tả công việc %s tại Sol, Tây Hồ, Hà Nội. Vị trí này đã tuyển xong.'
                 % r['name_vi'].lower())
    else:
        titles = (title, '%s — Sol, Tây Hồ' % r['name_vi'])
        descs = (desc, 'Mô tả công việc %s tại Sol, Tây Hồ, Hà Nội.' % r['name_vi'].lower())
    page(role_path(r), 'page-role', titles, descs,
         main, cur='role', og='%s/jobs/og-%s.png' % (SITE, r['slug']), bar=False,
         extra='<meta name="robots" content="noindex,follow">' if filled else '',
         body_attrs=' data-page="%s" data-role="%s" data-slug="%s"'
                    % ('role-filled' if filled else 'role', r['name_en'], r['slug']))


# ==========================================================================
# PRIVACY  /privacy/   (src/privacy/index.html, text untouched)
# ==========================================================================
def build_privacy():
    h = read(os.path.join(SRC, 'privacy', 'index.html'))
    title = re.search(r'<title>(.*?)</title>', h, re.S).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h).group(1)
    body = re.search(r'<main><div class="wrap">(.*)</div></main>', h, re.S).group(1)
    en = body.split('<div class="langblock" id="en">', 1)[1].split('<div class="langblock">', 1)[0]
    vi = body.split('<div class="langblock">', 1)[1]

    def block(part, lang, block_id):
        part = part.strip()
        assert part.endswith('</div>'), 'privacy: unexpected markup'
        part = part[:-len('</div>')].strip()
        h1 = re.search(r'<h1[^>]*>.*?</h1>', part, re.S).group(0)
        part = part.replace(h1, '', 1).strip()
        return ('<div data-l="%s" lang="%s" id="%s"><header class="page-title">%s</header>\n'
                '<div class="prose">\n%s\n</div></div>\n' % (lang, lang, block_id, h1, part))

    main = ('<main id="main" class="wrap">\n' + block(en, 'en', 'en') + block(vi, 'vi', 'vi-notice') + '</main>\n')
    return page('/privacy/', 'page-privacy',
                (title, 'Thông báo bảo mật dành cho ứng viên — Sol'),
                (desc, 'Cách Sol thu thập, sử dụng và lưu trữ dữ liệu cá nhân của ứng viên, theo Luật '
                       'Bảo vệ dữ liệu cá nhân số 91/2025/QH15.'),
                main, index=False, extra='<meta name="robots" content="noindex, follow">',
                body_attrs=' data-page="privacy"', verbatim=True)


# ==========================================================================
# COOKIES  /privacy/cookies/   what the site stores in the browser, and the choice
# The short notice that goes with the consent banner (consent_banner(), site.js).
# Cleared by the lawyer with the banner (13 Oct 2026). If what the site stores
# changes, change this table, the banner and CONSENT_VERSION together.
# ==========================================================================
COOKIES_UPDATED = date(2026, 10, 13)


def build_cookies():
    def row(name, what, how_long, who):
        return '<tr><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (name, what, how_long, who)

    def table(rows):
        return ('<div class="tablewrap"><table><thead><tr><th scope="col">%s</th><th scope="col">%s</th>'
                '<th scope="col">%s</th><th scope="col">%s</th></tr></thead><tbody>%s</tbody></table></div>'
                % (t('Name', 'Tên'), t('What it does', 'Dùng để làm gì'), t('How long', 'Lưu bao lâu'),
                   t('Whose', 'Của ai'), ''.join(rows)))
    sol = 'Sol'
    year = t('12 months', '12 tháng')
    until = t('Until you clear it', 'Đến khi bạn xoá')
    sections = [
        ('<p>%s</p>' % t(
            'sol.pizza is the website of Sol, a restaurant run by %s (%s) at No 7, Lane 88 Quang An Street, '
            'Tây Hồ, Hanoi. This notice lists what the site keeps in your browser, and the choice you have '
            'about it. It follows the Law on Personal Data Protection No. 91/2025/QH15 and Decree '
            '356/2025/ND-CP.' % (COMPANY_VI, COMPANY_EN),
            'sol.pizza là trang web của Sol, nhà hàng do %s điều hành tại số 7, ngõ 88 Quảng An, Tây Hồ, '
            'Hà Nội. Thông báo này liệt kê những gì trang web lưu trong trình duyệt của bạn, và lựa chọn của '
            'bạn về việc đó, theo Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 và Nghị định 356/2025/NĐ-CP.'
            % COMPANY_VI)),
        '<h2>%s</h2><p>%s</p>%s' % (
            t('Always on', 'Luôn bật'),
            t('The site needs these to remember what you chose. They stay in your browser and tell us '
              'nothing about you.',
              'Trang web cần những mục này để nhớ lựa chọn của bạn. Chúng nằm trong trình duyệt của bạn và '
              'không cho chúng tôi biết gì về bạn.'),
            table([
                row('sol-consent', t('Your cookie choice', 'Lựa chọn cookie của bạn'), year, sol),
                row('sol-lang', t('The language you picked', 'Ngôn ngữ bạn đã chọn'), until, sol),
                row('sol-ann-…', t('That you closed an announcement', 'Bạn đã đóng một thông báo'), until, sol),
                row('cf_clearance', t('Security: tells people from automated traffic. Set by Cloudflare, which '
                                      'serves the site.',
                                      'Bảo mật: phân biệt người dùng với truy cập tự động. Do Cloudflare, đơn vị '
                                      'vận hành máy chủ của trang, thiết lập.'),
                    year, 'Cloudflare'),
            ])),
        '<h2>%s</h2><p>%s</p>%s' % (
            t('Analytics: only if you say yes', 'Phân tích: chỉ khi bạn đồng ý'),
            t('Google Analytics shows us which pages are read and how people find us. Google may process '
              'this data outside Vietnam.',
              'Google Analytics cho chúng tôi biết những trang nào được đọc và khách tìm đến chúng tôi bằng '
              'cách nào. Google có thể xử lý dữ liệu này ở ngoài Việt Nam.'),
            table([row('_ga, _ga_%s' % GA_ID[2:], t('Counts visits, and tells one visitor from another',
                                                   'Đếm lượt truy cập, và phân biệt các khách truy cập'),
                       t('Up to 2 years', 'Tối đa 2 năm'), 'Google')])),
        '<h2>%s</h2><p>%s</p>%s' % (
            t('Advertising: only if you say yes', 'Quảng cáo: chỉ khi bạn đồng ý'),
            t('The Meta Pixel tells us whether our ads on Facebook and Instagram bring people to the site. '
              'Meta may process this data outside Vietnam.',
              'Meta Pixel cho chúng tôi biết quảng cáo trên Facebook và Instagram có đưa khách đến trang web '
              'không. Meta có thể xử lý dữ liệu này ở ngoài Việt Nam.'),
            table([row('_fbp, _fbc', t('Recognise a visit that came from one of our ads',
                                       'Nhận biết lượt truy cập đến từ quảng cáo của chúng tôi'),
                       t('90 days', '90 ngày'), 'Meta'),
                   row('lastExternalReferrer', t('Where the visit came from', 'Lượt truy cập đến từ đâu'),
                       until, 'Meta')])),
        '<h2>%s</h2><p>%s</p><p>%s</p>' % (
            t('Your choice', 'Lựa chọn của bạn'),
            t('Nothing in Analytics or Advertising loads until you choose, and the site works the same '
              'whichever you choose. Change your mind any time with Cookie settings at the foot of every page: '
              'if you take back a yes, we remove those cookies and stop loading the tool. We ask again after '
              '12 months.',
              'Không có mục Phân tích hay Quảng cáo nào được tải trước khi bạn chọn, và trang web hoạt động như '
              'nhau dù bạn chọn thế nào. Bạn có thể đổi lựa chọn bất cứ lúc nào ở mục Cài đặt cookie cuối mỗi '
              'trang: nếu bạn rút lại sự đồng ý, chúng tôi xoá các cookie đó và ngừng tải công cụ tương ứng. '
              'Sau 12 tháng, chúng tôi sẽ hỏi lại.'),
            '<button class="btn btn-outline btn-sm" type="button" data-consent-open>%s</button>'
            % t('Cookie settings', 'Cài đặt cookie')),
        '<h2>%s</h2><p>%s</p>' % (
            t('Questions', 'Câu hỏi'),
            t('Write to <a href="mailto:%s">%s</a>. If you applied for a job with us, the '
              '<a href="/privacy/">applicant privacy notice</a> explains how we handle your application.'
              % (EMAIL, EMAIL),
              'Hãy viết cho chúng tôi qua <a href="mailto:%s">%s</a>. Nếu bạn đã ứng tuyển tại Sol, '
              '<a href="/privacy/">thông báo bảo mật dành cho ứng viên</a> giải thích cách chúng tôi xử lý '
              'hồ sơ của bạn.' % (EMAIL, EMAIL))),
    ]
    main = ('<main id="main" class="wrap">\n<header class="page-title"><p class="eyebrow">%s</p><h1>%s</h1>'
            '<p class="page-lead updated">%s</p></header>\n<div class="prose prose-legal">\n%s\n</div>\n</main>\n'
            % (t('Privacy', 'Bảo mật'), t('Cookies on sol.pizza', 'Cookie trên sol.pizza'),
               t('Last updated %d %s %d' % (COOKIES_UPDATED.day, EN_MONTHS[COOKIES_UPDATED.month - 1],
                                           COOKIES_UPDATED.year),
                 'Cập nhật lần cuối: %02d/%02d/%d' % (COOKIES_UPDATED.day, COOKIES_UPDATED.month,
                                                     COOKIES_UPDATED.year)),
               '\n'.join(sections)))
    return page('/privacy/cookies/', 'page-legal',
                ('Cookies — Sol', 'Cookie — Sol'),
                ('What sol.pizza keeps in your browser, and how to change your choice.',
                 'Những gì sol.pizza lưu trong trình duyệt của bạn, và cách thay đổi lựa chọn.'),
                main, index=False, extra='<meta name="robots" content="noindex, follow">')


# ==========================================================================
# GUEST PRIVACY  /privacy/guests/   ACCESSIBILITY  /accessibility/
# Drafts for the lawyer, written in full; each waits (WAITING) until approved, so
# only the full previews show it, with a "Draft" note that goes with the approval.
# ==========================================================================
LEGAL_UPDATED = date(2026, 10, 13)
TO_COME = t('[to come]', '[sẽ cập nhật]')


def legal_page(path, eyebrow, h1, sections, title, desc, index=False):
    draft = (note_box(t('Draft', 'Bản nháp'), t('For the lawyer’s review: not on sol.pizza until approved.',
                                                 'Chờ luật sư xem xét: chưa đăng lên sol.pizza cho đến khi được duyệt.'))
             if path in WAITING else '')
    updated = t('Last updated %d %s %d' % (LEGAL_UPDATED.day, EN_MONTHS[LEGAL_UPDATED.month - 1], LEGAL_UPDATED.year),
                'Cập nhật lần cuối: %02d/%02d/%d' % (LEGAL_UPDATED.day, LEGAL_UPDATED.month, LEGAL_UPDATED.year))
    main = ('<main id="main" class="wrap">\n<header class="page-title"><p class="eyebrow">%s</p><h1>%s</h1>'
            '<p class="page-lead updated">%s</p></header>\n%s<div class="prose prose-legal">\n%s\n</div>\n</main>\n'
            % (eyebrow, h1, updated, draft, '\n'.join(sections)))
    return page(path, 'page-legal', title, desc, main, og='home', index=index,
                extra='' if index else '<meta name="robots" content="noindex, follow">')


def build_guest_privacy():
    def row(what, data, why):
        return '<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (what, data, why)
    sections = [
        '<p>%s</p>' % t(
            'Sol is a restaurant run by %s (%s) at No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi. This notice '
            'explains what we keep about you when you book a table, write to us or sign up for our news, why, '
            'who handles it for us, and your rights. It follows the Law on Personal Data Protection No. '
            '91/2025/QH15 and Decree 356/2025/ND-CP.' % (COMPANY_VI, COMPANY_EN),
            'Sol là nhà hàng do %s điều hành tại số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Thông báo này giải thích '
            'những thông tin chúng tôi lưu về bạn khi bạn đặt bàn, viết cho chúng tôi hoặc đăng ký nhận tin, vì sao, '
            'ai xử lý thông tin đó cho chúng tôi, và các quyền của bạn, theo Luật Bảo vệ dữ liệu cá nhân số '
            '91/2025/QH15 và Nghị định 356/2025/NĐ-CP.' % COMPANY_VI),
        '<h2>%s</h2><div class="tablewrap"><table><thead><tr><th scope="col">%s</th><th scope="col">%s</th>'
        '<th scope="col">%s</th></tr></thead><tbody>%s</tbody></table></div>' % (
            t('What we keep, and why', 'Chúng tôi lưu gì, và vì sao'),
            t('When', 'Khi nào'), t('What', 'Thông tin gì'), t('Why', 'Để làm gì'), ''.join([
                row(t('You book a table', 'Bạn đặt bàn'),
                    t('Your name, phone number and email; the day, time and size of your party; anything you add, '
                      'such as an occasion or an allergy',
                      'Họ tên, số điện thoại và email; ngày, giờ và số khách; những gì bạn ghi thêm, như một dịp '
                      'đặc biệt hay một loại dị ứng'),
                    t('To hold your table, to reach you about it, and to get ready for your visit',
                      'Để giữ bàn, liên hệ với bạn về việc đặt bàn, và chuẩn bị cho buổi tối của bạn')),
                row(t('You write to us', 'Bạn viết cho chúng tôi'),
                    t('What you write, and your contact details (the private dining and opening-week forms '
                      'write an email from your own app)',
                      'Nội dung bạn viết và thông tin liên hệ (các biểu mẫu tiệc riêng và tuần khai trương soạn '
                      'một email từ ứng dụng của chính bạn)'),
                    t('To answer you, and to plan your event', 'Để trả lời bạn, và lên kế hoạch cho buổi tiệc')),
                row(t('You sign up for news', 'Bạn đăng ký nhận tin'),
                    t('Your email address, and the day you asked', 'Địa chỉ email, và ngày bạn đăng ký'),
                    t('To send you news from Sol now and then, until you ask us to stop',
                      'Để thỉnh thoảng gửi tin từ Sol, cho đến khi bạn yêu cầu dừng')),
            ])),
        '<p>%s</p>' % t('What the website keeps in your browser is in the <a href="/privacy/cookies/">cookie '
                        'notice</a>.',
                        'Những gì trang web lưu trong trình duyệt của bạn có trong <a href="/privacy/cookies/">'
                        'thông báo về cookie</a>.'),
        '<h2>%s</h2><p>%s</p>' % (
            t('Allergies and dietary needs', 'Dị ứng và chế độ ăn'),
            t('If you tell us about an allergy or a dietary need, we use it only to prepare your meal safely, and '
              'share it only with the team looking after you that night. Information about your health is '
              'sensitive personal data: we ask for your consent before we record it, and you can ask us to '
              'delete it at any time.',
              'Nếu bạn cho chúng tôi biết về một loại dị ứng hay chế độ ăn, chúng tôi chỉ dùng thông tin đó để chuẩn '
              'bị món ăn an toàn cho bạn, và chỉ chia sẻ với những người phục vụ bạn tối hôm đó. Thông tin về sức '
              'khỏe là dữ liệu cá nhân nhạy cảm: chúng tôi hỏi ý kiến đồng ý của bạn trước khi ghi lại, và bạn có '
              'thể yêu cầu xoá bất cứ lúc nào.')),
        '<h2>%s</h2><p>%s</p><ul>%s</ul><p>%s</p><p>%s</p>' % (
            t('Who handles it for us', 'Ai xử lý thông tin cho chúng tôi'),
            t('These companies store or process it on our behalf, and only as we ask:',
              'Các công ty sau lưu trữ hoặc xử lý thông tin thay mặt chúng tôi, và chỉ theo yêu cầu của chúng tôi:'),
            ''.join('<li>%s</li>' % x for x in [
                t('ResDiary: our booking system', 'ResDiary: hệ thống đặt bàn của chúng tôi'),
                t('Google Workspace: our email', 'Google Workspace: hộp thư của chúng tôi'),
                t('Cloudflare: serves this website', 'Cloudflare: vận hành máy chủ cho trang web này'),
                t('Adobe Fonts: the website’s typefaces (when they load, it sees your browser’s internet address '
                  'and counts the page view)',
                  'Adobe Fonts: phông chữ của trang web (khi tải phông chữ, dịch vụ này thấy địa chỉ internet của '
                  'trình duyệt và đếm lượt xem trang)'),
            ]),
            t('If you say yes to them in the cookie banner, Google Analytics and Meta also receive information '
              'about your visit: the <a href="/privacy/cookies/">cookie notice</a> explains.',
              'Nếu bạn đồng ý trong bảng chọn cookie, Google Analytics và Meta cũng nhận thông tin về lượt truy '
              'cập của bạn: <a href="/privacy/cookies/">thông báo về cookie</a> giải thích rõ.'),
            t('Some of them keep data outside Vietnam.', 'Một số công ty lưu dữ liệu ở ngoài Việt Nam.')),
        '<h2>%s</h2><ul>%s</ul>' % (
            t('How long we keep it', 'Chúng tôi lưu trong bao lâu'),
            ''.join('<li>%s</li>' % x for x in [
                t('Bookings: %s' % TO_COME, 'Đặt bàn: %s' % TO_COME),
                t('Emails and enquiries: %s' % TO_COME, 'Email và yêu cầu: %s' % TO_COME),
                t('News by email: until you ask us to stop', 'Tin qua email: cho đến khi bạn yêu cầu dừng'),
            ])),
        '<h2>%s</h2><p>%s</p><p>%s</p>' % (
            t('Your rights', 'Quyền của bạn'),
            t('You can ask to see what we keep about you, to correct it or delete it, to take back your consent, '
              'or to object to how we use it. Write to <a href="mailto:%s">%s</a>.' % (EMAIL, EMAIL),
              'Bạn có thể yêu cầu xem những gì chúng tôi lưu về bạn, sửa hoặc xoá thông tin đó, rút lại sự đồng '
              'ý, hoặc phản đối cách chúng tôi sử dụng. Hãy viết cho chúng tôi qua <a href="mailto:%s">%s</a>.'
              % (EMAIL, EMAIL)),
            t('You can also complain to the Ministry of Public Security’s Department of Cybersecurity and '
              'High-Tech Crime Prevention (A05), which oversees personal data protection.',
              'Bạn cũng có thể khiếu nại tới Cục An ninh mạng và phòng, chống tội phạm sử dụng công nghệ cao '
              '(A05), Bộ Công an, cơ quan chuyên trách bảo vệ dữ liệu cá nhân.')),
        '<h2>%s</h2><p>%s</p>' % (
            t('Questions', 'Câu hỏi'),
            t('Write to <a href="mailto:%s">%s</a>. If you applied for a job with us, the '
              '<a href="/privacy/">applicant privacy notice</a> explains how we handle your application.'
              % (EMAIL, EMAIL),
              'Hãy viết cho chúng tôi qua <a href="mailto:%s">%s</a>. Nếu bạn đã ứng tuyển tại Sol, '
              '<a href="/privacy/">thông báo bảo mật dành cho ứng viên</a> giải thích cách chúng tôi xử lý '
              'hồ sơ của bạn.' % (EMAIL, EMAIL))),
    ]
    return legal_page('/privacy/guests/', t('Privacy', 'Bảo mật'),
                      t('Your privacy as our guest', 'Quyền riêng tư của khách'), sections,
                      ('Guest privacy — Sol', 'Quyền riêng tư của khách — Sol'),
                      ('What Sol keeps when you book, write to us or sign up for news, and your rights.',
                       'Những gì Sol lưu khi bạn đặt bàn, viết cho chúng tôi hoặc đăng ký nhận tin, và quyền của bạn.'))


def build_accessibility():
    sections = [
        '<p>%s</p>' % t('We want everyone to be able to use sol.pizza, and to visit Sol. This statement covers '
                        'both.',
                        'Chúng tôi muốn ai cũng có thể sử dụng sol.pizza và đến Sol. Bản tuyên bố này nói về cả hai.'),
        '<h2>%s</h2><p>%s</p><p>%s</p>' % (
            t('The website', 'Trang web'),
            t('We aim to meet the Web Content Accessibility Guidelines (WCAG) 2.2 at level AA. We test every '
              'page, in English and Vietnamese, on a phone and a computer, with an automated accessibility '
              'checker (axe), and check the menu, the cookie choices and the enquiry forms with a keyboard.',
              'Chúng tôi hướng tới đáp ứng Hướng dẫn về khả năng tiếp cận nội dung web (WCAG) 2.2, mức AA. Chúng '
              'tôi kiểm tra mọi trang, bằng tiếng Anh và tiếng Việt, trên điện thoại và máy tính, bằng công cụ '
              'kiểm tra khả năng tiếp cận tự động (axe), và kiểm tra menu, lựa chọn cookie và các biểu mẫu bằng '
              'bàn phím.'),
            t('The site works the same whether or not you accept cookies, and moves less when your device asks '
              'for less motion.',
              'Trang web hoạt động như nhau dù bạn có chấp nhận cookie hay không, và hạn chế chuyển động khi thiết '
              'bị của bạn yêu cầu.')),
        '<h2>%s</h2><p>%s</p>' % (
            t('Booking', 'Đặt bàn'),
            t('The booking form comes from ResDiary, inside our page. If it gives you any trouble, call us on '
              '%s or write to <a href="mailto:%s">%s</a>, and we’ll book for you.' % (PHONE, EMAIL, EMAIL),
              'Biểu mẫu đặt bàn là của ResDiary, nằm trong trang của chúng tôi. Nếu bạn gặp khó khăn, hãy gọi '
              '%s hoặc viết cho chúng tôi qua <a href="mailto:%s">%s</a>, chúng tôi sẽ đặt bàn giúp bạn.'
              % (PHONE, EMAIL, EMAIL)) if RESDIARY_URL else
            t('To book, call us on %s or write to <a href="mailto:%s">%s</a>, and we’ll look after the rest.'
              % (PHONE, EMAIL, EMAIL),
              'Để đặt bàn, hãy gọi %s hoặc viết cho chúng tôi qua <a href="mailto:%s">%s</a>, chúng tôi sẽ lo '
              'phần còn lại.' % (PHONE, EMAIL, EMAIL))),
        '<h2>%s</h2><p>%s</p>' % (
            t('The restaurant', 'Nhà hàng'),
            t('Step-free access, the lift and the toilets: %s' % TO_COME,
              'Lối vào không bậc thềm, thang máy và nhà vệ sinh: %s' % TO_COME)),
        '<h2>%s</h2><p>%s</p>' % (
            t('Tell us', 'Hãy cho chúng tôi biết'),
            t('If something on the site or at the restaurant gets in your way, tell us: '
              '<a href="mailto:%s">%s</a> or %s. We’ll answer, and fix what we can.' % (EMAIL, EMAIL, PHONE),
              'Nếu có điều gì trên trang web hay tại nhà hàng gây trở ngại cho bạn, hãy cho chúng tôi biết qua '
              '<a href="mailto:%s">%s</a> hoặc %s. Chúng tôi sẽ trả lời, và khắc phục những gì có thể.'
              % (EMAIL, EMAIL, PHONE))),
    ]
    return legal_page('/accessibility/', t('Accessibility', 'Hỗ trợ tiếp cận'),
                      t('Accessibility', 'Hỗ trợ tiếp cận'), sections,
                      ('Accessibility — Sol', 'Hỗ trợ tiếp cận — Sol'),
                      ('How sol.pizza and Sol work for everyone, and how to tell us when they don’t.',
                       'sol.pizza và Sol phục vụ mọi người như thế nào, và cách báo cho chúng tôi khi có trở ngại.'),
                      index=True)


# ==========================================================================
# GIFT CARDS  /gift-cards/   waits for its facts (WAITING)
# PRESS  /press/   the facts, the logo, photographs and who to ask
# ==========================================================================
def build_gift_cards():
    rows = [(t('Values', 'Mệnh giá'), TO_COME),
            (t('How long a card lasts', 'Thời hạn sử dụng'), TO_COME),
            (t('How to buy one', 'Cách mua'),
             t('At the restaurant, or by email: write to <a href="mailto:%s">%s</a>.' % (EMAIL, EMAIL),
               'Tại nhà hàng, hoặc qua email: hãy viết cho chúng tôi qua <a href="mailto:%s">%s</a>.'
               % (EMAIL, EMAIL)))]
    main = '\n'.join([
        '<main id="main">',
        '<div class="wrap">%s</div>' % page_title(t('Gift cards', 'Thẻ quà tặng'),
                                                  t('Give someone dinner at Sol', 'Tặng một bữa tối tại Sol'),
                                                  t('A gift card for Sol, in Tây Hồ.', 'Thẻ quà tặng của Sol, ở Tây Hồ.')),
        '<section class="prose-section wrap" %s><dl class="gtk-items">%s</dl></section>'
        % (label('Gift cards', 'Thẻ quà tặng'), ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % r for r in rows)),
        '</main>', ''])
    return page('/gift-cards/', 'page-gift-cards', ('Gift cards — Sol, Tây Hồ', 'Thẻ quà tặng — Sol, Tây Hồ'),
                ('A gift card for Sol, the Italian-American restaurant in Tây Hồ, Hanoi.',
                 'Thẻ quà tặng của Sol, nhà hàng Ý–Mỹ tại Tây Hồ, Hà Nội.'), main, og='home')


def press_photos():
    """The photographs the press may use: each with its credit and its full-size file."""
    ps = photos_for('press')
    if not ps:
        return '<div class="wrap">%s</div>' % (photo_placeholder('press', SLOTS['press']) if FULL else '')
    return ('<section class="prose-section wrap" aria-labelledby="s-photos"><header class="section-head">%s'
            '<h2 id="s-photos">%s</h2></header><ul class="press-photos">%s</ul></section>'
            % (sun(6), t('Photographs', 'Hình ảnh'), ''.join(
                '<li><figure>%s<figcaption>%s · <a href="%s%s" %s>%s</a></figcaption></figure></li>'
                % (picture(p, SLOTS['press']), t('Photo: %s' % esc(p['credit']), 'Ảnh: %s' % esc(p['credit'])),
                   MEDIA_BASE, p['key'], label(esc_attr('Full size: ' + p['alt_en']), esc_attr('Ảnh gốc: ' + p['alt_vi'])),
                   t('Full size', 'Ảnh gốc')) for p in ps)))


def build_press():
    opening = t('%s %d' % (en_date(OPENING_DAY), OPENING_DAY.year) if OPENING_DAY else 'Soon',
                vi_date(OPENING_DAY, year=True)[0].upper() + vi_date(OPENING_DAY, year=True)[1:]
                if OPENING_DAY else 'Sắp tới')
    facts = [
        (t('Name', 'Tên'), 'Sol'),
        (t('What it is', 'Sol là gì'),
         t('An Italian-American restaurant: pizza from a wood-fired oven, pasta made in-house, and %d wines, %d '
           'of them by the glass.' % (WINES_TOTAL, WINES_GLASS),
           'Nhà hàng Ý–Mỹ: pizza lò củi, mì Ý làm tại nhà hàng và %d loại vang, %d loại có phục vụ theo ly.'
           % (WINES_TOTAL, WINES_GLASS))),
        (t('Where', 'Địa chỉ'), t(ADDRESS_EN, ADDRESS_VI)),
    ] + ([(t('Opening', 'Khai trương'), opening, 'when-pre')] if SITE_STATE != 'open' else []) + [
        (t('Hours', 'Giờ mở cửa'), t(*HOURS_PLAIN)),
        (t('The oven', 'Lò nướng'), t('A Pavesi wood-fired oven, built in Italy.', 'Lò củi Pavesi, chế tác tại Ý.')),
        (t('Before Sol', 'Trước Sol'), t('Sol Pizza, in Tây Hồ until last year.', 'Sol Pizza, ở Tây Hồ cho đến năm ngoái.')),
        (t('The kitchen', 'Bếp'), t('Ngọc runs the kitchen.', 'Ngọc phụ trách bếp.')),
        (t('The company', 'Công ty'), '%s (%s)' % (COMPANY_VI, COMPANY_EN)),
        (t('Online', 'Trực tuyến'), '<a href="/">sol.pizza</a> · %s' % INSTA_LINK),
    ]
    if PRESS_CONTACT:
        contact = '%s · <a href="mailto:%s">%s</a>' % (esc(PRESS_CONTACT[0]), PRESS_CONTACT[1], PRESS_CONTACT[1])
    else:
        contact = gate('press-contact', 'who answers the press: a name and an email (PRESS_CONTACT in gen.py)',
                       t('[Name, email]', '[Tên, email]'),
                       t('Write to <a href="mailto:%s">%s</a>.' % (EMAIL, EMAIL),
                         'Hãy viết cho chúng tôi qua <a href="mailto:%s">%s</a>.' % (EMAIL, EMAIL)), tag='span')
    main = '\n'.join([
        '<main id="main">',
        '<div class="wrap">%s</div>' % page_title(t('Press', 'Báo chí'), t('For the press', 'Dành cho báo chí'),
                                                  t('The facts, the logo, and who to ask.',
                                                    'Thông tin, logo và đầu mối liên hệ.')),
        '<section class="prose-section wrap" aria-labelledby="s-facts"><header class="section-head">%s<h2 id="s-facts">%s'
        '</h2></header><dl class="gtk-items">%s</dl></section>'
        % (sun(1), t('The facts', 'Thông tin'), ''.join(
            # the opening row goes on opening day (by_state(), in the browser with a date)
            '<div%s><dt>%s</dt><dd>%s</dd></div>' % (' class="%s"' % f[2] if len(f) > 2 and OPENING_DATE else '',
                                                    f[0], f[1]) for f in facts)),
        '<section class="prose-section wrap" aria-labelledby="s-logo"><header class="section-head">%s<h2 id="s-logo">%s'
        '</h2></header><div class="press-logo"><img src="/assets/sol-primary-red.svg" alt="%s" width="240" height="85">'
        '<p>%s</p><a class="btn btn-outline" href="/assets/sol-primary-red.svg" download="sol-logo.svg">%s</a></div>'
        '</section>'
        % (sun(4), t('The logo', 'Logo'), 'Sol', t('In Sol red. Please use it as it is: don’t recolour, stretch or '
                                                  'redraw it.',
                                                  'Màu đỏ Sol. Vui lòng dùng nguyên bản: không đổi màu, kéo giãn hay '
                                                  'vẽ lại.'),
           t('Download the logo (SVG)', 'Tải logo (SVG)')),
        press_photos(),
        '<div class="wrap"><section class="offer" aria-labelledby="s-press-contact"><h2 id="s-press-contact">%s</h2>'
        '<p>%s</p></section></div>' % (t('Who to ask', 'Liên hệ'), contact),
        '</main>', ''])
    return page('/press/', 'page-press', ('Press — Sol, Tây Hồ', 'Báo chí — Sol, Tây Hồ'),
                ('Sol for the press: the facts, the logo, and who to ask. An Italian-American restaurant at No 7, '
                 'Lane 88 Quang An, Tây Hồ, Hanoi.',
                 'Thông tin về Sol dành cho báo chí: thông tin, logo và đầu mối liên hệ. Nhà hàng Ý–Mỹ tại số 7, '
                 'ngõ 88 Quảng An, Tây Hồ, Hà Nội.'), main, og='home')


# ==========================================================================
# COMPONENTS  /styleguide/   the full build only (full-site and the full/… previews)
# The parts pages are built from, in one place to review: after-dark sections, an
# image band, a gallery, cards, a quote, the "Content needed" marker. Placeholders
# only: never written to the public build, never in the sitemap.
# ==========================================================================
def build_styleguide():
    if not FULL:
        return None

    def ph(ratio, text):
        return '<div class="ph" style="aspect-ratio:%s">%s</div>' % (ratio, text)
    example = t('Example', 'Ví dụ')
    main = '\n'.join([
        '<main id="main">',
        '<div class="wrap">%s</div>' % page_title(
            t('Full build only', 'Chỉ có ở bản đầy đủ'), t('The parts pages are built from', 'Các thành phần của trang'),
            t('Placeholders, not content: this page is never on sol.pizza.',
              'Chỉ là chỗ giữ chỗ, không phải nội dung: trang này không bao giờ có trên sol.pizza.')),
        '<section class="after-dark" aria-labelledby="sg-dark"><div class="wrap measure">'
        '<p class="eyebrow">%s</p><h2 class="h-lg" id="sg-dark">%s</h2><p>%s</p>'
        '<div class="actions"><a class="btn btn-red" href="/booking/#book">%s</a><a class="btn btn-outline" href="/menu/">%s</a></div>'
        '<p style="margin-top:22px"><a href="/visit-us/">%s</a></p></div></section>' % (
            t('After dark', 'Sau hoàng hôn'), t('Wood brown, cream and sun', 'Nâu gỗ, kem và vàng nắng'),
            t('Cream type on wood is 11:1, sun yellow 8.5:1. Buttons turn sun yellow here, and so does the focus ring.',
              'Chữ màu kem trên nền nâu gỗ đạt 11:1, vàng nắng 8,5:1. Ở đây nút bấm và viền tiêu điểm chuyển sang vàng nắng.'),
            BOOK, t('See the menu', 'Xem thực đơn'), t('A link', 'Một liên kết')),
        '<figure class="band">%s<figcaption class="wrap">%s</figcaption></figure>' % (
            ph('2 / 1', t('Image band, 2:1, as wide as the window', 'Dải ảnh, 2:1, rộng bằng cửa sổ')),
            t('A caption, when a picture needs one.', 'Chú thích, khi ảnh cần.')),
        '<div class="wrap"><div class="gallery" role="region" tabindex="0" %s>' % label('Photographs', 'Ảnh') + '%s</div></div>' % ''.join(
            '<figure>%s</figure>' % ph('4 / 5', '%s %d' % (t('Gallery', 'Bộ ảnh'), i)) for i in (1, 2, 3)),
        '<div class="wrap"><div class="cards">%s</div></div>' % ''.join(
            '<article class="card">%s<div class="card-body"><h3>%s</h3><p>%s</p><a class="link-sc" href="%s">%s</a></div></article>'
            % (ph('3 / 2', example), name, desc, href, t('Go', 'Xem'))
            for name, desc, href in ((t('Menu', 'Thực đơn'), t('A card: a picture, a title, a line, a link.',
                                                               'Một thẻ: ảnh, tiêu đề, một dòng, một liên kết.'), '/menu/'),
                                     (t('About', 'Giới thiệu'), t('Three to a row on a wide screen.',
                                                                  'Ba thẻ một hàng trên màn hình rộng.'), '/about/'),
                                     (t('Visit', 'Ghé thăm'), t('One to a row on a phone.', 'Một thẻ một hàng trên điện thoại.'),
                                      '/visit-us/'))),
        '<figure class="quote wrap"><blockquote><p>%s</p></blockquote><figcaption>%s</figcaption></figure>' % (
            t('We’d rather cook a short menu well than a long one adequately.',
              'Chúng tôi thà nấu ít món cho thật ngon, còn hơn nhiều món mà tàm tạm.'), 'Sol'),
        '<div class="wrap"><div class="gated"><p class="gated-label">%s <code>key</code>: %s</p>%s</div></div>' % (
            t('Content needed', 'Cần nội dung'),
            t('how a section waiting for content looks in the full build', 'phần đang chờ nội dung trông thế nào ở bản đầy đủ'),
            ph('3 / 1', example)),
        '<div class="wrap"><section class="prose-section reveal" aria-labelledby="sg-fade"><header class="section-head">%s'
        '<h2 id="sg-fade">%s</h2></header><div class="prose"><p>%s</p></div></section></div>' % (
            sun(4), t('A slow fade', 'Hiện dần'),
            t('This section fades in as it comes into view, unless the device asks for less motion.',
              'Phần này hiện dần khi cuộn tới, trừ khi thiết bị yêu cầu giảm chuyển động.')),
        '</main>', ''])
    return page('/styleguide/', 'page-styleguide', ('Components — Sol', 'Thành phần — Sol'),
                ('The parts pages are built from (full build only).', 'Các thành phần của trang (chỉ bản đầy đủ).'),
                main, index=False, extra='<meta name="robots" content="noindex, nofollow">')


# ==========================================================================
# THE KITCHEN  /dough/  /dough/log/  /dough/login/
# Tools for the dough station, not pages for guests: behind the kitchen password
# (worker/index.js), with no tab, footer link or sitemap entry, noindex, and no
# analytics. Staff open sol.pizza/dough/ on a phone.
#   /dough/        the calculator: set the balls and their weight, and the weights
#                  for the mix follow, with the flour blend, a preferment (poolish or
#                  biga), the kitchen's temperature and humidity and, when wanted,
#                  the water temperature; then log the batch
#   /dough/log/    every batch logged, newest first, and a CSV of it
#   /dough/login/  the kitchen password
# This writes the pages, every line in both languages, and the house spec the
# calculator opens on. The arithmetic is in build/design/dough.js, the log page's
# script in dough-log.js, and the log itself in D1, behind the Worker.
# ==========================================================================
# The house spec: what the calculator opens on and what "Back to the house spec"
# goes back to. Baker's percentages: each ingredient as a percentage of all the
# flour's weight; the yeast is fresh yeast. The blend gives whole wheat and rye,
# and pizza flour is the rest. A shared link carries only what differs from these.
# CONFIRM with the Sous Chef, who owns the dough programme: a starting point for
# a cold-fermented dough for the wood oven, not Sol's spec yet.
DOUGH_SPEC = {
    'balls': 40, 'ball': 260, 'waste': 2,        # balls, grams each, % extra for the bowl and the bench
    'hydration': 65, 'salt': 2.8, 'yeast': 0.6, 'oil': 0, 'sugar': 0,
    'whole_wheat': 0, 'rye': 0,                  # % of the flour; pizza flour is the rest
    'preferment': 'none',                        # none, or a key of PREFERMENTS
    # Water temperature, °C: the dough you want after mixing, the flour, the
    # preferment, the mixer's friction, and the water before any ice. The kitchen's
    # temperature and humidity are measured each time, not part of the spec.
    't_dough': 24, 't_flour': 26, 't_pf': 18, 't_friction': 12, 't_water': 28,
}
# What a preferment starts at when it's picked: its share of all the flour (%),
# its hydration (%) and its fresh yeast (% of its own flour). It's made with pizza
# flour; whole wheat and rye go in at the final mix.
PREFERMENTS = {
    'poolish': {'pf_flour': 30, 'pf_hydration': 100, 'pf_yeast': 0.3},
    'biga':    {'pf_flour': 50, 'pf_hydration': 45, 'pf_yeast': 1},
}
assert DOUGH_SPEC['preferment'] in ['none'] + list(PREFERMENTS), \
    'DOUGH_SPEC: preferment is none or one of %s' % ', '.join(PREFERMENTS)
assert DOUGH_SPEC['whole_wheat'] + DOUGH_SPEC['rye'] <= 100, 'DOUGH_SPEC: whole wheat and rye come to over 100%'

DOUGH_UNITS = {'g': t('grams', 'gam'), '%': t('percent', 'phần trăm'), '°C': t('degrees Celsius', 'độ C')}
KITCHEN_EYEBROW = t('Kitchen', 'Bếp')
FRESH_YEAST = t('Fresh yeast', 'Men tươi')
PIZZA_FLOUR = t('Pizza flour', 'Bột pizza')
WHOLE_WHEAT = t('Whole wheat flour', 'Bột mì nguyên cám')
RYE = t('Rye flour', 'Bột lúa mạch đen')


def dough_default(name):
    """The value a box opens on: the house spec's; a preferment's boxes take the spec's
    preferment (with none, the first one, hidden until one is picked), as dough.js does;
    the kitchen's measurements and the log's boxes open empty."""
    if name in DOUGH_SPEC:
        return DOUGH_SPEC[name]
    pf = PREFERMENTS.get(DOUGH_SPEC['preferment']) or next(iter(PREFERMENTS.values()))
    return pf.get(name, '')


def dough_box(fid, inner, text, unit='', attrs=''):
    """A label in capitals over a white box, the unit at its right."""
    return ('<div class="dough-field"%s><label class="label" for="%s">%s%s</label><div class="dough-box">%s%s</div></div>'
            % (attrs, fid, text, '<span class="visually-hidden">, %s</span>' % DOUGH_UNITS[unit] if unit else '',
               inner, '<span class="dough-unit" aria-hidden="true">%s</span>' % unit if unit else ''))


def dough_field(name, text, unit, lo, hi, integer=False, hint=None, attrs='', optional=False):
    """One number. A text box with a number keypad rather than type="number", so 2,8 and
    2.8 both work whatever the phone's language; dough.js reads it and checks it against
    data-min, data-max and data-int. optional: may stay empty (the kitchen's measurements
    and the log's), until the log needs it. hint: the id of the line that explains it."""
    fid = 'd-' + name.replace('_', '-')
    value = dough_default(name)
    return dough_box(fid, '<input id="%s" name="%s" type="text" inputmode="%s" value="%s" autocomplete="off" '
                          'spellcheck="false" data-min="%g" data-max="%g"%s%s%s>'
                     % (fid, name, 'numeric' if integer else 'decimal', '' if value == '' else '%g' % value, lo, hi,
                        ' data-int' if integer else '', ' data-optional' if optional else '',
                        ' aria-describedby="%s"' % hint if hint else ''), text, unit, attrs)


def dough_choice(name, options):
    """Radio buttons drawn as one segmented box; the house spec's option is checked."""
    return '<div class="dough-seg">%s</div>' % ''.join(
        '<label><input type="radio" name="%s" value="%s"%s><span>%s</span></label>'
        % (name, value, ' checked' if DOUGH_SPEC[name] == value else '', text) for value, text in options)


def dough_nav(cur):
    """Calculator · Dough log · Sign out, under the page title."""
    links = [('calc', '/dough/', t('Calculator', 'Tính bột')), ('log', '/dough/log/', t('Dough log', 'Nhật ký bột'))]
    return ('<nav class="dough-nav" %s><ul>%s<li><form method="post" action="/api/dough/logout">'
            '<button type="submit">%s</button></form></li></ul></nav>'
            % (label('Kitchen', 'Bếp'),
               ''.join('<li><a href="%s"%s>%s</a></li>' % (href, ' aria-current="page"' if key == cur else '', name)
                       for key, href, name in links),
               t('Sign out', 'Đăng xuất')))


def kitchen_page(path, data_page, title, desc, main, extra=''):
    """A kitchen page: behind the password, out of search, no analytics, and the kitchen's
    own shell (kitchen_head(), kitchen_header(), kitchen_footer()): one bilingual page,
    never a /vi/ copy."""
    doc = kitchen_head(path, title, desc,
                       '<meta name="robots" content="noindex, nofollow">' + ('\n' + extra if extra else ''))
    doc += '<body class="page-kitchen page-%s" data-page="%s">\n%s\n' % (data_page, data_page, SUN_SPRITE)
    doc += nbsp('<a class="skip" href="#main">%s</a>\n' % t('Skip to content', 'Chuyển đến nội dung chính')
                + kitchen_header())
    doc += nbsp(main)
    doc += nbsp(kitchen_footer())
    doc += '</body>\n</html>\n'
    rec = dict(path=path, kitchen=True, doc=doc, hidden=hidden(path))
    PAGES.append(rec)
    return rec


def build_dough():
    def out(key):
        return '<span data-out="%s">—</span>' % key

    def row(key, name, cond=None):
        return ('<tr%s><th scope="row">%s</th><td>%s&nbsp;g</td></tr>'
                % (' data-if="%s" hidden' % cond if cond else '', name, out(key)))

    def pf_names(lower=False):
        return ''.join('<span data-if="pf-%s" hidden>%s</span>' % (k, k if lower else k.capitalize())
                       for k in PREFERMENTS)

    def warn(key, text):
        return '<p class="dough-warn" data-if="%s" hidden>%s</p>' % (key, text)

    def status(key, text, cls='dough-status'):
        return '<p class="%s" data-if="%s" hidden>%s</p>' % (cls, key, text)

    main = """<main id="main" class="wrap">
{title}
{nav}
<noscript><aside class="note-box"><p>{nojs}</p></aside></noscript>
<form class="dough" id="dough" autocomplete="off" novalidate>
<fieldset class="dough-set"><legend>{h_batch}</legend>
  <div class="dough-fields">{balls}{ball}{waste}</div>
  <p class="dough-hint" id="d-waste-hint">{waste_hint}</p>
</fieldset>
<section class="dough-out" aria-labelledby="dough-out-l">
  <p class="label" id="dough-out-l">{weigh}</p>
  <h2 class="dough-sum">{o_balls} × {o_ball}&nbsp;g</h2>
  <p class="dough-sub">{sub}</p>
  <table class="dough-table">
    <tbody data-if="pf" hidden><tr class="dough-group"><th colspan="2" scope="colgroup">{pf_head}</th></tr>{pf_rows}</tbody>
    <tbody><tr class="dough-group" data-if="pf" hidden><th colspan="2" scope="colgroup">{final}</th></tr>{rows}</tbody>
    <tfoot><tr><th scope="row">{total}</th><td>{o_total}&nbsp;g</td></tr></tfoot>
  </table>
  {w_invalid}{w_blend}{w_pf_pizza}{w_pf}
  <div class="dough-water" data-if="temp" hidden>
    <p class="label">{h_temp}</p>
    <p class="dough-water-main" data-if="ice" hidden>{ice}</p>
    <p class="dough-water-main" data-if="no-ice" hidden>{no_ice}</p>
    <p class="dough-water-note" data-if="water" hidden>{water_note}</p>
    {w_kitchen}{w_ice}{w_hot}{w_dry}
  </div>
  <div class="dough-actions"><button class="btn btn-red btn-sm" type="button" data-share><span data-if="not-copied">{share}</span><span data-if="copied" hidden>{copied}</span></button><button class="btn btn-outline btn-sm" type="button" data-reset>{reset}</button></div>
  <p class="dough-note">{note}</p>
  <a class="link-sc dough-to-log" href="#log">{to_log}</a>
</section>
<fieldset class="dough-set"><legend>{h_formula}</legend>
  <p class="dough-hint">{bakers}</p>
  <div class="dough-fields">{hydration}{salt}{yeast}{oil}{sugar}</div>
  <fieldset class="dough-blend"><legend class="label">{h_blend}</legend>
    <div class="dough-fields">{pizza}{whole_wheat}{rye}</div>
    <p class="dough-hint" id="d-blend-hint">{blend_hint}</p>
  </fieldset>
</fieldset>
<fieldset class="dough-set"><legend>{h_pf}</legend>
  {preferment}
  <div class="dough-fields" data-if="pf" hidden>{pf_flour}{pf_hydration}{pf_yeast}</div>
  <p class="dough-hint" id="d-pf-hint" data-if="pf" hidden>{pf_hint}</p>
</fieldset>
<fieldset class="dough-set"><legend>{h_kitchen}</legend>
  <div class="dough-fields">{kitchen_c}{humidity}</div>
  <p class="dough-hint" id="d-kitchen-hint">{kitchen_hint}</p>
</fieldset>
<details class="dough-set dough-temp"><summary>{h_temp}{caret}</summary>
  <p class="dough-hint">{temp_hint}</p>
  <div class="dough-fields">{t_dough}{t_flour}{t_pf}{t_friction}{t_water}</div>
  <p class="dough-hint" id="d-friction-hint">{friction_hint}</p>
  <p class="dough-hint" id="d-water-hint">{water_hint}</p>
</details>
<fieldset class="dough-set dough-log" id="log"><legend>{h_log}</legend>
  <p class="dough-hint">{log_hint}</p>
  <div class="dough-fields dough-fields-2">{day}{made_by}{dough_c}</div>
  <div class="dough-field dough-notes"><label class="label" for="d-notes">{l_notes}</label><textarea id="d-notes" name="notes" rows="3" maxlength="1000"></textarea></div>
  {w_log_kitchen}{w_log_who}{w_log_check}
  <div class="dough-actions"><button class="btn btn-red" type="button" data-log>{log_btn}</button></div>
  <div role="status">{s_saving}{s_saved}{s_failed}{s_signed_out}{s_off}</div>
</fieldset>
</form>
<script type="application/json" id="dough-spec">{spec}</script>
</main>
""".format(
        title=page_title(KITCHEN_EYEBROW, t('Dough calculator', 'Tính bột pizza'),
                         t('Set the number of balls and their weight, and the weights for the mix follow.',
                           'Nhập số viên bột và trọng lượng mỗi viên, lượng nguyên liệu cần trộn sẽ tự tính.')),
        nav=dough_nav('calc'),
        nojs=t('The calculator needs JavaScript. Turn it on in the browser’s settings.',
               'Công cụ này cần JavaScript. Hãy bật JavaScript trong cài đặt trình duyệt.'),
        h_batch=t('The batch', 'Mẻ bột'),
        balls=dough_field('balls', t('Dough balls', 'Số viên bột'), None, 1, 2000, integer=True),
        ball=dough_field('ball', t('Each ball', 'Mỗi viên'), 'g', 50, 2000),
        waste=dough_field('waste', t('Waste', 'Hao hụt'), '%', 0, 50, hint='d-waste-hint'),
        waste_hint=t('Waste: extra dough for what stays in the mixer bowl and on the bench.',
                     'Hao hụt: phần bột làm thêm cho lượng dính lại trong cối trộn và trên bàn.'),
        weigh=t('Weigh out', 'Cân nguyên liệu'),
        o_balls=out('balls'), o_ball=out('ball'),
        sub=t('%s kg of dough<span data-if="waste">, with %s%% for waste</span>' % (out('dough_kg'), out('waste')),
              '%s kg bột<span data-if="waste">, đã gồm %s%% hao hụt</span>' % (out('dough_kg'), out('waste'))),
        pf_head=pf_names() + t(' · mix first', ' · trộn trước'),
        pf_rows=row('pf_flour', PIZZA_FLOUR) + row('pf_water', t('Water', 'Nước')) + row('pf_yeast', FRESH_YEAST),
        final=t('Final mix', 'Trộn chính'),
        rows=''.join([row('pizza', PIZZA_FLOUR), row('ww', WHOLE_WHEAT, 'ww'), row('rye', RYE, 'rye'),
                      row('water', t('Water', 'Nước')),
                      row('pf', t('All the %s' % pf_names(True), 'Toàn bộ %s' % pf_names(True)), 'pf'),
                      row('salt', t('Salt', 'Muối')), row('yeast', FRESH_YEAST),
                      row('oil', t('Oil', 'Dầu'), 'oil'), row('sugar', t('Sugar', 'Đường'), 'sugar')]),
        total=t('Total', 'Tổng'), o_total=out('dough_g'),
        w_invalid=warn('warn-invalid', t('Check the marked boxes.', 'Kiểm tra lại các ô được đánh dấu.')),
        w_blend=warn('warn-blend', t('Whole wheat and rye come to more than all the flour.',
                                     'Bột nguyên cám và bột lúa mạch đen đang nhiều hơn tổng lượng bột mì.')),
        w_pf_pizza=warn('warn-pf-pizza', t('The preferment needs more pizza flour than the blend has. Lower its '
                                           'share of the flour, or the whole wheat and rye.',
                                           'Bột ủ cần nhiều bột pizza hơn lượng có trong hỗn hợp. Hãy giảm phần bột '
                                           'mì của bột ủ, hoặc giảm bột nguyên cám và lúa mạch đen.')),
        w_pf=warn('warn-pf', t('The preferment holds more water than the whole dough. Lower its hydration or '
                               'its share of the flour.',
                               'Bột ủ đang chứa nhiều nước hơn cả khối bột. Hãy giảm tỉ lệ nước hoặc phần bột '
                               'mì của bột ủ.')),
        h_temp=t('Water temperature', 'Nhiệt độ nước'),
        ice=t('%s&nbsp;g water + %s&nbsp;g ice' % (out('w_tap'), out('ice')),
              '%s&nbsp;g nước + %s&nbsp;g đá' % (out('w_tap'), out('ice'))),
        no_ice=t('%s&nbsp;g water at %s&nbsp;°C' % (out('w_final'), out('tw')),
                 '%s&nbsp;g nước ở %s&nbsp;°C' % (out('w_final'), out('tw'))),
        water_note=t('For dough at %s&nbsp;°C the water works out at %s&nbsp;°C; yours is %s&nbsp;°C.'
                     % (out('t_dough'), out('tw'), out('t_water')),
                     'Để bột đạt %s&nbsp;°C, nước cần ở %s&nbsp;°C; nước của bạn đang ở %s&nbsp;°C.'
                     % (out('t_dough'), out('tw'), out('t_water'))),
        w_kitchen=status('need-kitchen', t('Measure the kitchen’s temperature to work out the water.',
                                           'Hãy đo nhiệt độ bếp để tính nhiệt độ nước.'), 'dough-water-note'),
        w_ice=warn('warn-ice', t('Ice alone can’t cool it that far: chill the flour first, or aim a degree or '
                                 'two warmer.',
                                 'Chỉ dùng đá thì không đủ lạnh: hãy làm lạnh bột mì trước, hoặc chọn nhiệt độ '
                                 'bột cao hơn một, hai độ.')),
        w_hot=warn('warn-hot', t('Water above 40&nbsp;°C can harm the yeast: use it cooler and let the dough '
                                 'warm up after mixing.',
                                 'Nước trên 40&nbsp;°C có thể làm hỏng men: hãy dùng nước nguội hơn và để bột '
                                 'ấm lên sau khi trộn.')),
        w_dry=warn('warn-dry', t('All the water is in the preferment, so there’s none to set at the final mix.',
                                 'Toàn bộ nước đã nằm trong bột ủ, nên không có nước để điều chỉnh ở lần '
                                 'trộn chính.')),
        share=t('Share this batch', 'Chia sẻ mẻ bột này'),
        copied=t('Link copied', 'Đã sao chép liên kết'),
        reset=t('Back to the house spec', 'Về công thức chuẩn'),
        note=t('The page opens on the house spec. Share sends the batch as it is now, as a link.',
               'Trang luôn mở với công thức chuẩn của bếp. Nút Chia sẻ gửi mẻ bột hiện tại dưới dạng '
               'liên kết.'),
        to_log=t('Log this batch', 'Ghi nhật ký mẻ này'),
        h_formula=t('The formula', 'Công thức'),
        bakers=t('Baker’s percentages: each ingredient as a percentage of all the flour’s weight.',
                 'Tỉ lệ theo bột mì (baker’s percentage): mỗi nguyên liệu tính bằng phần trăm so với '
                 'tổng trọng lượng bột mì.'),
        hydration=dough_field('hydration', t('Hydration', 'Tỉ lệ nước'), '%', 40, 120),
        salt=dough_field('salt', t('Salt', 'Muối'), '%', 0, 10),
        yeast=dough_field('yeast', FRESH_YEAST, '%', 0, 10),
        oil=dough_field('oil', t('Oil', 'Dầu'), '%', 0, 30),
        sugar=dough_field('sugar', t('Sugar', 'Đường'), '%', 0, 30),
        h_blend=t('The flour', 'Bột mì'),
        pizza=dough_box('d-pizza', '<output id="d-pizza" for="d-whole-wheat d-rye" data-out="pizza_pct">%g</output>'
                        % (100 - DOUGH_SPEC['whole_wheat'] - DOUGH_SPEC['rye']), PIZZA_FLOUR, '%',
                        ' data-readout'),
        whole_wheat=dough_field('whole_wheat', t('Whole wheat', 'Nguyên cám'), '%', 0, 100, hint='d-blend-hint'),
        rye=dough_field('rye', t('Rye', 'Lúa mạch đen'), '%', 0, 100, hint='d-blend-hint'),
        blend_hint=t('Pizza flour is the rest. A preferment is made with pizza flour; whole wheat and rye go in '
                     'at the final mix.',
                     'Bột pizza là phần còn lại. Bột ủ làm bằng bột pizza; bột nguyên cám và lúa mạch đen cho vào '
                     'ở lần trộn chính.'),
        h_pf=t('Preferment', 'Bột ủ trước'),
        preferment=dough_choice('preferment', [('none', t('None', 'Không'))]
                                + [(k, k.capitalize()) for k in PREFERMENTS]),
        pf_flour=dough_field('pf_flour', t('Share of the flour', 'Phần bột mì'), '%', 1, 100, hint='d-pf-hint'),
        pf_hydration=dough_field('pf_hydration', t('Its hydration', 'Tỉ lệ nước'), '%', 40, 150),
        pf_yeast=dough_field('pf_yeast', t('Its yeast', 'Men tươi'), '%', 0, 10, hint='d-pf-hint'),
        pf_hint=t('Share of the flour: how much of all the flour goes into the preferment. Its fresh yeast is a '
                  'percentage of its own flour. The salt and the rest go in at the final mix.',
                  'Phần bột mì: bao nhiêu phần trăm tổng lượng bột mì dùng cho bột ủ. Men tươi của bột ủ tính '
                  'theo phần trăm bột mì của chính nó. Muối và phần còn lại cho vào ở lần trộn chính.'),
        h_kitchen=t('The kitchen', 'Bếp'),
        kitchen_c=dough_field('kitchen_c', t('Temperature', 'Nhiệt độ'), '°C', -10, 60, optional=True,
                              hint='d-kitchen-hint'),
        humidity=dough_field('humidity', t('Air humidity', 'Độ ẩm không khí'), '%', 0, 100, optional=True,
                             hint='d-kitchen-hint'),
        kitchen_hint=t('Measure them when you mix. Both go in the log, and the temperature works out the water.',
                       'Đo khi bắt đầu trộn. Cả hai được ghi vào nhật ký, và nhiệt độ bếp dùng để tính nhiệt '
                       'độ nước.'),
        temp_hint=t('Measure the flour and your water too, and this works out how warm the water should be, '
                    'and how much ice, for the dough you want.',
                    'Đo thêm nhiệt độ bột mì và nước, công cụ sẽ tính nước cần ấm hay lạnh bao nhiêu, và cần '
                    'bao nhiêu đá, để bột đạt nhiệt độ mong muốn.'),
        t_dough=dough_field('t_dough', t('Dough to aim for', 'Bột cần đạt'), '°C', 10, 40),
        t_flour=dough_field('t_flour', t('Flour', 'Bột mì'), '°C', -20, 50),
        t_pf=dough_field('t_pf', t('Preferment', 'Bột ủ'), '°C', -5, 50, attrs=' data-if="pf" hidden'),
        t_friction=dough_field('t_friction', t('Mixer friction', 'Nhiệt từ máy trộn'), '°C', 0, 40,
                               hint='d-friction-hint'),
        t_water=dough_field('t_water', t('Your water', 'Nước của bạn'), '°C', 0, 60, hint='d-water-hint'),
        friction_hint=t('Mixer friction: how much the mixer warms the dough. To measure it, after a mix: 3 × '
                        'the dough’s temperature, minus the flour, the kitchen and the water (with a preferment, '
                        '4 × and minus the preferment too).',
                        'Nhiệt từ máy trộn: máy trộn làm bột ấm thêm bao nhiêu độ. Cách đo, sau một mẻ trộn: '
                        '3 × nhiệt độ bột, trừ nhiệt độ bột mì, bếp và nước (nếu có bột ủ: 4 × và trừ thêm '
                        'nhiệt độ bột ủ).'),
        water_hint=t('Your water: as it comes, from the tap or the fridge, before any ice.',
                     'Nước của bạn: nhiệt độ nước đang có, từ vòi hoặc tủ lạnh, trước khi cho đá.'),
        caret=CARET,
        h_log=t('Log this batch', 'Ghi nhật ký mẻ này'),
        log_hint=t('Once it’s mixed. The batch, the flour, the kitchen and the weights above go in with it.',
                   'Sau khi trộn xong. Mẻ bột, bột mì, thông số bếp và lượng nguyên liệu ở trên sẽ được ghi '
                   'cùng.'),
        day=dough_box('d-day', '<input id="d-day" name="day" type="date">', t('Day', 'Ngày')),
        made_by=dough_box('d-made-by', '<input id="d-made-by" name="made_by" type="text" maxlength="60" '
                          'autocomplete="off" spellcheck="false">', t('Mixed by', 'Người trộn')),
        dough_c=dough_field('dough_c', t('Dough after mixing', 'Bột sau khi trộn'), '°C', -10, 60, optional=True),
        l_notes=t('Notes', 'Ghi chú'),
        w_log_kitchen=warn('log-kitchen', t('Measure the kitchen first: its temperature and air humidity go in '
                                            'the log.',
                                            'Hãy đo bếp trước: nhiệt độ và độ ẩm không khí sẽ được ghi vào '
                                            'nhật ký.')),
        w_log_who=warn('log-who', t('Add the day and who mixed it.', 'Hãy ghi ngày và người trộn.')),
        w_log_check=warn('log-check', t('Fix what’s marked above first.',
                                        'Hãy sửa các mục được đánh dấu ở trên trước.')),
        log_btn=t('Log this batch', 'Ghi vào nhật ký'),
        s_saving=status('log-saving', t('Saving…', 'Đang lưu…')),
        s_saved=status('log-saved', t('Logged. <a href="/dough/log/">See the dough log</a>',
                                      'Đã ghi. <a href="/dough/log/">Xem nhật ký bột</a>')),
        s_failed=status('log-failed', t('Couldn’t save it. Check the connection and try again.',
                                        'Chưa lưu được. Hãy kiểm tra kết nối và thử lại.'), 'dough-warn'),
        s_signed_out=status('log-signed-out',
                            t('You’ve been signed out. <a href="/dough/login/" target="_blank">Sign in</a> in a '
                              'new tab, then log it again here.',
                              'Bạn đã bị đăng xuất. Hãy <a href="/dough/login/" target="_blank">đăng nhập</a> ở '
                              'một thẻ mới, rồi ghi lại ở đây.'), 'dough-warn'),
        s_off=status('log-off', t('The log isn’t set up on this copy of the site.',
                                  'Nhật ký chưa được thiết lập trên bản này của trang.'), 'dough-warn'),
        spec=json.dumps({'spec': DOUGH_SPEC, 'preferments': PREFERMENTS},
                        ensure_ascii=False).replace('</', '<\\/'),
    )
    return kitchen_page('/dough/', 'dough', ('Dough calculator — Sol', 'Tính bột pizza — Sol'),
                        ('The dough calculator for Sol’s kitchen.', 'Công cụ tính bột pizza cho bếp của Sol.'),
                        main, extra='<script src="/assets/dough.js" defer></script>')


def build_dough_log():
    """/dough/log/: dough-log.js fetches the log and fills a copy of the entry template
    for each batch, under a heading for each day."""
    def fact(name, value, cond=None):
        return '<div%s><dt>%s</dt><dd>%s</dd></div>' % (' data-if="%s"' % cond if cond else '', name, value)

    def slot(key):
        return '<span data-slot="%s"></span>' % key

    def part(cond, en, vi):
        """A piece of a line that shows only when cond holds, in both languages."""
        return '<span data-if="%s"> · %s</span>' % (cond, t(en, vi))

    entry = ('<template id="log-entry"><article class="log-entry">'
             '<header class="log-head"><p class="log-batch">{balls} × {ball}&nbsp;g · {kg}&nbsp;kg</p>'
             '<p class="log-meta">{by}</p></header><dl class="log-facts">{facts}</dl>'
             '<button class="log-delete" type="button" data-delete data-confirm-en="{c_en}" data-confirm-vi="{c_vi}">'
             '{delete}</button></article></template>').format(
        balls=slot('balls'), ball=slot('ball'), kg=slot('dough_kg'),
        by=t('%s, logged at %s' % (slot('made_by'), slot('time')), '%s, ghi lúc %s' % (slot('made_by'), slot('time'))),
        facts=''.join([
            fact(t('Flour', 'Bột mì'),
                 t('%s%% pizza flour' % slot('pizza_pct'), '%s%% bột pizza' % slot('pizza_pct'))
                 + part('ww', '%s%% whole wheat' % slot('ww_pct'), '%s%% nguyên cám' % slot('ww_pct'))
                 + part('rye', '%s%% rye' % slot('rye_pct'), '%s%% lúa mạch đen' % slot('rye_pct'))),
            fact(t('Formula', 'Công thức'),
                 t('Hydration %s%% · salt %s%% · fresh yeast %s%%' % (slot('hydration'), slot('salt'), slot('yeast')),
                   'Nước %s%% · muối %s%% · men tươi %s%%' % (slot('hydration'), slot('salt'), slot('yeast')))
                 + part('oil', 'oil %s%%' % slot('oil'), 'dầu %s%%' % slot('oil'))
                 + part('sugar', 'sugar %s%%' % slot('sugar'), 'đường %s%%' % slot('sugar'))),
            fact(t('Preferment', 'Bột ủ trước'),
                 slot('pf_name') + t(': %s%% of the flour, %s%% hydration, %s%% fresh yeast'
                                     % (slot('pf_flour'), slot('pf_hydration'), slot('pf_yeast')),
                                     ': %s%% bột mì, %s%% nước, %s%% men tươi'
                                     % (slot('pf_flour'), slot('pf_hydration'), slot('pf_yeast'))), 'pf'),
            fact(t('Kitchen', 'Bếp'),
                 t('%s&nbsp;°C · air humidity %s%%' % (slot('kitchen_c'), slot('humidity')),
                   '%s&nbsp;°C · độ ẩm không khí %s%%' % (slot('kitchen_c'), slot('humidity')))),
            fact(t('Water', 'Nước'),
                 t('%s&nbsp;°C<span data-if="ice">, with %s&nbsp;g ice</span>' % (slot('water_c'), slot('ice')),
                   '%s&nbsp;°C<span data-if="ice">, có %s&nbsp;g đá</span>' % (slot('water_c'), slot('ice'))),
                 'water'),
            fact(t('Dough after mixing', 'Bột sau khi trộn'),
                 t('%s&nbsp;°C<span data-if="target"> (aiming for %s&nbsp;°C)</span>' % (slot('dough_c'), slot('t_dough')),
                   '%s&nbsp;°C<span data-if="target"> (mục tiêu %s&nbsp;°C)</span>' % (slot('dough_c'), slot('t_dough'))),
                 'dough_c'),
            fact(t('Weighed out', 'Đã cân'),
                 t('Pizza flour %s&nbsp;g' % slot('pizza_g'), 'Bột pizza %s&nbsp;g' % slot('pizza_g'))
                 + part('ww', 'whole wheat %s&nbsp;g' % slot('ww_g'), 'nguyên cám %s&nbsp;g' % slot('ww_g'))
                 + part('rye', 'rye %s&nbsp;g' % slot('rye_g'), 'lúa mạch đen %s&nbsp;g' % slot('rye_g'))
                 + ' · ' + t('water %s&nbsp;g · salt %s&nbsp;g · fresh yeast %s&nbsp;g'
                             % (slot('water_g'), slot('salt_g'), slot('yeast_g')),
                             'nước %s&nbsp;g · muối %s&nbsp;g · men tươi %s&nbsp;g'
                             % (slot('water_g'), slot('salt_g'), slot('yeast_g')))
                 + part('oil', 'oil %s&nbsp;g' % slot('oil_g'), 'dầu %s&nbsp;g' % slot('oil_g'))
                 + part('sugar', 'sugar %s&nbsp;g' % slot('sugar_g'), 'đường %s&nbsp;g' % slot('sugar_g'))),
            fact(t('Notes', 'Ghi chú'), '<span class="log-notes" data-slot="notes"></span>', 'notes'),
        ]),
        c_en='Delete this batch from the log? This can’t be undone.',
        c_vi='Xoá mẻ này khỏi nhật ký? Không thể hoàn tác.',
        delete=t('Delete', 'Xoá'))

    def state(key, text, cls='dough-status'):
        return '<p class="%s" data-state="%s" hidden>%s</p>' % (cls, key, text)

    main = '\n'.join([
        '<main id="main" class="wrap">',
        page_title(KITCHEN_EYEBROW, t('Dough log', 'Nhật ký bột'),
                   t('Every batch logged from the calculator, newest first.',
                     'Mọi mẻ bột đã ghi từ công cụ tính bột, mới nhất ở trên.')),
        dough_nav('log'),
        '<noscript><aside class="note-box"><p>%s</p></aside></noscript>'
        % t('The log needs JavaScript. Turn it on in the browser’s settings.',
            'Nhật ký cần JavaScript. Hãy bật JavaScript trong cài đặt trình duyệt.'),
        '<p class="log-tools"><a class="link-sc" href="/api/dough/log.csv">%s</a></p>'
        % t('Download it as a spreadsheet (CSV)', 'Tải về dạng bảng tính (CSV)'),
        '<div class="log-states" role="status">%s</div>' % ''.join([
            state('loading', t('Loading…', 'Đang tải…')),
            state('empty', t('Nothing logged yet. Log a batch from the <a href="/dough/">calculator</a>.',
                             'Chưa có gì trong nhật ký. Hãy ghi một mẻ từ <a href="/dough/">công cụ tính bột</a>.')),
            state('failed', t('Couldn’t load the log. Check the connection and reload the page.',
                              'Không tải được nhật ký. Hãy kiểm tra kết nối và tải lại trang.'), 'dough-warn'),
            state('delete-failed', t('Couldn’t delete it. Check the connection and try again.',
                                     'Chưa xoá được. Hãy kiểm tra kết nối và thử lại.'), 'dough-warn'),
            state('signed-out', t('You’ve been signed out. <a href="/dough/login/?next=/dough/log/">Sign in again</a>.',
                                  'Bạn đã bị đăng xuất. <a href="/dough/login/?next=/dough/log/">Đăng nhập lại</a>.'),
                  'dough-warn'),
            state('off', t('The log isn’t set up on this copy of the site.',
                           'Nhật ký chưa được thiết lập trên bản này của trang.'), 'dough-warn'),
        ]),
        '<div class="log-list" id="log-list"></div>',
        '<div class="actions"><button class="btn btn-outline" type="button" data-more hidden>%s</button></div>'
        % t('Show older batches', 'Xem các mẻ cũ hơn'),
        entry,
        '</main>', ''])
    return kitchen_page('/dough/log/', 'dough-log', ('Dough log — Sol', 'Nhật ký bột — Sol'),
                        ('Every batch of dough logged in Sol’s kitchen.', 'Nhật ký các mẻ bột của bếp Sol.'),
                        main, extra='<script src="/assets/dough-log.js" defer></script>')


def build_dough_login():
    """/dough/login/: the Worker shows the line for a wrong password, too many tries or no
    password set (data-if, unhidden by the Worker), and fills in where to go next."""
    def warn(key, text):
        return '<p class="dough-warn" data-if="%s" hidden>%s</p>' % (key, text)

    main = ('<main id="main" class="wrap">\n%s\n'
            '<form class="dough-login" method="post" action="/api/dough/login">'
            '<input type="hidden" name="next" value="/dough/">%s%s%s%s'
            '<div class="actions"><button class="btn btn-red" type="submit">%s</button></div>'
            '<p class="dough-hint">%s</p></form>\n</main>\n') % (
        page_title(KITCHEN_EYEBROW, t('Sign in', 'Đăng nhập'),
                   t('The dough calculator and the dough log are for Sol’s kitchen. Ask the Sous Chef for the '
                     'password.',
                     'Công cụ tính bột và nhật ký bột dành cho bếp của Sol. Hãy hỏi Bếp phó để biết mật khẩu.')),
        dough_box('d-password', '<input id="d-password" name="password" type="password" '
                                'autocomplete="current-password" required>', t('Kitchen password', 'Mật khẩu bếp')),
        warn('wrong', t('That isn’t the password. Try again.', 'Mật khẩu chưa đúng. Hãy thử lại.')),
        warn('wait', t('Too many tries. Wait 15 minutes, then try again.',
                       'Bạn đã thử quá nhiều lần. Hãy đợi 15 phút rồi thử lại.')),
        warn('off', t('Signing in isn’t set up on this copy of the site.',
                      'Chức năng đăng nhập chưa được thiết lập trên bản này của trang.')),
        t('Sign in', 'Đăng nhập'),
        t('You stay signed in on this phone for 30 days.', 'Bạn sẽ được giữ đăng nhập trên điện thoại này trong 30 ngày.'))
    return kitchen_page('/dough/login/', 'dough-login', ('Sign in — Sol kitchen', 'Đăng nhập — Bếp Sol'),
                        ('Sign in to Sol’s kitchen tools.', 'Đăng nhập vào công cụ của bếp Sol.'), main)


# ==========================================================================
# 404 and support files
# ==========================================================================
def build_404():
    # Menu and Booking; while those pages aren't public, Home and See open roles. Then
    # the main pages that are public.
    options = [('menu', '/menu/', t('Menu', 'Thực đơn')), ('booking', '/booking/', t('Booking', 'Đặt bàn')),
               (None, '/', t('Home', 'Trang chủ')), (None, '/jobs/', SEE_ROLES)]
    as_buttons = [href for key, href, _ in options if key is None or live(key)][:2]
    paths = [(href, name) for key, href, name in NAV_TABS + [(None, '/', t('Home', 'Trang chủ'))]
             if (key is None or live(key)) and href not in as_buttons]
    main = ('<main id="main" class="wrap">\n<header class="page-title"><h1>%s</h1><p class="page-lead">%s</p></header>\n'
            '<div class="actions">%s</div>\n<ul class="paths-404">%s</ul>\n'
            '</main>\n' % (t('We can’t find that page.', 'Chúng tôi không tìm thấy trang này.'),
                           t('It may have moved. Try one of these:', 'Có thể trang đã được chuyển. Bạn hãy thử một '
                                                                       'trong những trang sau:'),
                           buttons(options),
                           ''.join('<li><a class="link-sc" href="%s">%s</a></li>' % p for p in paths)))
    # Workers serve the nearest 404.html: /vi/404.html for a missing /vi/… address, in
    # Vietnamese, and /404.html for the rest. EN · VI lead to the two home pages.
    return page('/404.html', 'page-404', ('Page not found — Sol', 'Không tìm thấy trang — Sol'),
                ('Page not found.', 'Không tìm thấy trang.'), main, og='home', index=False,
                extra='<meta name="robots" content="noindex">', body_attrs=' data-page="404"',
                switch=('/', '/vi/'))


SITEMAP_PAGES = ['/', '/about/', '/menu/', '/menu/wine/', '/menu/bar/', '/events/', '/private-dining/', '/visit-us/',
                 '/booking/', '/gift-cards/', '/press/', '/accessibility/', '/jobs/'] + \
    [e['path'] for e in EVENTS]


def build_support():
    pages = SITEMAP_PAGES + [role_path(r) for r in ROLES if r['status'] == 'open'] + \
        [open_role_path(r) for r in OPEN_ROLES]
    pages = [p for p in pages if not hidden(p)]
    urls = []
    for p in pages:
        pri = '1.0' if p == '/' else ('0.9' if p.startswith(('/about/', '/menu/', '/private-dining/', '/visit-us/',
                                                             '/booking/')) else '0.6')
        # Each page in both languages, each listing both and English as the default
        alts = ''.join('    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>\n' % (code, SITE, lang_path(p, code))
                       for code in LANGS) + \
            '    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>\n' % (SITE, p)
        urls += ['  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority>\n%s  </url>'
                 % (SITE, lang_path(p, lang), TODAY, pri, alts) for lang in LANGS]
    write(os.path.join(DIST, 'sitemap.xml'),
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
          '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(urls) + '\n</urlset>\n')
    # The full build is the full-site preview: it stays out of search. The public build never does.
    # (The privacy notices carry noindex; a Disallow would stop search engines reading it.)
    write(os.path.join(DIST, 'robots.txt'),
          'User-agent: *\n%s\nSitemap: %s/sitemap.xml\n'
          % ('Disallow: /\n' if FULL else 'Allow: /\n', SITE))
    redirects()


# The addresses the public build sends to the home page: the hidden pages' own and
# the old ones from src/_redirects that led to them (redirects(), check_links()).
HIDDEN_REDIRECTS = set()


def redirect_rules(text):
    """(source, destination, code) for each rule in a _redirects file."""
    rules = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and not parts[0].startswith('#'):
            rules.append((parts[0], parts[1], parts[2] if len(parts) > 2 else '302'))
    return rules


def redirects():
    """dist/_redirects; Cloudflare applies it (the Worker is assets-only). While every
    page is public (the full build, or HIDDEN empty) it is src/_redirects as it is.
    Otherwise the addresses of the pages that aren't public yet and every old address in
    src/_redirects that leads to one, each with and without the slash, go to the home
    page with a 302, not a 301: browsers cache a 301, and these pages come back. The
    rest of src/_redirects stays as it is. Static rules first, splats last."""
    src, out = os.path.join(SRC, '_redirects'), os.path.join(DIST, '_redirects')
    if not HIDE:
        shutil.copy2(src, out)
        return

    def dynamic(path):
        return '*' in path or ':' in path

    def both(path):
        if path.endswith('.html') or dynamic(path):
            return [path]
        return [path, path.rstrip('/')] if path.endswith('/') else [path, path + '/']

    # each hidden page, with and without the slash, and as .html where no splat below
    # catches it (/about.html; /menu/wine.html falls under /menu/*)
    pages = [q for p in SITEMAP_PAGES if hidden_section(p)
             for q in both(p) + [p.rstrip('/') + '.html']
             if not (q.endswith('.html') and any(q.startswith(h) for h in HIDDEN_PATHS))]
    old, kept = [], []
    for source, dest, code in redirect_rules(read(src)):
        if hidden_section(dest):
            old += [q for q in both(source) if q not in pages + old]
        else:
            kept.append((source, dest, code))
    # and the same in Vietnamese, to the Vietnamese home page
    vi_pages = ['/vi' + p for p in pages]
    HIDDEN_REDIRECTS.update(pages + old + vi_pages)

    def rules(heading, rows):
        rows = list(rows)
        return ['', '# ' + heading] + ['%-22s %-14s %s' % r for r in rows] if rows else []

    lines = [
        '# sol.pizza redirects for the PUBLIC build, written by build/gen.py from',
        '# src/_redirects and HIDDEN: edit those, not this file. The pages not public',
        '# yet and the old addresses that led to them go to the home page with a 302,',
        '# not a 301: browsers cache a 301, and these pages come back.',
        '# Not public yet: %s.' % ', '.join(HIDDEN),
    ]
    lines += rules('Not public yet', [(p, '/', 302) for p in pages if not dynamic(p)]
                   + [(p, '/vi/', 302) for p in vi_pages if not dynamic(p)])
    lines += rules('Old addresses (src/_redirects) that led to them',
                   ((p, '/', 302) for p in old if not dynamic(p)))
    lines += rules('The rest of src/_redirects', (r for r in kept if not dynamic(r[0])))
    lines += rules('Splats last: anything else under a page not public yet, then src/_redirects',
                   [('%s*' % p, '/', 302) for p in HIDDEN_PATHS] + [('/vi%s*' % p, '/vi/', 302) for p in HIDDEN_PATHS]
                   + [(p, '/', 302) for p in pages + old if dynamic(p)]
                   + [r for r in kept if dynamic(r[0])])
    write(out, '\n'.join(lines) + '\n')


def leave_out_unused():
    """Public build: the share cards and illustrations no public page uses (those of the
    pages not public yet) aren't in dist/ either."""
    used = '\n'.join(read(os.path.join(root, f)) for root, _, files in os.walk(DIST)
                     for f in files if f.endswith(('.html', '.css')))
    gone = []
    for folder in (DIST, os.path.join(DIST, 'jobs'), os.path.join(DIST, 'assets')):
        for f in sorted(os.listdir(folder)):
            rel = os.path.relpath(os.path.join(folder, f), DIST).replace(os.sep, '/')
            card = f.startswith('og-') and f.endswith('.png')
            art = folder.endswith('assets') and f.endswith('.svg')
            if (card or art) and '/' + rel not in used:
                os.remove(os.path.join(folder, f))
                gone.append(rel)
    if gone:
        print('left out, no public page uses them:', ', '.join(gone))


def copy_existing():
    """Static files that aren't generated: favicon, pixel.js, share cards, design, scripts, SVGs, fonts."""
    for f in ('favicon.svg', 'pixel.js'):
        shutil.copy2(os.path.join(SRC, f), os.path.join(DIST, f))
    os.makedirs(os.path.join(DIST, 'jobs'), exist_ok=True)
    for f in os.listdir(os.path.join(SRC, 'jobs')):
        if f.startswith('og-') and f.endswith('.png'):
            shutil.copy2(os.path.join(SRC, 'jobs', f), os.path.join(DIST, 'jobs', f))
    for f in os.listdir(os.path.join(HERE, 'og', 'png')):          # share cards
        shutil.copy2(os.path.join(HERE, 'og', 'png', f), os.path.join(DIST, f))
    assets = os.path.join(DIST, 'assets')
    os.makedirs(assets, exist_ok=True)
    for f in ('tokens.css', 'printed-menu.css', 'site.css', 'dough.js', 'dough-log.js'):
        shutil.copy2(os.path.join(DESIGN, f), os.path.join(assets, f))
    # the guest pages' script, with the analytics IDs from the top of this file and the
    # consent version the head script checks too
    js = (read(os.path.join(DESIGN, 'site.js')).replace('__GA_ID__', GA_ID).replace('__FB_PIXEL__', FB_PIX)
          .replace('__CONSENT_VERSION__', str(CONSENT_VERSION)))
    assert not re.search(r'__[A-Z_]+__', js), 'site.js: a __PLACEHOLDER__ gen.py doesn\'t fill in'
    write(os.path.join(assets, 'site.js'), js)
    for f in ('kitchen.css', 'kitchen.js'):                         # the kitchen's frozen shell
        shutil.copy2(os.path.join(DESIGN, 'kitchen', f), os.path.join(assets, f))
    for f in os.listdir(ASSETS):
        if f.endswith('.svg') and f != 'suns-sprite.svg':             # the sprite is inlined
            shutil.copy2(os.path.join(ASSETS, f), os.path.join(assets, f))
    shutil.copy2(os.path.join(HERE, 'fonts.css'), os.path.join(assets, 'fonts.css'))
    shutil.copytree(os.path.join(HERE, 'fonts'), os.path.join(assets, 'fonts'), dirs_exist_ok=True)
    shutil.copy2(BN_ARORA_SRC, os.path.join(DIST, BN_ARORA_URL.lstrip('/')))


# ==========================================================================
# OPTIMISE
# CSS, JS and SVGs are minified where it helps and given content-hashed names
# so Cloudflare caches them for a year; the free fonts' @font-face rules are
# inlined into every page. HTML stays readable and is served with
# must-revalidate, so a redeploy shows up straight away. OG images are
# palette-quantised when Pillow is installed.
# ==========================================================================
def _hash(b):
    return hashlib.sha1(b).hexdigest()[:8]


def _node(args, data):
    return subprocess.run(['node'] + args, input=data, capture_output=True, check=True).stdout


def optimise():
    assets = os.path.join(DIST, 'assets')
    node = os.path.join(ROOT, 'node_modules')
    csso = ['-e', 'const c=require(process.argv[1]);let s="";process.stdin.on("data",d=>s+=d)'
                  '.on("end",()=>process.stdout.write(c.minify(s,{comments:false}).css))',
            os.path.join(node, 'csso')]
    terser = [os.path.join(node, 'terser', 'bin', 'terser'), '--compress', '--mangle', '--comments', 'false']
    rename = {}

    fonts_css = _node(csso, open(os.path.join(assets, 'fonts.css'), 'rb').read()).decode('utf-8')
    os.remove(os.path.join(assets, 'fonts.css'))

    for f in sorted(os.listdir(assets)):
        path = os.path.join(assets, f)
        if not os.path.isfile(path):
            continue
        data = open(path, 'rb').read()
        if f.endswith('.css'):
            data = _node(csso, data)
        elif f.endswith('.js'):
            data = _node(terser, data)
        base, ext = os.path.splitext(f)
        new = '%s.%s%s' % (base, _hash(data), ext)
        open(os.path.join(assets, new), 'wb').write(data)
        os.remove(path)
        rename['/assets/' + f] = '/assets/' + new

    pixel = os.path.join(DIST, 'pixel.js')
    with open(pixel, 'rb') as f:
        data = _node(terser, f.read())
    with open(pixel, 'wb') as f:
        f.write(data)

    for root, _, files in os.walk(DIST):
        for f in files:
            if not f.endswith('.html'):
                continue
            fp = os.path.join(root, f)
            h = read(fp)
            h = h.replace('<link rel="stylesheet" href="/assets/fonts.css">', '<style>%s</style>' % fonts_css)
            for a, b in rename.items():
                h = h.replace('"%s"' % a, '"%s"' % b)
            write(fp, h)

    try:
        from PIL import Image
        for root, _, files in os.walk(DIST):
            for f in files:
                if f.startswith('og-') and f.endswith('.png'):
                    fp = os.path.join(root, f)
                    im = Image.open(fp).convert('RGB').quantize(colors=96, method=Image.Quantize.MEDIANCUT)
                    im.save(fp, optimize=True)
    except ImportError:
        pass

    write(os.path.join(DIST, '_headers'), """# Cloudflare static-asset headers.
# HTML: always revalidate, so a redeploy shows up immediately.
# /assets: content-hashed filenames (fonts: versioned by npm; BN Arora: see
# build/README.md before replacing it), cached for a year.
# Link: early hints: the fonts above the fold (English pages: BN Arora and EB
# Garamond; Vietnamese pages, /vi/: Philosopher and EB Garamond with their Vietnamese
# letters), and the Adobe kit's hosts (its CSS on use.typekit.net @imports Adobe's
# counter from p.typekit.net).
%(robots)s/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(%(payment)s)
  Cache-Control: public, max-age=0, must-revalidate
  Link: %(link_en)s, %(kit)s%(noindex)s

/vi/*
  ! Link
  Link: %(link_vi)s, %(kit)s

/assets/*
  ! Cache-Control
  ! Link
  Cache-Control: public, max-age=31536000, immutable

/favicon.svg
  ! Cache-Control
  ! Link
  Cache-Control: public, max-age=604800

/*.png
  ! Cache-Control
  ! Link
  Cache-Control: public, max-age=86400
""" % dict(payment=' '.join(['self'] + sorted({'"{0.scheme}://{0.netloc}"'.format(urlsplit(u))
                                                 for u in (RESDIARY_URL, RESDIARY_URL_VI) if u}))
                   if RESDIARY_URL and RESDIARY_PAYMENTS else '',
           link_en=', '.join('<%s>; rel=preload; as=font; type=font/woff2; crossorigin' % f for f in FONT_PRELOADS['en']),
           link_vi=', '.join('<%s>; rel=preload; as=font; type=font/woff2; crossorigin' % f for f in FONT_PRELOADS['vi']),
           kit='<https://use.typekit.net>; rel=preconnect; crossorigin, <https://use.typekit.net>; rel=preconnect, '
               '<https://p.typekit.net>; rel=preconnect',
           # The full build is the full-site preview: it stays out of search. The public build never does.
           robots='# X-Robots-Tag: this is the full build (the full-site preview), kept out of search.\n'
                  if FULL else '',
           noindex='\n  X-Robots-Tag: noindex' if FULL else ''))


# ==========================================================================
# LINK CHECK   (the end of every public build)
# Every address in dist/ must be a file there or a redirect, and none may lead
# to a page that isn't public yet: href and src (canonical and alternate links
# included), og:url and og:image, the JSON-LD, CSS url()s, the sitemap,
# robots.txt, the font preloads in _headers and the redirects' destinations.
# ==========================================================================
class _Links(HTMLParser):
    """The addresses in one page: (where, address)."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found, self._ld, self._style = [], None, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ('href', 'src'):
            if a.get(k):
                self.found.append(('<%s %s>' % (tag, k), a[k]))
        if tag == 'meta' and a.get('property') in ('og:url', 'og:image') and a.get('content'):
            self.found.append((a['property'], a['content']))
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self._ld = []
        if tag == 'style':
            self._style = []

    def handle_data(self, data):
        for buf in (self._ld, self._style):
            if buf is not None:
                buf.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self._ld is not None:
            self.found += [('JSON-LD', u) for u in _json_urls(json.loads(''.join(self._ld)))]
            self._ld = None
        if tag == 'style' and self._style is not None:
            self.found += [('<style> url()', u) for u in _css_urls(''.join(self._style))]
            self._style = None


def _json_urls(v):
    if isinstance(v, dict):
        v = list(v.values())
    if isinstance(v, list):
        return [u for x in v for u in _json_urls(x)]
    return [v] if isinstance(v, str) and (v == SITE or v.startswith(SITE + '/')) else []


def _css_urls(css):
    return [u for u in re.findall(r'url\(\s*[\'"]?([^\'")]+)', css) if not u.startswith('data:')]


def _site_path(url, base):
    """The path on sol.pizza an address leads to, or None (another site, mailto:, #…)."""
    if url.startswith(('#', 'mailto:', 'tel:', 'data:', 'javascript:')):
        return None
    parts = urlsplit(urljoin(SITE + base, url))
    if parts.netloc != 'sol.pizza' or parts.path.startswith('/cdn-cgi/'):
        return None                     # another site, or Cloudflare's own (the photos' sizes)
    return unquote(parts.path) or '/'


# Addresses the Worker's own code answers (worker/index.js), not files in dist/: the
# kitchen's API (the dough log and its CSV, signing in and out).
WORKER_PATHS = ('/api/',)


def _served(path, rules):
    """True if the sol-pizza Worker answers this path with a redirect from dist/_redirects,
    a file from dist/ (html_handling auto-trailing-slash) or its own code (WORKER_PATHS),
    not the 404 page."""
    if path.startswith(WORKER_PATHS):
        return True
    for source, _, _ in rules:
        if path == source or (source.endswith('*') and path.startswith(source[:-1])):
            return True
    if path in ('/_headers', '/_redirects'):
        return False
    f = os.path.join(DIST, *[p for p in path.split('/') if p])
    if path.endswith('/'):
        return os.path.isfile(os.path.join(f, 'index.html')) or (path != '/' and os.path.isfile(f.rstrip(os.sep) + '.html'))
    return os.path.isfile(f) or os.path.isfile(f + '.html') or os.path.isfile(os.path.join(f, 'index.html'))


def check_links():
    rules = redirect_rules(read(os.path.join(DIST, '_redirects')))
    problems, count = [], [0, 0]

    def check(where, what, url, base='/'):
        path = _site_path(url, base)
        if path is None:
            return
        count[1] += 1
        if hidden(path) or path in HIDDEN_REDIRECTS:
            problems.append("%s: %s %s leads to a page that isn't public yet" % (where, what, url))
        elif not _served(path, rules):
            problems.append('%s: %s %s is neither in dist/ nor a redirect' % (where, what, url))

    for root, _, files in os.walk(DIST):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(root, f), DIST).replace(os.sep, '/')
            if hidden('/' + rel):
                problems.append("dist/%s: written, but it isn't public yet" % rel)
            if f.endswith('.html'):
                count[0] += 1
                base = '/' + (rel[:-len('index.html')] if f == 'index.html' else rel[:-len('.html')])
                links = _Links()
                links.feed(read(os.path.join(root, f)))
                links.close()
                for what, url in links.found:
                    check('dist/' + rel, what, url, base)
            elif f.endswith('.css'):
                for url in _css_urls(read(os.path.join(root, f))):
                    check('dist/' + rel, 'url()', url, '/' + rel)
    for url in re.findall(r'<loc>([^<]+)</loc>|href="([^"]+)"', read(os.path.join(DIST, 'sitemap.xml'))):
        check('dist/sitemap.xml', 'address', ''.join(url))
    for url in re.findall(r'(?im)^Sitemap:\s*(\S+)', read(os.path.join(DIST, 'robots.txt'))):
        check('dist/robots.txt', 'Sitemap:', url)
    for url in re.findall(r'<(/[^>]*)>', read(os.path.join(DIST, '_headers'))):
        check('dist/_headers', 'Link:', url)
    for source, dest, _ in rules:
        check('dist/_redirects', source + ' ->', re.sub(r'/:[A-Za-z]\w*.*$', '/', dest))
    if problems:
        raise SystemExit('Link check failed (public build):\n  ' + '\n  '.join(problems))
    print('link check: %d pages, %d addresses, all in dist/ or redirects; none lead to %s'
          % (count[0], count[1], ', '.join(HIDDEN) or 'a hidden page'))


# ==========================================================================
# LANGUAGE CHECK   (every build)
# Every guest page is in dist/ in both languages, each file one language: its <html
# lang>, a self-canonical and reciprocal hreflang, nothing of the other language left
# (data-l, data-aria-*), links that stay in its language (except those that say
# otherwise with hreflang, like EN · VI), and nothing under /vi/dough. Every section
# gate() keeps back is listed in CONTENT-NEEDED.md.
# ==========================================================================
def check_languages():
    problems = []
    guest = [r for r in PAGES if not r['kitchen'] and not r['hidden']]
    guest_paths = {r['path'] for r in guest}
    for r in guest:
        for lang in LANGS:
            path = lang_path(r['path'], lang)
            f = out_file(path)
            where = 'dist/' + os.path.relpath(f, DIST).replace(os.sep, '/')
            if not os.path.isfile(f):
                problems.append('%s: missing (the %s twin of %s)' % (where, lang, r['path']))
                continue
            h = read(f)
            m = re.search(r'<html lang="([a-z]+)"', h)
            if not m or m.group(1) != lang:
                problems.append('%s: <html lang="%s">, should be %s' % (where, m and m.group(1), lang))
            if re.search(r'\sdata-l="|\sdata-(aria|alt)-(en|vi)="', h):
                problems.append('%s: still carries both languages (data-l, data-aria- or data-alt-)' % where)
            if r['index']:
                canon = re.findall(r'<link rel="canonical" href="([^"]+)"', h)
                if canon != [SITE + path]:
                    problems.append('%s: canonical %s, should be %s' % (where, canon, SITE + path))
                alts = dict(re.findall(r'<link rel="alternate" hreflang="([a-z-]+)" href="([^"]+)"', h))
                want = {code: SITE + lang_path(r['path'], code) for code in LANGS}
                want['x-default'] = SITE + r['path']
                if alts != want:
                    problems.append('%s: hreflang %s, should be %s' % (where, alts, want))
            for tag in _A_TAG.findall(h):
                href = re.search(r'\shref="(/[^"]*)"', tag)
                if not href or ' hreflang="' in tag:
                    continue
                target = urlsplit(href.group(1)).path
                english = re.sub(r'^/vi(?=/)', '', target)
                if english not in guest_paths:
                    continue
                if (lang == 'vi') != target.startswith('/vi/'):
                    problems.append('%s: links to %s, a page in the other language' % (where, href.group(1)))
    if os.path.exists(os.path.join(DIST, 'vi', 'dough')):
        problems.append('dist/vi/dough/: the kitchen has no Vietnamese copy (it would skip the password)')
    listed = read(os.path.join(ROOT, 'CONTENT-NEEDED.md'))
    problems += ['gate %r ("%s") is not in CONTENT-NEEDED.md' % (k, w) for k, w in sorted(GATES.items())
                 if '`%s`' % k not in listed and not (k.startswith('event-') and '`event-<slug>`' in listed)]
    if problems:
        raise SystemExit('Language check failed:\n  ' + '\n  '.join(problems))
    print('language check: %d pages, each in English and Vietnamese; %d sections waiting for content'
          % (len(guest), len(GATES)))


# ==========================================================================
# SEARCH CHECK   (every build)
# Every structured-data block is valid JSON, with what search engines need for its
# type; every indexed page's title and description fit in a search result. Titles
# over 70 characters and descriptions under 50 or over 200 stop the build; over 60
# and over 160 are listed (Google may shorten them).
# ==========================================================================
LD_NEEDS = {'Restaurant': ('name', 'address', 'url'), 'WebSite': ('name', 'url'),
            'Event': ('name', 'startDate', 'location', 'url'), 'Menu': ('hasMenuSection', 'url'),
            'BreadcrumbList': ('itemListElement',), 'JobPosting': ('title', 'datePosted', 'hiringOrganization')}


def check_search():
    problems, long_titles, long_descs, blocks = [], [], [], 0
    for r in PAGES:
        if r['kitchen'] or r['hidden']:
            continue
        for lang in LANGS:
            f = out_file(lang_path(r['path'], lang))
            where = 'dist/' + os.path.relpath(f, DIST).replace(os.sep, '/')
            h = read(f)
            for raw in re.findall(r'<script type="?application/ld\+json"?>(.*?)</script>', h, flags=re.S):
                blocks += 1
                try:
                    data = json.loads(raw)
                except ValueError as e:
                    problems.append('%s: structured data that isn\'t JSON (%s)' % (where, e))
                    continue
                for item in data if isinstance(data, list) else [data]:
                    missing = [k for k in LD_NEEDS.get(item.get('@type'), ()) if not item.get(k)]
                    if missing:
                        problems.append('%s: %s without %s' % (where, item.get('@type'), ', '.join(missing)))
                    for ev in [item] + item.get('event', []):
                        if ev.get('@type') == 'Event' and ev.get('endDate', '') < ev.get('startDate', ''):
                            problems.append('%s: Event %s ends (%s) before it starts (%s)'
                                            % (where, ev.get('name'), ev['endDate'], ev['startDate']))
            if not r['index']:
                continue
            title = _html.unescape(re.search(r'<title>(.*?)</title>', h, flags=re.S).group(1))
            m = re.search(r'<meta name="?description"? content="([^"]*)"', h)
            desc = _html.unescape(m.group(1)) if m else ''
            if len(title) > 70:
                problems.append('%s: the title is %d characters (70 at most): %s' % (where, len(title), title))
            elif len(title) > 60:
                long_titles.append(where)
            if not 50 <= len(desc) <= 200:
                problems.append('%s: the description is %d characters (50 to 200)' % (where, len(desc)))
            elif len(desc) > 160:
                long_descs.append(where)
    if problems:
        raise SystemExit('Search check failed:\n  ' + '\n  '.join(problems))
    print('search check: %d structured-data blocks valid; titles and descriptions fit%s'
          % (blocks, ''.join('; %d %s over %d (may be shortened): %s' % (len(x), what, n, ', '.join(x))
                             for x, what, n in ((long_titles, 'titles', 60), (long_descs, 'descriptions', 160)) if x)))


# ==========================================================================
# BOOTSTRAP: make a clean checkout buildable
# Fonts come from the @fontsource npm packages (npm ci); share-card PNGs and
# BN Arora from build/assets.b64.json (a text manifest, see build/pack_assets.py).
# Nothing binary lives in git.
# ==========================================================================
def ensure_fonts():
    """Copy the woff2 files the site uses out of node_modules and write build/fonts.css."""
    fd = os.path.join(HERE, 'fonts')
    nm = os.path.join(ROOT, 'node_modules', '@fontsource')
    if not os.path.isdir(nm):
        if os.path.exists(os.path.join(HERE, 'fonts.css')) and os.path.isdir(fd) and os.listdir(fd):
            return  # a font set from an earlier run
        raise SystemExit('fonts: run `npm ci` first (needs the @fontsource packages in package.json)')
    if os.path.isdir(fd):
        rmtree(fd)        # nothing stale (an old family) may reach dist/
    os.makedirs(fd)
    css = []
    for pkg, family, styles in FONT_PLAN:
        uni = json.loads(read(os.path.join(nm, pkg, 'unicode.json')))
        for weight, style in styles:
            for sub in FONT_SUBSETS:
                fn = '%s-%s-%d-%s.woff2' % (pkg, sub, weight, style)
                shutil.copy2(os.path.join(nm, pkg, 'files', fn), os.path.join(fd, fn))
                css.append("@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:swap;\n"
                           "  src:url('/assets/fonts/%s') format('woff2');\n  unicode-range:%s;}"
                           % (family, style, weight, fn, uni[sub]))
    # BN Arora: one weight, upright only (the headings set font-synthesis: none).
    css.append("@font-face{font-family:'BN Arora';font-style:normal;font-weight:400;font-display:swap;\n"
               "  src:url('%s') format('woff2');}" % BN_ARORA_URL)
    write(os.path.join(HERE, 'fonts.css'),
          '/* The self-hosted fonts, generated by build/gen.py: the free fonts from the\n'
          '   @fontsource packages, split by unicode-range (a browser downloads a subset\n'
          '   only when the page uses it), and BN Arora. */\n'
          + '\n'.join(css) + '\n')


def unpack_assets():
    m = json.loads(read(os.path.join(HERE, 'assets.b64.json')))
    for rel, b64 in m.items():
        out = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if not os.path.exists(out):
            with open(out, 'wb') as f:
                f.write(base64.b64decode(b64))


def rmtree(path):
    def writable(func, p, _):          # Windows: read-only files
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=writable)
    else:
        shutil.rmtree(path, onerror=writable)


if __name__ == '__main__':
    ensure_fonts()
    unpack_assets()
    # Empty dist/ rather than delete it: a running `wrangler dev` keeps the folder open.
    os.makedirs(DIST, exist_ok=True)
    for f in os.listdir(DIST):
        p = os.path.join(DIST, f)
        if os.path.isdir(p):
            rmtree(p)
        else:
            os.chmod(p, stat.S_IWRITE)
            os.remove(p)
    og_cards()
    copy_existing()
    # Every page is built in both modes; write_pages() doesn't write the ones not public yet.
    for e in EVENTS:
        build_event(e)
    for fn in (build_home, build_about, build_food, build_wine, build_bar, build_events, build_private_dining,
               build_visit, build_booking, build_gift_cards, build_press, build_guest_privacy, build_accessibility,
               build_jobs, build_privacy, build_cookies, build_styleguide, build_dough, build_dough_log,
               build_dough_login, build_404):
        fn()
    written = write_pages()
    print('wrote %d pages: %d in English, %d in Vietnamese, %d for the kitchen' % (
        len(written), sum(1 for f in written if not os.path.relpath(f, DIST).startswith(('vi' + os.sep, 'dough'))),
        sum(1 for f in written if os.path.relpath(f, DIST).startswith('vi' + os.sep)),
        sum(1 for f in written if os.path.relpath(f, DIST).startswith('dough'))))
    if HIDE:
        print('built but not written, not public yet:', ', '.join(p for p in SITEMAP_PAGES if hidden_section(p)))
    if not FULL and WAITING:
        print('built but not written, waiting for content (CONTENT-NEEDED.md):', ', '.join(sorted(WAITING)))
    build_support()
    print('wrote support files')
    if HIDE:
        leave_out_unused()
    optimise()
    print('optimised')
    check_languages()
    check_search()
    if not FULL:
        check_links()
