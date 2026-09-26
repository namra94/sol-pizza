#!/usr/bin/env python3
"""
Build the sol.pizza static site: the "Printed menu" design.

    npm run build          (= python3 build/gen.py; run `npm ci` once first, for the fonts)

Writes plain, readable HTML into dist/, which the sol-pizza Worker serves.
Every page is generated here. Each line of copy appears twice, English then
Vietnamese, so the two never drift apart; the menu lives in build/menu-data.json.

  build/design/        tokens.css + printed-menu.css (the design), site.css (what
                       this repo adds), printed-menu.js (header, nav sheet, EN / VI)
  build/assets/        logo, illustrations and the sun pattern (SVG)
  build/menu-data.json food, wine and bar: names as the kitchen and bar write them
  src/                 role pages and privacy notice (re-wrapped here, copy
                       untouched), _redirects, favicon.svg, pixel.js
"""
import os, re, sys, json, stat, shutil, hashlib, subprocess, base64, html as _html
from datetime import date, datetime
from urllib.parse import quote

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
# Above the fold on every page: BN Arora (headings) and EB Garamond (text).
PRELOAD_FONTS = [BN_ARORA_URL, '/assets/fonts/eb-garamond-latin-400-normal.woff2']

# --------------------------------------------------------------------------
# site-wide facts: EDIT THESE, they appear on every page
# --------------------------------------------------------------------------
ADDRESS_EN = 'No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi'
ADDRESS_VI = 'Số 7, Ngõ 88 Quảng An, Tây Hồ, Hà Nội'
PHONE      = '+84 866 161 600'
PHONE_TEL  = 'tel:+84866161600'
EMAIL      = 'hello@sol.pizza'
MAPS_URL   = ('https://www.google.com/maps/search/?api=1&amp;query=Sol+Hanoi%2C+7+Ng%C3%B5+88+'
              'Qu%E1%BA%A3ng+An%2C+T%C3%A2y+H%E1%BB%93%2C+H%C3%A0+N%E1%BB%99i')
INSTAGRAM  = 'https://www.instagram.com/solhanoi/'

# ResDiary: paste the widget URL here (ResDiary > Promote > Widget configurator >
# Embed Code) and rebuild. The Booking page's booking box then shows the widget.
RESDIARY_URL = ''

# The wine lead and the home and wine meta descriptions spell the wine counts
# out in words ("Thirty wines", "26 wines by the glass"). They're right for the
# list as it is. If the list changes, the build stops here: update those lines
# (search this file for "Thirty" and "26 wines"), then PROSE_WINE_COUNTS.
PROSE_WINE_COUNTS = (30, 26)


# --------------------------------------------------------------------------
# bilingual helpers
# --------------------------------------------------------------------------
def t(en, vi):
    """One line in both languages. site.css shows the one <html lang> asks for."""
    if en == vi:
        return en
    return '<span data-l="en" lang="en">%s</span><span data-l="vi" lang="vi">%s</span>' % (en, vi)


def label(en, vi):
    """An aria-label in both languages; printed-menu.js swaps it with the page."""
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
HOURS_TAB  = t('Tue–Sun, 5pm–11pm', 'Thứ Ba – CN, 17:00 – 23:00')
INSTA_LINK = '<a href="%s">%s</a>' % (INSTAGRAM, t('@solhanoi on Instagram', '@solhanoi trên Instagram'))
MAPS_LINK_TEXT = t('Open in Google Maps', 'Mở trong Google Maps')
WINE_TAB   = t('%d wines, %d by the glass' % (WINES_TOTAL, WINES_GLASS),
               '%d loại vang, %d loại theo ly' % (WINES_TOTAL, WINES_GLASS))

MENU_TABS = [  # (key, href, name, descriptor)
    ('food', '/menu/',      t('Food', 'Món ăn'),   t('Pizza, pasta and small plates', 'Pizza, mì Ý và món khai vị')),
    ('wine', '/menu/wine/', t('Wine', 'Vang'),     WINE_TAB),
    ('bar',  '/menu/bar/',  t('Bar', 'Quầy bar'),  t('Cocktails, beer and sake', 'Cocktail, bia và sake')),
]
# The three tabs in the header, the mobile nav sheet and the footer: (key, href, name).
# Menu keeps its Food / Wine / Bar sub-tabs (MENU_TABS).
NAV_TABS = [('about',   '/about/',   t('About', 'Giới thiệu')),
            ('menu',    '/menu/',    t('Menu', 'Thực đơn')),
            ('booking', '/booking/', t('Booking', 'Đặt bàn'))]


# --------------------------------------------------------------------------
# shell
# --------------------------------------------------------------------------
# Applies the language before first paint: a ?lang=vi link (remembered), a
# #vi / #en link such as /privacy/#vi (this page only), else the saved choice.
LANG_SCRIPT = ("try{var q=/[?&]lang=(en|vi)(?:&|$)/.exec(location.search),"
               "h=/^#(en|vi)\\b/.exec(location.hash),"
               "l=q?q[1]:h?h[1]:localStorage.getItem('sol-lang');"
               "if(l==='vi'||l==='en')document.documentElement.lang=l;"
               "if(q)localStorage.setItem('sol-lang',l)}catch(e){}")

ANALYTICS = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=%(ga)s"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '%(ga)s');
</script>
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '%(pix)s');
fbq('track', 'PageView');
</script>
<!-- End Meta Pixel Code -->
<script defer src="/pixel.js"></script>""" % dict(ga=GA_ID, pix=FB_PIX)


def head(path, title, desc, og, ogtype, extra, index, og_text=None, og_locale=('en_GB', 'vi_VN')):
    """og_text: the share card's (title, description) when they differ from the English
    title and description; og_locale: (the card's locale, the alternate)."""
    (title_en, title_vi), (desc_en, desc_vi) = title, desc
    og_title, og_desc = og_text or (title_en, desc_en)
    url = SITE + path
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
        # The Adobe kit (Plunct) mustn't hold up the first paint: fetch it as a
        # preload and apply it once it arrives.
        '<link rel="preload" href="%s" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">' % TYPEKIT_KIT,
        '<noscript><link rel="stylesheet" href="%s"></noscript>' % TYPEKIT_KIT,
        '<link rel="stylesheet" href="/assets/fonts.css">',     # inlined by optimise()
        '<link rel="stylesheet" href="/assets/tokens.css">',
        '<link rel="stylesheet" href="/assets/printed-menu.css">',
        '<link rel="stylesheet" href="/assets/site.css">',
        '<script src="/assets/printed-menu.js" defer></script>',
    ] + ['<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' % f for f in PRELOAD_FONTS]
    if index:
        lines += [
            '<link rel="canonical" href="%s">' % url,
            '<link rel="alternate" hreflang="en" href="%s">' % url,
            '<link rel="alternate" hreflang="vi" href="%s?lang=vi">' % url,
            '<link rel="alternate" hreflang="x-default" href="%s">' % url,
        ]
    lines += [
        '<meta property="og:type" content="%s">' % ogtype,
        '<meta property="og:site_name" content="Sol">',
        '<meta property="og:title" content="%s">' % og_title,
        '<meta property="og:description" content="%s">' % og_desc,
    ]
    if og:
        lines += ['<meta property="og:image" content="%s">' % og,
                  '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">']
    lines += [
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:locale" content="%s">' % og_locale[0],
        '<meta property="og:locale:alternate" content="%s">' % og_locale[1],
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="theme-color" content="#f9e9d3">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
    ]
    if extra:
        lines.append(extra)
    lines += [ANALYTICS, '</head>']
    return '\n'.join(lines) + '\n'


CARET  = ('<svg class="caret" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" '
          'aria-hidden="true" focusable="false"><path d="M3 6l5 5 5-5"/></svg>')
BURGER = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
          'stroke-linecap="square" aria-hidden="true" focusable="false"><path d="M3 6.5h18M3 12h18M3 17.5h18"/></svg>')
CLOSE  = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
          'stroke-linecap="square" aria-hidden="true" focusable="false"><path d="M5 5l14 14M19 5L5 19"/></svg>')
HOME_LABEL = label('Sol, home', 'Sol, trang chủ')


def logo(w, h):
    return '<img src="/assets/sol-primary-red.svg" alt="Sol" width="%d" height="%d">' % (w, h)


def lang_switch():
    return ('<div class="lang" role="group" %s><button type="button" data-set-lang="en" aria-pressed="true">EN</button>'
            '<span aria-hidden="true">·</span><button type="button" data-set-lang="vi" aria-pressed="false" lang="vi">VI</button></div>'
            % label('Language', 'Ngôn ngữ'))


def tab_current(key, cur):
    """aria-current for a header tab. cur: about / food / wine / bar / booking, or None.
    Menu is the current page on Food (/menu/) and the current section on Wine and Bar."""
    if key == cur or (key == 'menu' and cur == 'food'):
        return ' aria-current="page"'
    if key == 'menu' and cur in ('wine', 'bar'):
        return ' aria-current="true"'
    return ''


def header(cur):
    """cur: about / food / wine / bar / booking, or None."""
    def subtabs():
        return ''.join('<li><a href="%s"%s>%s<span>%s</span></a></li>'
                       % (href, ' aria-current="page"' if key == cur else '', name, sub)
                       for key, href, name, sub in MENU_TABS)

    def tabs(caret):
        return ''.join('<li><a href="%s"%s%s>%s%s</a></li>'
                       % (href, ' data-menu-link' if caret and key == 'menu' else '',
                          tab_current(key, cur), name, CARET if caret and key == 'menu' else '')
                       for key, href, name in NAV_TABS)

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
  <nav class="subnav" {sub_l}><div class="wrap"><ul>{subtabs}</ul></div></nav>
</header>
<div class="navsheet" id="navsheet" role="dialog" aria-modal="true" {sheet_l} tabindex="-1" hidden>
  <div class="navsheet-top"><span></span><a href="/" {home}>{logo_s}</a>
    <button class="navsheet-close" type="button" {close_l} data-sheet-close>{close}</button></div>
  <ul class="navsheet-pages">{sheet_tabs}</ul>
  <div class="navsheet-foot">
    <div class="navsheet-meta"><span>{hours}</span>{lang}</div>
  </div>
</div>
""".format(lang=lang_switch(), home=HOME_LABEL, logo_s=logo(74, 26), logo_l=logo(165, 58),
           open_l=label('Open navigation', 'Mở menu điều hướng'), burger=BURGER,
           main_l=label('Main', 'Điều hướng chính'), tabs=tabs(True),
           sub_l=label('Menu sections', 'Các mục thực đơn'), subtabs=subtabs(),
           sheet_l=label('Navigation', 'Điều hướng'), sheet_tabs=tabs(False),
           close_l=label('Close navigation', 'Đóng menu điều hướng'), close=CLOSE, hours=HOURS_TAB)


def footer():
    more = [(href, name) for _, href, name in NAV_TABS] + [
        ('/jobs/', t('Work with us', 'Tuyển dụng')), ('/privacy/', t('Privacy', 'Bảo mật'))]
    return """<footer class="site-footer">
  <div class="wrap"><div class="footer-inner">
    <a class="footer-logo" href="/" {home}>{logo}</a>
    <div class="footer-cols"><section><h2>{find}</h2><p>{addr}</p><p><a href="{maps}">{maps_t}</a></p></section><section><h2>{open}</h2><p>{days}</p><p>{hours}</p><p>{closed}</p></section><section><h2>{talk}</h2><p><a href="{tel}">{phone}</a></p><p><a href="mailto:{email}">{email}</a></p><p>{insta}</p></section><nav {more_l}><h2>{more_h}</h2><ul>{more}</ul></nav></div>
    <p class="legal">{legal}</p>
  </div></div>
</footer>
""".format(home=HOME_LABEL, logo=logo(91, 32), find=t('Find us', 'Tìm chúng tôi'),
           addr=t(ADDRESS_EN, ADDRESS_VI), maps=MAPS_URL, maps_t=MAPS_LINK_TEXT,
           open=t('Open', 'Giờ mở cửa'), days=t('Tuesday to Sunday', 'Thứ Ba đến Chủ Nhật'),
           hours=t('5pm–11pm', '17:00 – 23:00'), closed=t('Closed Mondays', 'Nghỉ thứ Hai'),
           talk=t('Talk to us', 'Liên hệ'), tel=PHONE_TEL, phone=PHONE, email=EMAIL,
           insta=INSTA_LINK, more_l=label('More', 'Thêm'), more_h=t('More', 'Thêm'),
           more=''.join('<li><a href="%s">%s</a></li>' % m for m in more),
           legal=t('© 2026 Công ty TNHH Aurelian · Tây Hồ, Hanoi',
                   '© 2026 Công ty TNHH Aurelian · Tây Hồ, Hà Nội'))


def page(path, body_class, title, desc, main, cur=None, og=None, ogtype='website',
         extra='', body_attrs='', index=True, out=None, verbatim=False,
         og_text=None, og_locale=('en_GB', 'vi_VN')):
    """Write one page. title and desc are (English, Vietnamese) pairs.
    verbatim: leave main's text exactly as it is (the privacy notice).
    og_text, og_locale: see head()."""
    doc = head(path, title, desc, og, ogtype, extra, index, og_text, og_locale)
    doc += '<body class="%s"%s>\n%s\n' % (body_class, body_attrs, SUN_SPRITE)
    doc += nbsp('<a class="skip" href="#main">%s</a>\n' % t('Skip to content', 'Chuyển đến nội dung chính')
                + header(cur))
    doc += main if verbatim else nbsp(main)
    doc += nbsp(footer())
    doc += '</body>\n</html>\n'
    if out is None:
        out = os.path.join(DIST, path.strip('/'), 'index.html') if path != '/' \
              else os.path.join(DIST, 'index.html')
    write(out, doc)
    return out


def og_image(name):
    return '%s/og-%s.png' % (SITE, name)


# ==========================================================================
# STRUCTURED DATA (home and Booking)
# ==========================================================================
HOME_DESC = ('Wood-fired pizza, pasta made in-house and 26 wines by the glass. '
             'Sol opens soon at No 7, Lane 88 Quang An, Tây Hồ, Hanoi.')

SCHEMA = '<script type="application/ld+json">\n%s\n</script>' % json.dumps({
    '@context': 'https://schema.org',
    '@type': 'Restaurant',
    '@id': 'https://sol.pizza/#restaurant',
    'name': 'Sol',
    'alternateName': 'Sol Hanoi',
    'url': 'https://sol.pizza/',
    'description': HOME_DESC,
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
    'openingHoursSpecification': [{
        '@type': 'OpeningHoursSpecification',
        'dayOfWeek': ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'opens': '17:00', 'closes': '23:00',
    }],
    'sameAs': [INSTAGRAM],
    'parentOrganization': {'@type': 'Organization', 'name': 'Công ty TNHH Aurelian'},
}, ensure_ascii=False, indent=2)


# ==========================================================================
# HOME  /
# The hero and the facts row, nothing more: the tabs carry the rest. "What Sol
# is", the three boxes and the pull quote are on /about/.
# ==========================================================================
def build_home():
    facts = [
        (t('Opening', 'Khai trương'), t('Soon', 'Sắp tới')),
        (t('Where', 'Địa điểm'), t('Lane 88 Quang An, Tây Hồ', 'Ngõ 88 Quảng An, Tây Hồ')),
        (t('Kitchen', 'Bếp'), t('Wood-fired Italian-American', 'Lò củi, ẩm thực Ý–Mỹ')),
        (t('Hours', 'Giờ mở cửa'), HOURS_TAB),
    ]
    main = """<main id="main">
<section class="hero wrap">
  <p class="eyebrow">{eyebrow}</p>
  <h1 class="hero-title">{h1}</h1>
  <p class="hand hero-hand">{hand}</p>
  <p class="hero-lead">{lead}</p>
  <div class="actions"><a class="btn btn-red" href="/booking/">{book}</a><a class="btn btn-outline" href="/menu/">{see_menu}</a></div>
</section>
<div class="wrap"><dl class="facts">{facts}</dl></div>
</main>
""".format(
        eyebrow=t('Opening soon · Tây Hồ, Hanoi', 'Sắp khai trương · Tây Hồ, Hà Nội'),
        # lang="vi": BN Arora has no Vietnamese letters, so site.css sets the name in Philosopher
        h1=t('Sol is back in <span lang="vi">Tây Hồ</span>.', 'Sol trở lại Tây Hồ.'),
        hand=t('with the oven we always wanted', 'cùng chiếc lò chúng tôi luôn mong muốn'),
        lead=t('Sol Pizza closed last year. Sol opens on the same stretch of Tây Hồ with more room: '
               'a bigger kitchen, a proper bar and a Pavesi wood-fired oven built in Italy.',
               'Sol Pizza đã đóng cửa năm ngoái. Sol sẽ mở lại ngay trên con phố ấy ở Tây Hồ, với nhiều '
               'không gian hơn: căn bếp rộng hơn, một quầy bar đúng nghĩa và chiếc lò củi Pavesi chế '
               'tác tại Ý.'),
        book=BOOK, see_menu=t('See the menu', 'Xem thực đơn'),
        # The photo band goes here, between the buttons and the facts row, once
        # there's photography: 1040 × 520 (2:1).
        facts=''.join('<div><dt>%s</dt><dd>%s</dd></div>' % f for f in facts),
    )
    return page('/', 'page-home',
                ('Sol — Italian-American restaurant in Tây Hồ, Hanoi',
                 'Sol — Nhà hàng Ý–Mỹ tại Tây Hồ, Hà Nội'),
                (HOME_DESC,
                 'Pizza lò củi, mì Ý làm tại nhà hàng và 26 loại vang theo ly. Sol sắp khai trương tại '
                 'số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội.'),
                main, og=og_image('home'), extra=SCHEMA)

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


def menu_section(sec, sun_n, body):
    sid = 's-' + slug(sec['name'])
    intro = sec.get('intro', '')
    intro_html = '<p>%s</p>' % t(esc(intro), esc(sec.get('intro_vi') or intro)) if intro else ''
    return ('<section class="menu-section" aria-labelledby="%s"><header class="section-head">%s'
            '<h2 id="%s">%s</h2>%s</header>%s</section>'
            % (sid, sun(sun_n), sid, t(esc(sec['name']), esc(sec.get('name_vi') or sec['name'])),
               intro_html, body))


def item(name, desc, desc_vi, after_name='', cls=''):
    li = '<li%s><p class="item-name">%s%s</p>' % (cls, esc(name), after_name)
    if desc:
        li += '<p class="item-desc">%s</p>' % t(esc(desc), esc(desc_vi or desc))
    return li + '</li>'


def good_to_know():
    g = MENU['good_to_know']
    return ('<section class="good-to-know" %s><div><h2>%s</h2><p>%s</p></div><div><h2>%s</h2><ul>%s</ul></div></section>'
            % (label('Good to know', 'Thông tin hữu ích'), t('Allergies', 'Dị ứng thực phẩm'),
               t(esc(g['allergies']), esc(g['allergies_vi'])), t('Good to know', 'Thông tin hữu ích'),
               ''.join('<li>%s</li>' % t(esc(en), esc(vi)) for en, vi in zip(g['rules'], g['rules_vi']))))


def menu_page(path, key, body_class, title, desc, main, og):
    return page(path, body_class + ' section-menu', title, desc, '<main id="main" class="wrap">\n' + main + '\n</main>\n',
                cur=key, og=og_image(og))


def build_food():
    food = MENU['food']
    parts = [
        page_title(MENU_EYEBROW, t('What we’re cooking', 'Chúng tôi nấu gì'),
                   t('Pizza from the wood oven, pasta made in-house and small plates to start.',
                     'Pizza từ lò củi, mì Ý làm tại nhà hàng và món khai vị để mở đầu.'), TOMATOES),
        note_box(t('A first draft', 'Bản nháp đầu tiên'),
                 t('These are the dishes we cooked at Sol Pizza, and they’re where Sol starts. Expect '
                   'changes as the new kitchen settles in, and prices here once they’re set.',
                   'Đây là những món chúng tôi từng nấu tại Sol Pizza, và là điểm khởi đầu của Sol. '
                   'Các món sẽ còn thay đổi khi căn bếp mới đi vào nếp, và giá sẽ được đăng ở đây '
                   'khi đã chốt.')),
    ]
    for i, sec in enumerate(food['sections']):
        items = ''.join(
            item(d['name'], d['description'], d.get('description_vi'),
                 ''.join('&ensp;<span class="tag">%s</span>' % t(tag, TAGS_VI.get(tag, tag)) for tag in d['tags']))
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
    legend = ''.join('<span><b>%s</b>%s</span>' % (t(lg['mark'], lg['mark_vi']), t(lg['meaning'], lg['meaning_vi']))
                     for lg in wine['legend'])
    parts = [
        page_title(MENU_EYEBROW, t('The wine list', 'Danh sách vang'),
                   t('Thirty wines, from Burgundy and Tuscany to Moldova and the Czech Republic. '
                     'Twenty-six of them are open by the glass.',
                     'Ba mươi loại vang, từ Bourgogne và Toscana đến Moldova và Cộng hòa Séc. '
                     'Hai mươi sáu loại trong số đó có phục vụ theo ly.'), GRAPE),
        '<p class="legend">%s</p>' % legend,
        note_box(t('A first draft', 'Bản nháp đầu tiên'),
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
            rows.append(item(w['name'], w['details'], w.get('details_vi'), marks, ' class="wine"'))
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
             'something. Prices are on the printed list in the room.',
             'Hãy cho chúng tôi biết bạn thích uống gì và tầm giá mong muốn, chúng tôi sẽ tìm cho '
             'bạn một chai phù hợp. Giá có trên danh sách in tại nhà hàng.')),
        good_to_know(),
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
    parts = [page_title(MENU_EYEBROW, t('The bar', 'Quầy bar'),
                        t('Cocktails, Bia Craft on draft, sake and everything else. It’s a full bar, '
                          'so ask for anything.',
                          'Cocktail, bia tươi Bia Craft, sake và mọi thứ còn lại. Quầy bar đầy đủ, '
                          'bạn cứ gọi món mình thích.'))]
    for i, sec in enumerate(bar['sections']):
        if all(not d['description'] for d in sec['items']) and sec['name'] == 'Soft drinks':
            body = '<p class="inline-list">%s</p>' % ' · '.join(esc(d['name']) for d in sec['items'])
        else:
            body = '<ul class="menu-grid">%s</ul>' % ''.join(
                item(d['name'], d['description'], d.get('description_vi')) for d in sec['items'])
        parts.append(menu_section(sec, 5 + i, body))
    parts += [
        '<section class="offer" aria-labelledby="happy-hour"><h2 id="happy-hour">%s</h2><p class="hand">%s</p><p>%s</p></section>'
        % ('Happy hour', t('5–7pm', '17:00 – 19:00'),
           t('Tuesday to Sunday: 50% off house wine, sake and draft beer.',
             'Thứ Ba đến Chủ Nhật: giảm 50% vang quán, sake và bia tươi.')),
        good_to_know(),
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
        t('We’re still building: the oven is in and the team is coming together. Underneath it '
          'all is one rule — food quality is non-negotiable.',
          'Chúng tôi vẫn đang hoàn thiện: lò đã về và đội ngũ đang dần đầy đủ. Nền tảng của tất cả '
          'là một nguyên tắc — chất lượng món ăn là điều không thể thỏa hiệp.'),
    ]
    main = '\n'.join([
        '<main id="main">',
        '<div class="wrap"><header class="page-title"><p class="eyebrow">%s</p><h1>%s</h1>%s</header></div>' % (
            t('What Sol is', 'Sol là gì'),
            t('A neighbourhood restaurant built around pizza.',
              'Một nhà hàng của khu phố, lấy pizza làm trung tâm.'),
            ''.join('<p class="page-lead">%s</p>' % p for p in intro)),
        '<div class="wrap"><ul class="trio">%s</ul></div>' % ''.join(
            '<li><h2>%s</h2><p>%s</p></li>' % box for box in trio),
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
            # HIDE until Arman supplies it: one line on what closing meant to him and the team.
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
        '<figure class="pullquote wrap">%s<blockquote><p>%s</p></blockquote>%s</figure>' % (
            sun(4),
            t('A restaurant is a room, a team and a menu. Get the room right and the other two get easier.',
              'Một nhà hàng là một không gian, một đội ngũ và một thực đơn. Làm đúng không gian, hai '
              'điều còn lại sẽ dễ hơn.'),
            sun(7)),
        # CONFIRM: ships without Long; Arman to say whether to add "and Long runs the floor."
        # HIDE until supplied: a few lines on Ngọc.
        prose_section('s-team', 8, t('The team', 'Đội ngũ'), [
            '<p style="text-align:center">%s</p>' % t('Ngọc runs the kitchen.', 'Ngọc phụ trách bếp.'),
        ], style=' style="margin-top:0"', level=3),
        '<div class="wrap"><section class="offer" aria-labelledby="s-join"><h3 id="s-join">%s</h3><p>%s</p>'
        '<a class="btn btn-red" href="/jobs/">%s</a></section></div>' % (
            t('Build it with us', 'Cùng chúng tôi dựng nên Sol'),
            t('We’re hiring for the kitchen and the floor before we open. If you want to be on the '
              'first team in the new room, start here.',
              'Chúng tôi đang tuyển cho cả bếp và khu phục vụ trước ngày khai trương. Nếu bạn muốn là '
              'một phần của đội ngũ đầu tiên, các vị trí đang mở ở đây.'),
            t('See open roles', 'Xem vị trí tuyển dụng')),
        '</section>',
        '</main>', ''])
    return page('/about/', 'page-about',
                ('About — Sol, Tây Hồ', 'Giới thiệu — Sol, Tây Hồ'),
                ('We closed Sol Pizza to build Sol: a bigger kitchen, a proper bar and a Pavesi '
                 'wood-fired oven on Quang An.',
                 'Chúng tôi đóng cửa Sol Pizza để xây dựng Sol: căn bếp rộng hơn, một quầy bar đúng '
                 'nghĩa và lò củi Pavesi trên phố Quảng An.'),
                main, cur='about', og=og_image('story'))


# ==========================================================================
# BOOKING  /booking/   booking, hours, address, contact (/visit/ redirects here)
# ==========================================================================
def build_booking():
    if RESDIARY_URL:
        booking_p = t('Book online below, or call or email us.',
                      'Đặt bàn trực tuyến ngay bên dưới, hoặc gọi điện hay gửi email cho chúng tôi.')
        widget = ('<iframe src="%s" title="Book a table at Sol" %s loading="lazy" '
                  'style="display:block;width:100%%;min-height:640px;margin-top:26px;border:0"></iframe>\n  '
                  % (RESDIARY_URL, label('Book a table at Sol', 'Đặt bàn tại Sol')))
    else:
        booking_p = t('Online booking opens closer to the day we open. Until then, call or email us '
                      'and we’ll hold you a table for opening week.',
                      'Chúng tôi sẽ mở đặt bàn trực tuyến khi gần đến ngày khai trương. Từ nay đến lúc '
                      'đó, bạn cứ gọi điện hoặc gửi email, chúng tôi sẽ giữ bàn cho bạn trong tuần '
                      'khai trương.')
        widget = '<!-- ResDiary: set RESDIARY_URL in build/gen.py and its widget appears here. -->\n  '
    main = """<main id="main">
<div class="wrap">{title}</div>
<div class="wrap"><section class="offer booking" id="book" aria-labelledby="book-h">
  <p class="eyebrow">{k1}</p><h2 id="book-h">{book}</h2>
  <p>{booking_p}</p>
  {widget}<dl class="book-contact"><div><dt>{l_phone}</dt><dd>{phone}</dd></div><div><dt>Email</dt><dd>{email}</dd></div></dl>
  <p class="offer-note">{groups}</p>
</section></div>
<div class="wrap"><div class="visit-info">
  <section aria-labelledby="v-hours"><h2 class="label" id="v-hours">{l_hours}</h2><dl class="hours"><div><dt>{mon}</dt><dd>{closed}</dd></div><div><dt>{tue_sun}</dt><dd>{hours}</dd></div></dl><p class="small">{from_open}</p></section>
  <section aria-labelledby="v-addr"><h2 class="label" id="v-addr">{l_addr}</h2><p>{addr}</p><a class="link-sc" href="{maps}">{maps_t}</a></section>
  <section aria-labelledby="v-contact"><h2 class="label" id="v-contact">{l_talk}</h2><p><a href="{tel}">{phone}</a><br><a href="mailto:{email}">{email}</a><br>{insta}</p></section>
</div></div>
<section class="prose-section wrap" aria-labelledby="s-gtk"><header class="section-head">{sun}<h2 id="s-gtk">{gtk}</h2></header><dl class="gtk-items"><div><dt>{children}</dt><dd>{children_d}</dd></div></dl></section>
</main>
""".format(
        # HIDE until supplied: large groups (seat count), getting here, parking.
        title=page_title(t('Visit', 'Ghé thăm'),
                         t('Find us and book a table', 'Tìm chúng tôi và đặt bàn'),
                         t('Sol is on the first two floors of No 7, Lane 88 Quang An. We’re opening soon.',
                           'Sol nằm ở hai tầng đầu của tòa nhà số 7, ngõ 88 Quảng An. Chúng tôi sắp khai trương.')),
        k1=t('Reservations', 'Đặt chỗ'), book=BOOK, booking_p=booking_p, widget=widget,
        # Until online booking is live: the number and address as text to copy,
        # not buttons that open another app (Linh, 24 Sep).
        l_phone=t('Phone', 'Điện thoại'), email=EMAIL, tel=PHONE_TEL,
        groups=t('Seven or more? Email us and we’ll look after you personally.',
                 'Nhóm từ bảy người trở lên: vui lòng gửi email, chúng tôi sẽ sắp xếp riêng cho bạn.'),
        l_hours=t('Opening hours', 'Giờ mở cửa'), mon=t('Monday', 'Thứ Hai'),
        closed=t('Closed', 'Đóng cửa'), tue_sun=t('Tuesday to Sunday', 'Thứ Ba đến Chủ Nhật'),
        hours=t('5pm–11pm', '17:00 – 23:00'),
        from_open=t('From the day we open.', 'Từ ngày chúng tôi khai trương.'),
        l_addr=t('Address', 'Địa chỉ'), addr=t(ADDRESS_EN, ADDRESS_VI),
        maps=MAPS_URL, maps_t=MAPS_LINK_TEXT,
        l_talk=t('Talk to us', 'Liên hệ'), phone=PHONE, insta=INSTA_LINK,
        sun=sun(3), gtk=t('Good to know', 'Thông tin hữu ích'),
        children=t('Children', 'Trẻ em'),
        children_d=t('Very welcome. We have high chairs, and the kitchen will happily make something plain.',
                     'Rất hoan nghênh. Có ghế ăn cho bé, và bếp sẵn sàng làm món đơn giản.'),
    )
    return page('/booking/', 'page-booking',
                ('Booking — Sol, Tây Hồ', 'Đặt bàn — Sol, Tây Hồ'),
                ('No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi. Tuesday to Sunday, 5pm–11pm, from the '
                 'day we open. Call or email to hold a table.',
                 'Số 7, ngõ 88 Quảng An, Tây Hồ, Hà Nội. Thứ Ba đến Chủ Nhật, 17:00 – 23:00, kể từ '
                 'ngày khai trương. Gọi điện hoặc gửi email để giữ bàn.'),
                main, cur='booking', og=og_image('visit'),
                # iOS would turn the booking box's phone number back into a link
                extra='<meta name="format-detection" content="telephone=no">\n' + SCHEMA)


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


def vnd(n, sep):
    return '{:,}'.format(n).replace(',', sep)


def band_en(lo_hi, dash=' – '):
    return dash.join(vnd(n, ',') for n in lo_hi)


def band_vi(lo_hi):
    return ' – '.join(vnd(n, '.') for n in lo_hi)


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
            'Lương cơ bản <span class="nowrap">%s VNĐ</span> gross/tháng<br>'
            '+ phí phục vụ &amp; tip ước tính <span class="nowrap">%s VNĐ</span>/tháng'
            % (band_vi(r['base']), band_vi(SERVICE)))
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
  <a class="btn btn-red" href="mailto:jobs@sol.pizza">{email_jobs}</a><p class="privacy-links"><a href="/privacy/#en" lang="en" hreflang="en">Applicant privacy notice</a> · <a href="/privacy/#vi" lang="vi" hreflang="vi">Thông báo bảo mật ứng viên</a></p></section></div>
{script}
</main>
""".format(
        title=page_title(t('We’re hiring · Tây Hồ, Hanoi', 'Tuyển dụng · Tây Hồ, Hà Nội'),
                         t('Come and build the new Sol.', 'Cùng xây dựng Sol mới.'),
                         t('We’re hiring now for our opening, in the kitchen and on the floor, and '
                           'every application gets a reply.',
                           'Chúng tôi sắp khai trương. Bếp và khu phục vụ đang tuyển ngay bây giờ, và '
                           'mọi hồ sơ đều nhận được phản hồi.')),
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
         ('We’re hiring a Host and our opening team for the floor and the kitchen. Every application '
          'gets a reply.',
          'Chúng tôi đang tuyển Lễ tân (Host) và đội ngũ khai trương cho khu phục vụ và bếp. Mọi hồ '
          'sơ đều được phản hồi.'),
         main, og=og_image('jobs'), extra=ROUND_SCRIPT, body_attrs=' data-page="index"')
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
               t('See open roles', 'Xem vị trí tuyển dụng'), apply_button(r), APPLY_SCRIPT))

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
        posting, ensure_ascii=False, indent=2).replace('</', '<\\/')
    og_title = 'Tuyển %s — Sol, Tây Hồ' % r['name_en']
    og_desc = 'Lương cơ bản %s + phí phục vụ ước tính %s/tháng. Hạn nộp %s.' % (
        trieu(r['base']), trieu(SERVICE), vi_date(CLOSES, True).split(' ')[-1])
    desc_en = ('%s at Sol, Tây Hồ, Hanoi. Base salary %s VND a month, plus service charge and tips, est. '
               '%s VND a month. Applications close %s %d.'
               % (r['name_en'], band_en(r['base'], '–'), band_en(SERVICE, '–'), en_date(CLOSES), CLOSES.year))
    desc_vi = 'Tuyển %s tại Sol, Tây Hồ, Hà Nội. %s' % (r['name_vi'], og_desc)
    page(open_role_path(r), 'page-role',
         (esc_attr('%s — Sol, Tây Hồ' % r['name_en']), esc_attr('%s — Sol, Tây Hồ' % r['name_vi'])),
         (esc_attr(desc_en), esc_attr(desc_vi)), main, og=og_image('jobs'),
         og_text=(esc_attr(og_title), esc_attr(og_desc)), og_locale=('vi_VN', 'en_GB'),
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
         main, og='%s/jobs/og-%s.png' % (SITE, r['slug']),
         extra='<meta name="robots" content="noindex,follow">' if filled else '',
         body_attrs=' data-page="%s" data-role="%s" data-slug="%s"'
                    % ('role-filled' if filled else 'role', r['name_en'], r['slug']),
         out=os.path.join(DIST, 'jobs', r['slug'] + '.html'))


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
# 404 and support files
# ==========================================================================
def build_404():
    main = ('<main id="main" class="wrap">\n<header class="page-title"><h1>%s</h1></header>\n'
            '<div class="actions"><a class="btn btn-red" href="/menu/">%s</a><a class="btn btn-outline" href="/booking/">%s</a></div>\n'
            '</main>\n' % (t('We can’t find that page.', 'Chúng tôi không tìm thấy trang này.'),
                           t('Menu', 'Thực đơn'), t('Booking', 'Đặt bàn')))
    return page('/404.html', 'page-404', ('Page not found — Sol', 'Không tìm thấy trang — Sol'),
                ('Page not found.', 'Không tìm thấy trang.'), main, og=og_image('home'), index=False,
                extra='<meta name="robots" content="noindex">', body_attrs=' data-page="404"',
                out=os.path.join(DIST, '404.html'))


SITEMAP_PAGES = ['/', '/about/', '/menu/', '/menu/wine/', '/menu/bar/', '/booking/', '/jobs/']


def build_support():
    pages = SITEMAP_PAGES + [role_path(r) for r in ROLES if r['status'] == 'open'] + \
        [open_role_path(r) for r in OPEN_ROLES]
    urls = []
    for p in pages:
        pri = '1.0' if p == '/' else ('0.9' if p.startswith(('/about/', '/menu/', '/booking/')) else '0.6')
        urls.append(
            '  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority>\n'
            '    <xhtml:link rel="alternate" hreflang="en" href="%s%s"/>\n'
            '    <xhtml:link rel="alternate" hreflang="vi" href="%s%s?lang=vi"/>\n'
            '  </url>' % (SITE, p, TODAY, pri, SITE, p, SITE, p))
    write(os.path.join(DIST, 'sitemap.xml'),
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
          '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(urls) + '\n</urlset>\n')
    write(os.path.join(DIST, 'robots.txt'),
          'User-agent: *\nAllow: /\nDisallow: /privacy/\n\nSitemap: %s/sitemap.xml\n' % SITE)
    # Redirects live in src/_redirects; Cloudflare applies the copy in dist/.
    shutil.copy2(os.path.join(SRC, '_redirects'), os.path.join(DIST, '_redirects'))


def copy_existing():
    """Static files that aren't generated: favicon, pixel.js, share cards, design, SVGs, fonts."""
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
    for f in ('tokens.css', 'printed-menu.css', 'site.css', 'printed-menu.js'):
        shutil.copy2(os.path.join(DESIGN, f), os.path.join(assets, f))
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
# Link: early hints: the two fonts above the fold, and the Adobe kit's hosts
# (its CSS on use.typekit.net @imports Adobe's counter from p.typekit.net).
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Cache-Control: public, max-age=0, must-revalidate
  Link: %s, <https://use.typekit.net>; rel=preconnect; crossorigin, <https://use.typekit.net>; rel=preconnect, <https://p.typekit.net>; rel=preconnect

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
""" % ', '.join('<%s>; rel=preload; as=font; type=font/woff2; crossorigin' % f for f in PRELOAD_FONTS))


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
    copy_existing()
    for fn in (build_home, build_about, build_food, build_wine, build_bar, build_booking,
               build_privacy, build_404):
        print('wrote', os.path.relpath(fn(), ROOT))
    build_jobs()
    print('wrote jobs/ and the role pages')
    build_support()
    print('wrote support files')
    optimise()
    print('optimised')
