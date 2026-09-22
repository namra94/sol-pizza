#!/usr/bin/env python3
"""
Build the sol.pizza static site.

    python3 build/gen.py

Writes plain, readable HTML into dist/. Everything a human needs to edit
day-to-day (dish names, prices, hours, copy) lives in this file in one place,
in both English and Vietnamese, so the two never drift apart.
"""
import os, re, shutil, html as _html
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, 'dist')
SRC  = os.path.join(ROOT, 'src')       # the existing deployed site (jobs, privacy)
PART = os.path.join(ROOT, 'partials')

SITE   = 'https://sol.pizza'
GA_ID  = 'G-SLBWDVH550'
FB_PIX = '856214124247013'
TODAY  = date.today().isoformat()

MARK_SOL   = open(os.path.join(PART, 'mark-sol.svg')).read()
MARK_LOCK  = open(os.path.join(PART, 'mark-sol-hanoi.svg')).read()

# --------------------------------------------------------------------------
# bilingual helpers
# --------------------------------------------------------------------------
def t(en, vi, tag='span'):
    """Inline bilingual pair."""
    return ('<{tag} data-l="en" lang="en">{en}</{tag}>'
            '<{tag} data-l="vi" lang="vi">{vi}</{tag}>').format(tag=tag, en=en, vi=vi)

def tb(en, vi, tag='div', cls=''):
    """Block-level bilingual pair."""
    c = ' class="%s"' % cls if cls else ''
    return ('\n<{tag}{c} data-l="en" lang="en">{en}</{tag}>'
            '\n<{tag}{c} data-l="vi" lang="vi">{vi}</{tag}>').format(tag=tag, c=c, en=en, vi=vi)

def todo(s):
    return '<span class="todo">%s</span>' % s

# --------------------------------------------------------------------------
# site-wide facts — EDIT THESE, they appear on every page
# --------------------------------------------------------------------------
ADDRESS_EN = 'No 7, Lane 88 Quang An Street, Tây Hồ, Hanoi'
ADDRESS_VI = 'Số 7, Ngõ 88 Quảng An, Tây Hồ, Hà Nội'
PHONE      = '+84 866 161 600'
PHONE_TEL  = 'tel:+84866161600'
EMAIL      = 'hello@sol.pizza'
MAPS_URL   = 'https://www.google.com/maps/search/?api=1&amp;query=Sol+Hanoi%2C+7+Ng%C3%B5+88+Qu%E1%BA%A3ng+An%2C+T%C3%A2y+H%E1%BB%93%2C+H%C3%A0+N%E1%BB%99i'
INSTAGRAM  = 'https://instagram.com/'                        # TODO: real handle

NAV = [
    ('/',       'Home',  'Trang chủ'),
    ('/menu/',  'Menu',  'Thực đơn'),
    ('/story/', 'Story', 'Câu chuyện'),
    ('/visit/', 'Visit', 'Ghé thăm'),
]

# --------------------------------------------------------------------------
# shell
# --------------------------------------------------------------------------
HEAD_TPL = """<!doctype html>
<html lang="en" data-lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_en}</title>
<meta data-title-en="{title_en}" data-title-vi="{title_vi}" name="x-titles">
<meta name="description" content="{desc_en}">
<link rel="canonical" href="{site}{path}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Sol">
<meta property="og:title" content="{title_en}">
<meta property="og:description" content="{desc_en}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{site}{path}">
<meta property="og:locale" content="en_GB">
<meta property="og:locale:alternate" content="vi_VN">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#A72024">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" hreflang="en" href="{site}{path}">
<link rel="alternate" hreflang="vi" href="{site}{path}?lang=vi">
<link rel="alternate" hreflang="x-default" href="{site}{path}">
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/be-vietnam-pro-latin-400-normal.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/eb-garamond-latin-600-normal.woff2" crossorigin>
<link rel="stylesheet" href="/assets/fonts.css">
<link rel="stylesheet" href="/assets/sol.css">
<script>
/* Set the language before first paint so there is no flash of English. */
(function(){{var l=null;try{{var q=new URLSearchParams(location.search).get('lang');
l=q||localStorage.getItem('sol-lang')||((navigator.language||'').toLowerCase().indexOf('vi')===0?'vi':'en');}}catch(e){{l='en';}}
l=(l==='vi')?'vi':'en';var d=document.documentElement;d.setAttribute('data-lang',l);d.setAttribute('lang',l);}})();
</script>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga}');
</script>
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{fbpix}');
fbq('track', 'PageView');
</script>
<!-- End Meta Pixel Code -->
<script defer src="/pixel.js"></script>
<script defer src="/assets/sol.js"></script>
{head_extra}
</head>
<body{body_attrs}>
<a class="sr-only" href="#main">Skip to content</a>
"""

def header(path):
    links = []
    for href, en, vi in NAV:
        cur = ' aria-current="page"' if href == path else ''
        links.append('    <a href="%s"%s>%s</a>' % (href, cur, t(en, vi)))
    return """<header class="site"><div class="wrap">
  <a class="brandmark" href="/" aria-label="Sol">%s</a>
  <button class="navtoggle" aria-expanded="false" aria-controls="sitenav">%s</button>
  <nav class="site" id="sitenav" aria-label="Main">
%s
    <a class="nav-book" href="/visit/#book">%s</a>
    <div class="langswitch" role="group" aria-label="Language">
      <button type="button" data-lang="en" aria-pressed="true">EN</button>
      <button type="button" data-lang="vi" aria-pressed="false">VI</button>
    </div>
  </nav>
</div></header>
""" % (MARK_SOL, t('Menu', 'Menu'), '\n'.join(links), t('Book', 'Đặt bàn'))

STICKY = {
    'book':  '<div class="stickybar"><a class="btn wide" href="/visit/#book">%s</a></div>'
             % t('Book a table', 'Đặt bàn'),
    'apply': '<div class="stickybar"><a class="btn wide" href="#apply">%s</a></div>'
             % t('Apply for this role', 'Ứng tuyển vị trí này'),
    'jobs':  '<div class="stickybar"><a class="btn wide" href="mailto:jobs@sol.pizza">%s</a></div>'
             % t('Email jobs@sol.pizza', 'Gửi email tới jobs@sol.pizza'),
    'none':  '',
}

def footer(sticky='book'):
    navlinks = '\n'.join(
        '      <li><a href="%s">%s</a></li>' % (h, t(en, vi)) for h, en, vi in NAV[1:])
    return """<footer class="site"><div class="wrap">
  <span class="fmark">%s</span>
  <div class="footgrid">
    <div>
      <h3>%s</h3>
      <p data-l="en" lang="en">%s</p>
      <p data-l="vi" lang="vi">%s</p>
      <p><a href="%s" rel="noopener">%s</a></p>
    </div>
    <div>
      <h3>%s</h3>
      <ul>
        <li><a href="%s">%s</a></li>
        <li><a href="mailto:%s">%s</a></li>
        <li><a href="%s" rel="noopener">Instagram</a></li>
      </ul>
    </div>
    <div>
      <h3>%s</h3>
      <ul>
%s
        <li><a href="/jobs/">%s</a></li>
        <li><a href="/privacy/">%s</a></li>
      </ul>
    </div>
  </div>
  <p class="legal">%s</p>
</div></footer>
%s
</body></html>
""" % (
    MARK_LOCK,
    t('Find us', 'Tìm chúng tôi'),
    ADDRESS_EN, ADDRESS_VI,
    MAPS_URL, t('Open in Google Maps', 'Mở trong Google Maps'),
    t('Contact', 'Liên hệ'),
    PHONE_TEL, PHONE, EMAIL, EMAIL, INSTAGRAM,
    t('More', 'Thêm'),
    navlinks,
    t('Work at Sol', 'Tuyển dụng'),
    t('Privacy', 'Bảo mật'),
    t('© 2026 CÔNG TY TNHH AURELIAN · Tây Hồ, Hanoi',
      '© 2026 CÔNG TY TNHH AURELIAN · Tây Hồ, Hà Nội'),
    STICKY[sticky],
)

def page(path, slug, title_en, title_vi, desc_en, desc_vi, body,
         head_extra='', ogtype='website', body_attrs='', out=None, nav_path=None,
         og=None, sticky='book'):
    doc = HEAD_TPL.format(title_en=title_en, title_vi=title_vi,
                          desc_en=desc_en, desc_vi=desc_vi,
                          site=SITE, path=path, slug=slug, ogtype=ogtype,
                          ga=GA_ID, fbpix=FB_PIX, head_extra=head_extra,
                          body_attrs=body_attrs, og=og or '%s/og-%s.png' % (SITE, slug))
    doc += header(nav_path or path)
    doc += body
    doc += footer(sticky)
    if out is None:
        out = os.path.join(DIST, path.strip('/'), 'index.html') if path != '/' \
              else os.path.join(DIST, 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(doc)
    return out


# ==========================================================================
# STRUCTURED DATA
# ==========================================================================
SCHEMA = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Restaurant",
  "@id": "https://sol.pizza/#restaurant",
  "name": "Sol",
  "alternateName": "Sol Hanoi",
  "url": "https://sol.pizza/",
  "description": "Italian-American cooking and a wood-fired oven in Tây Hồ, Hanoi.",
  "servesCuisine": ["Italian-American", "Pizza"],
  "priceRange": "$$",
  "image": "https://sol.pizza/og-home.png",
  "logo": "https://sol.pizza/favicon.svg",
  "email": "hello@sol.pizza",
  "telephone": "+84866161600",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Số 7, Ngõ 88 Quảng An",
    "addressLocality": "Tây Hồ",
    "addressRegion": "Hà Nội",
    "addressCountry": "VN"
  },
  "hasMenu": "https://sol.pizza/menu/",
  "acceptsReservations": "https://sol.pizza/visit/#book",
  "openingHoursSpecification": [
    { "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
      "opens": "17:00", "closes": "23:00" }
  ],
  "parentOrganization": { "@type": "Organization", "name": "CÔNG TY TNHH AURELIAN" }
}
</script>"""


# ==========================================================================
# HOME
# ==========================================================================
def build_home():
    facts = [
        ('Opening', 'Khai trương', 'October 2026', 'Tháng 10 năm 2026'),
        ('Where', 'Địa điểm', 'Tây Hồ, Hanoi', 'Tây Hồ, Hà Nội'),
        ('Kitchen', 'Bếp', 'Wood-fired, Italian-American', 'Lò củi, ẩm thực Ý–Mỹ'),
        ('Hours', 'Giờ mở cửa', 'Tue – Sun, 17:00 – 23:00', 'Thứ Ba – CN, 17:00 – 23:00'),
    ]
    factshtml = '\n'.join(
        '      <div><dt>%s</dt><dd>%s</dd></div>' % (t(a, b), t(c, d))
        for a, b, c, d in facts)

    teasers = [
        ('The oven', 'Lò nướng',
         'A Pavesi wood-fired oven, built in Italy and shipped to Tây Hồ. '
         'Dough fermented slowly, then thirty seconds of real fire.',
         'Lò củi Pavesi, chế tác tại Ý và đưa về Tây Hồ. Bột ủ chậm, '
         'rồi ba mươi giây trong lửa thật.'),
        ('The room', 'Không gian',
         'Two floors, under 200 square metres, a bar you can eat at and a '
         'terrace for when Hanoi behaves.',
         'Hai tầng, dưới 200 mét vuông, quầy bar có thể ngồi ăn và một khoảng '
         'hiên cho những ngày Hà Nội dịu trời.'),
        ('The table', 'Bàn ăn',
         'Italian-American means generous. Plates meant for the middle of the '
         'table, and nobody counting.',
         'Ẩm thực Ý–Mỹ nghĩa là hào phóng. Món đặt giữa bàn, và không ai phải '
         'đắn đo.'),
    ]
    teaserhtml = '\n'.join(
        """      <div class="card">
        <h3>%s</h3>
        <p data-l="en" lang="en">%s</p>
        <p data-l="vi" lang="vi">%s</p>
      </div>""" % (t(a, b), c, d) for a, b, c, d in teasers)

    body = """<main id="main">
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="subtitle">{sub}</p>
    <p class="standfirst" data-l="en" lang="en">{sf_en}</p>
    <p class="standfirst" data-l="vi" lang="vi">{sf_vi}</p>
    <div class="btnrow">
      <a class="btn" href="/visit/#book">{cta1}</a>
      <a class="btn ghost" href="/menu/">{cta2}</a>
    </div>
    <dl class="facts">
{facts}
    </dl>
  </div>
</section>

<section class="band" style="padding-top:56px">
  <div class="wrap prose">
    <p class="kicker">{k1}</p>
    <h2>{h2a}</h2>
    <p class="lede" data-l="en" lang="en">{p1_en}</p>
    <p class="lede" data-l="vi" lang="vi">{p1_vi}</p>
    <p data-l="en" lang="en">{p2_en}</p>
    <p data-l="vi" lang="vi">{p2_vi}</p>
    <p><a href="/story/">{link1}</a></p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="grid g3">
{teasers}
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap prose">
    <blockquote class="belief">
      <p data-l="en" lang="en">{bq_en}</p>
      <p data-l="vi" lang="vi">{bq_vi}</p>
    </blockquote>
    <p class="kicker">{k2}</p>
    <h2>{h2b}</h2>
    <p data-l="en" lang="en">{p3_en}</p>
    <p data-l="vi" lang="vi">{p3_vi}</p>
    <p><a class="btn solid" href="/menu/">{cta3}</a></p>
  </div>
</section>

<section class="band ruled">
  <div class="wrap prose">
    <p class="kicker">{k3}</p>
    <h2>{h2c}</h2>
    <ul class="contactlist">
      <li><span class="k">{l_where}</span>
          <span class="v"><span data-l="en" lang="en">{addr_en}</span><span data-l="vi" lang="vi">{addr_vi}</span></span></li>
      <li><span class="k">{l_hours}</span>
          <span class="v">{hours}</span></li>
      <li><span class="k">{l_phone}</span><span class="v">{phone}</span></li>
    </ul>
    <p style="margin-top:22px">
      <a class="btn solid" href="/visit/#book">{cta4}</a>
      <a href="{maps}" rel="noopener" style="margin-left:16px">{maps_l}</a>
    </p>
  </div>
</section>
</main>
""".format(
        eyebrow=t('Opening October 2026 · Tây Hồ, Hanoi',
                  'Khai trương tháng 10 năm 2026 · Tây Hồ, Hà Nội'),
        h1=t('Sol comes back to Tây Hồ.', 'Sol trở lại Tây Hồ.'),
        sub=t('Italian-American, cooked over wood.', 'Ẩm thực Ý–Mỹ, nấu trên lửa củi.'),
        sf_en='Sol Pizza closed last year. What opens this October on the same '
              'stretch of Tây Hồ is the same idea with more room to breathe — a '
              'proper kitchen, a proper bar, and the oven we always wanted.',
        sf_vi='Sol Pizza đã đóng cửa năm ngoái. Tháng 10 này, ngay trên con phố ấy '
              'ở Tây Hồ, chúng tôi mở lại với nhiều không gian hơn — một căn bếp '
              'đúng nghĩa, một quầy bar đúng nghĩa, và chiếc lò chúng tôi luôn mong muốn.',
        cta1=t('Book a table', 'Đặt bàn'), cta2=t('See the menu', 'Xem thực đơn'),
        facts=factshtml,
        k1=t('What Sol is', 'Sol là gì'),
        h2a=t('A neighbourhood restaurant that takes the food seriously.',
              'Một nhà hàng của khu phố, nghiêm túc với món ăn.'),
        p1_en='Italian-American is a cuisine of immigrants: Italian technique, '
              'American appetite, and whatever the local market actually has that '
              'morning. In Hanoi that means Vietnamese herbs, Vietnamese seafood '
              'and imported flour, cheese and tinned tomatoes we do not compromise on.',
        p1_vi='Ẩm thực Ý–Mỹ là món ăn của người nhập cư: kỹ thuật Ý, khẩu vị Mỹ, và '
              'bất cứ thứ gì chợ địa phương có vào sáng hôm đó. Ở Hà Nội, điều đó '
              'nghĩa là rau thơm Việt, hải sản Việt, cùng bột mì, phô mai và cà chua '
              'hộp nhập khẩu mà chúng tôi không thỏa hiệp.',
        p2_en='We are still building. The oven is in, the drawings are done, and '
              'the team is coming together. Everything on this site marked in yellow '
              'is still being confirmed.',
        p2_vi='Chúng tôi vẫn đang hoàn thiện. Lò đã về, bản vẽ đã xong, và đội ngũ '
              'đang dần đầy đủ. Mọi thông tin được đánh dấu vàng trên trang này vẫn '
              'đang được xác nhận.',
        link1=t('Read the story →', 'Đọc câu chuyện →'),
        teasers=teaserhtml,
        bq_en='We would rather do <strong>twelve things properly</strong> than '
              'forty things adequately.',
        bq_vi='Chúng tôi thà làm <strong>mười hai món thật tử tế</strong> còn hơn '
              'bốn mươi món tàm tạm.',
        k2=t('The menu', 'Thực đơn'),
        h2b=t('Short, and it changes.', 'Ngắn gọn, và luôn thay đổi.'),
        p3_en='Antipasti to share, a handful of pizzas, pasta made in-house, '
              'two or three larger plates off the fire, and pudding. '
              'A bar list built around amaro, vermouth and Italian wine.',
        p3_vi='Khai vị để chia sẻ, vài loại pizza, mì tươi làm tại chỗ, hai ba món '
              'chính nướng lửa, và tráng miệng. '
              'Quầy bar xoay quanh amaro, vermouth và rượu vang Ý.',
        cta3=t('See the full menu', 'Xem toàn bộ thực đơn'),
        k3=t('Visit', 'Ghé thăm'),
        h2c=t('Tây Hồ, Hanoi', 'Tây Hồ, Hà Nội'),
        l_where=t('Where', 'Địa chỉ'), l_hours=t('Hours', 'Giờ mở cửa'),
        l_phone=t('Phone', 'Điện thoại'),
        addr_en=ADDRESS_EN, addr_vi=ADDRESS_VI,
        hours=t('Tuesday – Sunday, 17:00 – 23:00', 'Thứ Ba – Chủ Nhật, 17:00 – 23:00'),
        phone=PHONE,
        cta4=t('Book a table', 'Đặt bàn'), maps=MAPS_URL,
        maps_l=t('Open in Google Maps →', 'Mở trong Google Maps →'),
    )

    return page('/', 'home',
        'Sol — Italian-American in Tây Hồ, Hanoi',
        'Sol — Ẩm thực Ý–Mỹ tại Tây Hồ, Hà Nội',
        'Sol is an Italian-American restaurant opening in Tây Hồ, Hanoi in October 2026. '
        'Wood-fired pizza, pasta made in-house, and a bar built around amaro and Italian wine.',
        'Sol là nhà hàng Ý–Mỹ khai trương tại Tây Hồ, Hà Nội vào tháng 10 năm 2026.',
        body, head_extra=SCHEMA)


# ==========================================================================
# MENU
# ==========================================================================
# Each dish: (name_en, name_vi, desc_en, desc_vi, price, tags)
# price is a plain string — put the real number in when you have it.
MENU = [
 ('Antipasti', 'Khai vị',
  'To share, while the oven catches up.',
  'Để chia sẻ, trong lúc chờ lò nóng.',
  [
   ('Focaccia, olive oil, sea salt', 'Focaccia, dầu ô liu, muối biển',
    'Baked to order in the wood oven.', 'Nướng theo yêu cầu trong lò củi.',
    '—', ['v']),
   ('Whipped ricotta, honey, black pepper', 'Ricotta đánh bông, mật ong, tiêu đen',
    'With grilled bread.', 'Ăn kèm bánh mì nướng.', '—', ['v']),
   ('Meatballs, sugo, pecorino', 'Thịt viên, sốt cà chua, pecorino',
    'Beef and pork, slow-cooked in tomato.', 'Bò và heo, om chậm trong cà chua.',
    '—', []),
   ('Chopped salad', 'Salad trộn',
    'Little gem, salami, chickpeas, red onion, oregano.',
    'Xà lách, salami, đậu gà, hành tím, oregano.', '—', []),
   ('Clams, white wine, garlic, chilli', 'Nghêu, rượu vang trắng, tỏi, ớt',
    'Local clams, plenty of bread.', 'Nghêu địa phương, ăn kèm nhiều bánh mì.',
    '—', ['hot']),
  ]),

 ('Pizza', 'Pizza',
  'Naturally leavened dough, fermented 48 hours, cooked in the Pavesi wood oven. '
  'Twelve inches. We do not do half-and-half — sorry.',
  'Bột lên men tự nhiên trong 48 giờ, nướng trong lò củi Pavesi. Đường kính 30 cm. '
  'Chúng tôi không làm nửa nọ nửa kia — mong bạn thông cảm.',
  [
   ('Marinara', 'Marinara',
    'Tomato, garlic, oregano, olive oil. No cheese, and none needed.',
    'Cà chua, tỏi, oregano, dầu ô liu. Không phô mai, và không cần phô mai.',
    '—', ['v']),
   ('Margherita', 'Margherita',
    'Fior di latte, basil, olive oil.', 'Fior di latte, húng quế, dầu ô liu.',
    '—', ['v']),
   ('Diavola', 'Diavola',
    'Spicy salami, fior di latte, chilli honey.',
    'Salami cay, fior di latte, mật ong ớt.', '—', ['hot']),
   ('Quattro formaggi', 'Bốn loại phô mai',
    'Four cheeses, walnut, thyme.', 'Bốn loại phô mai, óc chó, húng tây.',
    '—', ['v']),
   ('The Tây Hồ', 'Tây Hồ',
    'Our house pie — ' + todo('[decide the toppings]') + '.',
    'Pizza đặc trưng của quán — ' + todo('[chọn topping]') + '.',
    '—', ['new']),
   ('Bianca', 'Bianca',
    'No tomato: mozzarella, potato, rosemary, black pepper.',
    'Không cà chua: mozzarella, khoai tây, hương thảo, tiêu đen.', '—', ['v']),
  ]),

 ('Pasta', 'Mì Ý',
  'Made in-house every morning.',
  'Làm tươi mỗi sáng tại nhà hàng.',
  [
   ('Cacio e pepe', 'Cacio e pepe',
    'Pecorino, black pepper, nothing else.', 'Pecorino, tiêu đen, không gì khác.',
    '—', ['v']),
   ('Rigatoni alla vodka', 'Rigatoni sốt vodka',
    'The Italian-American one. Tomato, cream, a little heat.',
    'Món Ý–Mỹ kinh điển. Cà chua, kem, chút cay.', '—', []),
   ('Linguine alle vongole', 'Linguine nghêu',
    'Clams, white wine, parsley.', 'Nghêu, vang trắng, mùi tây.', '—', []),
   ('Lasagne', 'Lasagne',
    'Slow ragù, béchamel, baked to order.',
    'Ragù om chậm, sốt béchamel, nướng theo yêu cầu.', '—', []),
  ]),

 ('From the fire', 'Món nướng lửa',
  'Larger plates, for the middle of the table.',
  'Món lớn, đặt giữa bàn để cùng thưởng thức.',
  [
   ('Whole fish, lemon, oregano', 'Cá nguyên con, chanh, oregano',
    todo('[market fish]') + ', cooked in the oven.',
    todo('[cá theo chợ]') + ', nướng trong lò.', '—', []),
   ('Chicken alla diavola', 'Gà alla diavola',
    'Half chicken, chilli, lemon, roasted hard.',
    'Nửa con gà, ớt, chanh, nướng già lửa.', '—', ['hot']),
   ('Chicken parmigiana', 'Gà parmigiana',
    'Breaded, tomato, mozzarella. The most American thing we make.',
    'Tẩm bột chiên, cà chua, mozzarella. Món Mỹ nhất trong bếp chúng tôi.',
    '—', []),
  ]),

 ('Sides', 'Món phụ', '', '',
  [
   ('Roast potatoes, rosemary', 'Khoai tây nướng, hương thảo', '', '', '—', ['v']),
   ('Greens, garlic, chilli', 'Rau xanh, tỏi, ớt', '', '', '—', ['v']),
   ('Tomato salad', 'Salad cà chua', '', '', '—', ['v']),
  ]),

 ('Dolci', 'Tráng miệng', '', '',
  [
   ('Tiramisù', 'Tiramisù', '', '', '—', []),
   ('Affogato', 'Affogato', 'Vietnamese coffee, vanilla gelato.',
    'Cà phê Việt Nam, kem vani.', '—', []),
   ('Lemon tart', 'Tart chanh', '', '', '—', []),
  ]),

 ('Bar', 'Quầy bar',
  'Amaro, vermouth, and a short Italian wine list that changes. '
  'Ask us what just landed.',
  'Amaro, vermouth và một danh sách vang Ý ngắn, thay đổi thường xuyên. '
  'Hãy hỏi chúng tôi chai nào vừa về.',
  [
   ('Negroni', 'Negroni', '', '', '—', []),
   ('Americano', 'Americano', '', '', '—', []),
   ('Spritz', 'Spritz', 'Aperol, Select, or ' + todo('[house]') + '.',
    'Aperol, Select, hoặc ' + todo('[đặc chế của quán]') + '.', '—', []),
   ('Wine by the glass', 'Vang ly', 'Ask — the list moves.',
    'Hãy hỏi — danh sách luôn thay đổi.', '—', []),
  ]),
]

TAGNAMES = {'v': ('Veg', 'Chay'), 'hot': ('Spicy', 'Cay'), 'new': ('New', 'Mới')}

def build_menu():
    secs = []
    for name_en, name_vi, note_en, note_vi, dishes in MENU:
        rows = []
        for d_en, d_vi, desc_en, desc_vi, price, tags in dishes:
            tag_html = ''
            if tags:
                tag_html = '<span class="tags">' + ''.join(
                    '<span class="tag %s">%s</span>' % (tg, t(*TAGNAMES[tg]))
                    for tg in tags) + '</span>'
            desc = ''
            if desc_en or desc_vi:
                desc = ('<p class="d-desc" data-l="en" lang="en">%s</p>'
                        '<p class="d-desc" data-l="vi" lang="vi">%s</p>' % (desc_en, desc_vi))
            rows.append(
                """      <div class="dish">
        <div class="d-main">
          <p class="d-name">%s%s</p>
          %s
        </div>
        <p class="d-price">%s</p>
      </div>""" % (t(d_en, d_vi), tag_html, desc, todo(price)))
        note = ''
        if note_en or note_vi:
            note = ('<p class="secnote" data-l="en" lang="en">%s</p>'
                    '<p class="secnote" data-l="vi" lang="vi">%s</p>' % (note_en, note_vi))
        secs.append("""    <div class="menusec">
      <h2>%s</h2>
      %s
%s
    </div>""" % (t(name_en, name_vi), note, '\n'.join(rows)))

    body = """<main id="main">
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="standfirst" data-l="en" lang="en">{sf_en}</p>
    <p class="standfirst" data-l="vi" lang="vi">{sf_vi}</p>
  </div>
</section>

<section class="band" style="padding-top:44px">
  <div class="wrap prose">
    <div class="card green" style="margin-bottom:38px">
      <h2 style="margin-top:0;font-size:24px">{warn_h}</h2>
      <p data-l="en" lang="en" style="margin-bottom:0">{warn_en}</p>
      <p data-l="vi" lang="vi" style="margin-bottom:0">{warn_vi}</p>
    </div>
{secs}
    <div class="card">
      <h3 style="margin-top:0">{alg_h}</h3>
      <p data-l="en" lang="en" style="margin-bottom:0">{alg_en}</p>
      <p data-l="vi" lang="vi" style="margin-bottom:0">{alg_vi}</p>
    </div>
    <p style="margin-top:30px"><a class="btn solid" href="/visit/#book">{cta}</a></p>
  </div>
</section>
</main>
""".format(
        eyebrow=t('Menu', 'Thực đơn'),
        h1=t('What we are cooking', 'Chúng tôi nấu gì'),
        sf_en='Short, seasonal, and built around the oven. Everything changes when '
              'the market changes.',
        sf_vi='Ngắn gọn, theo mùa, và xoay quanh chiếc lò. Mọi thứ thay đổi khi chợ '
              'thay đổi.',
        warn_h=t('This menu is a draft', 'Thực đơn này là bản nháp'),
        warn_en='Dishes and prices below are placeholders while we finish the kitchen. '
                'Replace them in <code>build/gen.py</code> (the <code>MENU</code> list) '
                'or directly in this page.',
        warn_vi='Các món và giá bên dưới chỉ là tạm thời trong lúc chúng tôi hoàn thiện '
                'căn bếp.',
        secs='\n'.join(secs),
        alg_h=t('Allergies', 'Dị ứng thực phẩm'),
        alg_en='Please tell your server before you order. Our kitchen handles wheat, '
               'dairy, egg, nuts, shellfish and fish, so we cannot promise a dish is '
               'free of any of them.',
        alg_vi='Vui lòng báo nhân viên trước khi gọi món. Bếp của chúng tôi sử dụng lúa mì, '
               'sữa, trứng, các loại hạt, động vật có vỏ và cá, nên chúng tôi không thể '
               'cam kết món ăn hoàn toàn không chứa các thành phần này.',
        cta=t('Book a table', 'Đặt bàn'),
    )

    return page('/menu/', 'menu',
        'Menu — Sol, Tây Hồ, Hanoi', 'Thực đơn — Sol, Tây Hồ, Hà Nội',
        'Wood-fired pizza, pasta made in-house, antipasti and a bar list built around '
        'amaro and Italian wine. Sol, Tây Hồ, Hanoi.',
        'Pizza lò củi, mì Ý tươi, khai vị và quầy bar với amaro và vang Ý. Sol, Tây Hồ, Hà Nội.',
        body)


# ==========================================================================
# STORY
# ==========================================================================
def build_story():
    body = """<main id="main">
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="standfirst" data-l="en" lang="en">{sf_en}</p>
    <p class="standfirst" data-l="vi" lang="vi">{sf_vi}</p>
  </div>
</section>

<section class="band" style="padding-top:48px">
  <div class="wrap prose">
    <h2>{h2a}</h2>
    <p data-l="en" lang="en">{a1_en}</p>
    <p data-l="vi" lang="vi">{a1_vi}</p>
    <p data-l="en" lang="en">{a2_en}</p>
    <p data-l="vi" lang="vi">{a2_vi}</p>

    <h2 style="margin-top:44px">{h2b}</h2>
    <p data-l="en" lang="en">{b1_en}</p>
    <p data-l="vi" lang="vi">{b1_vi}</p>
    <p data-l="en" lang="en">{b2_en}</p>
    <p data-l="vi" lang="vi">{b2_vi}</p>

    <blockquote class="belief" style="margin-top:40px">
      <p data-l="en" lang="en">{bq_en}</p>
      <p data-l="vi" lang="vi">{bq_vi}</p>
    </blockquote>

    <h2>{h2c}</h2>
    <p data-l="en" lang="en">{c1_en}</p>
    <p data-l="vi" lang="vi">{c1_vi}</p>
  </div>
</section>

<section class="band tint">
  <div class="wrap prose">
    <h2>{h2d}</h2>
    <p data-l="en" lang="en">{d1_en}</p>
    <p data-l="vi" lang="vi">{d1_vi}</p>
    <p><a class="btn solid" href="/jobs/">{cta}</a></p>
  </div>
</section>
</main>
""".format(
        eyebrow=t('Our story', 'Câu chuyện của chúng tôi'),
        h1=t('Closing one thing to build another.', 'Đóng lại một chương để mở ra chương khác.'),
        sf_en='Sol Pizza ran in Tây Hồ until last year. Sol is what we learned from it, '
              'with the space to do it properly.',
        sf_vi='Sol Pizza hoạt động ở Tây Hồ cho đến năm ngoái. Sol là những gì chúng tôi '
              'học được từ đó, với đủ không gian để làm cho tử tế.',
        h2a=t('Sol Pizza', 'Sol Pizza'),
        a1_en='We opened Sol Pizza in Tây Hồ and ran it until we could see, clearly, '
              'what it wanted to become and that the room would not let it. A small '
              'kitchen sets a hard ceiling. So does an oven that is nearly right.',
        a1_vi='Chúng tôi mở Sol Pizza ở Tây Hồ và vận hành cho đến khi nhìn thấy rõ nó '
              'muốn trở thành điều gì — và rằng không gian đó không cho phép. Một căn bếp '
              'nhỏ đặt ra giới hạn cứng. Một chiếc lò gần đúng cũng vậy.',
        a2_en='Closing was the harder decision and the right one. ' + todo('[Add a line here about what closing meant to you and the team.]'),
        a2_vi='Đóng cửa là quyết định khó khăn hơn, và là quyết định đúng. ' + todo('[Thêm một câu về ý nghĩa của việc đóng cửa với bạn và đội ngũ.]'),
        h2b=t('The new building', 'Toà nhà mới'),
        b1_en='Sol takes the first two floors of a building in Tây Hồ — under 200 square '
              'metres of room, which is small enough to run properly and big enough to '
              'do the things the old place could not.',
        b1_vi='Sol chiếm hai tầng đầu của một toà nhà ở Tây Hồ — dưới 200 mét vuông, đủ nhỏ '
              'để vận hành chỉn chu và đủ lớn để làm những điều nơi cũ không thể.',
        b2_en='The centre of it is a Pavesi wood-fired oven, built in Italy, shipped here '
              'and installed this summer. Everything else in the kitchen is arranged '
              'around it.',
        b2_vi='Trung tâm của tất cả là chiếc lò củi Pavesi, chế tác tại Ý, đưa về đây và '
              'lắp đặt trong mùa hè này. Mọi thứ còn lại trong bếp đều được sắp xếp quanh nó.',
        bq_en='A restaurant is a <strong>room, a team and a menu</strong>. Get the room '
              'right and the other two get easier.',
        bq_vi='Một nhà hàng là <strong>một không gian, một đội ngũ và một thực đơn</strong>. '
              'Làm đúng không gian, hai điều còn lại sẽ dễ hơn.',
        h2c=t('The kitchen', 'Căn bếp'),
        c1_en='Ngoc leads the kitchen. ' + todo('[A few lines about Ngoc — where she trained, what she cooks, why she is the right person.]'),
        c1_vi='Ngọc phụ trách bếp. ' + todo('[Vài dòng về Ngọc — học nghề ở đâu, nấu món gì, vì sao là người phù hợp.]'),
        h2d=t('Come and build it with us', 'Cùng chúng tôi dựng nên Sol'),
        d1_en='We are hiring across the kitchen and the floor before we open. If you want '
              'to be part of the first team in the new room, the roles are here.',
        d1_vi='Chúng tôi đang tuyển cho cả bếp và khu phục vụ trước ngày khai trương. Nếu bạn '
              'muốn là một phần của đội ngũ đầu tiên, các vị trí đang mở ở đây.',
        cta=t('See open roles', 'Xem vị trí tuyển dụng'),
    )

    return page('/story/', 'story',
        'Story — Sol, Tây Hồ, Hanoi', 'Câu chuyện — Sol, Tây Hồ, Hà Nội',
        'Sol Pizza closed last year. Sol opens in Tây Hồ, Hanoi in October 2026 — '
        'the same idea, a bigger room and a Pavesi wood-fired oven.',
        'Sol Pizza đã đóng cửa năm ngoái. Sol khai trương tại Tây Hồ, Hà Nội tháng 10 năm 2026.',
        body, ogtype='article')


# ==========================================================================
# VISIT + BOOKING
# ==========================================================================
HOURS = [
    ('Monday', 'Thứ Hai', 'Closed', 'Đóng cửa'),
    ('Tuesday – Sunday', 'Thứ Ba – Chủ Nhật', '17:00 – 23:00', '17:00 – 23:00'),
]

def build_visit():
    hrows = '\n'.join(
        '        <tr><th>%s</th><td>%s</td></tr>' % (
            t(d_en, d_vi),
            t(h_en, h_vi))
        for d_en, d_vi, h_en, h_vi in HOURS)

    body = """<main id="main">
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="standfirst" data-l="en" lang="en">{sf_en}</p>
    <p class="standfirst" data-l="vi" lang="vi">{sf_vi}</p>
  </div>
</section>

<section class="band" style="padding-top:44px" id="book">
  <div class="wrap prose">
    <p class="kicker">{k1}</p>
    <h2>{h2a}</h2>

    <!-- =====================================================================
         RESDIARY BOOKING WIDGET

         1. In ResDiary go to  Promote → Widget configurator  and build your
            widget (colours, logo, party sizes).
         2. Open the Embed Code tab and copy the widget URL out of the code it
            gives you. It looks like:
              https://booking.resdiary.com/widget/Standard/YourVenueName/12345
            (Some accounts are on a different host — use whatever URL ResDiary
            shows you, do not retype this example.)
         3. Paste it between the quotes below and redeploy. That is the only
            change needed — the page swaps the "booking opens soon" panel for
            the live widget automatically.

         Optional extras you can append to the URL:
           ?partySize=2      default number of guests
           ?date=2026-10-05  default date (YYYY-MM-DD, put it first)
           &channelcode=WEB  tags bookings that came from this site
         ===================================================================== -->
    <script>
      window.SOL_RESDIARY_URL = "";   /* ← paste your ResDiary widget URL here */
    </script>

    <div id="rd-mount"></div>

    <noscript>
      <div class="fallback">
        <p style="margin:0">{nojs}</p>
      </div>
    </noscript>

    <p style="font-size:15px;color:var(--ink-soft)" data-l="en" lang="en">{bnote_en}</p>
    <p style="font-size:15px;color:var(--ink-soft)" data-l="vi" lang="vi">{bnote_vi}</p>
  </div>
</section>

<section class="band tint">
  <div class="wrap prose">
    <div class="grid g2">
      <div>
        <h2>{h2b}</h2>
        <table class="hours">
          <caption class="sr-only">{cap}</caption>
          <tbody>
{hrows}
          </tbody>
        </table>
        <p style="font-size:15px;color:var(--ink-soft);margin-top:16px" data-l="en" lang="en">{hnote_en}</p>
        <p style="font-size:15px;color:var(--ink-soft);margin-top:16px" data-l="vi" lang="vi">{hnote_vi}</p>
      </div>
      <div>
        <h2>{h2c}</h2>
        <ul class="contactlist">
          <li><span class="k">{l_addr}</span>
              <span class="v"><span data-l="en" lang="en">{addr_en}</span><span data-l="vi" lang="vi">{addr_vi}</span></span></li>
          <li><span class="k">{l_phone}</span><span class="v">{phone}</span></li>
          <li><span class="k">{l_email}</span><span class="v"><a href="mailto:{email}">{email}</a></span></li>
        </ul>
        <p style="margin-top:20px"><a class="btn solid" href="{maps}" rel="noopener">{maps_l}</a></p>
      </div>
    </div>
  </div>
</section>

<section class="band" style="padding-top:52px">
  <div class="wrap prose">
    <h2>{h2d}</h2>
    <div class="grid g2">
      <div class="card">
        <h3 style="margin-top:0">{g1}</h3>
        <p data-l="en" lang="en" style="margin-bottom:0">{g1_en}</p>
        <p data-l="vi" lang="vi" style="margin-bottom:0">{g1_vi}</p>
      </div>
      <div class="card">
        <h3 style="margin-top:0">{g2}</h3>
        <p data-l="en" lang="en" style="margin-bottom:0">{g2_en}</p>
        <p data-l="vi" lang="vi" style="margin-bottom:0">{g2_vi}</p>
      </div>
      <div class="card">
        <h3 style="margin-top:0">{g3}</h3>
        <p data-l="en" lang="en" style="margin-bottom:0">{g3_en}</p>
        <p data-l="vi" lang="vi" style="margin-bottom:0">{g3_vi}</p>
      </div>
      <div class="card">
        <h3 style="margin-top:0">{g4}</h3>
        <p data-l="en" lang="en" style="margin-bottom:0">{g4_en}</p>
        <p data-l="vi" lang="vi" style="margin-bottom:0">{g4_vi}</p>
      </div>
    </div>
  </div>
</section>

<script>
/* Mount the ResDiary widget if a URL has been configured; otherwise show a
   panel telling people booking is not open yet, so the page never looks broken. */
(function(){{
  var mount = document.getElementById('rd-mount');
  if(!mount) return;
  var url = (window.SOL_RESDIARY_URL || '').trim();
  if(url){{
    var box = document.createElement('div');
    box.className = 'widgetbox';
    var f = document.createElement('iframe');
    f.src = url;
    f.title = 'Book a table at Sol';
    f.setAttribute('allowtransparency','true');
    f.loading = 'lazy';
    f.style.cssText = 'width:100%;border:0;min-height:640px;display:block';
    box.appendChild(f);
    mount.appendChild(box);
    if(window.gtag) gtag('event','booking_widget_shown');
  }} else {{
    mount.innerHTML = {fallback_js};
  }}
}})();
</script>
</main>
""".format(
        eyebrow=t('Visit', 'Ghé thăm'),
        h1=t('Find us, and book a table', 'Tìm chúng tôi và đặt bàn'),
        sf_en='Sol is on the first two floors of a building in Tây Hồ. From October 2026.',
        sf_vi='Sol nằm ở hai tầng đầu của một toà nhà tại Tây Hồ. Từ tháng 10 năm 2026.',
        k1=t('Reservations', 'Đặt bàn'),
        h2a=t('Book a table', 'Đặt bàn'),
        nojs=t('Booking needs JavaScript. Please call us on ' + PHONE + ' or email '
               '<a href="mailto:' + EMAIL + '">' + EMAIL + '</a>.',
               'Chức năng đặt bàn cần JavaScript. Vui lòng gọi ' + PHONE + ' hoặc gửi email tới '
               '<a href="mailto:' + EMAIL + '">' + EMAIL + '</a>.'),
        bnote_en='Tables of seven or more: please email us and we will look after you '
                 'personally.',
        bnote_vi='Nhóm từ bảy người trở lên: vui lòng gửi email, chúng tôi sẽ sắp xếp riêng cho bạn.',
        h2b=t('Hours', 'Giờ mở cửa'), cap=t('Opening hours', 'Giờ mở cửa'),
        hrows=hrows,
        hnote_en='From our opening in October 2026.',
        hnote_vi='Từ khi khai trương vào tháng 10 năm 2026.',
        h2c=t('Contact', 'Liên hệ'),
        l_addr=t('Address', 'Địa chỉ'), l_phone=t('Phone', 'Điện thoại'),
        l_email=t('Email', 'Email'),
        addr_en=ADDRESS_EN, addr_vi=ADDRESS_VI, phone=PHONE, email=EMAIL,
        maps=MAPS_URL, maps_l=t('Open in Google Maps', 'Mở trong Google Maps'),
        h2d=t('Good to know', 'Thông tin hữu ích'),
        g1=t('Getting here', 'Cách di chuyển'),
        g1_en=todo('[Nearest landmark, and roughly how long from the Old Quarter by Grab.]'),
        g1_vi=todo('[Điểm mốc gần nhất và thời gian di chuyển từ Phố cổ bằng Grab.]'),
        g2=t('Parking', 'Gửi xe'),
        g2_en=todo('[Where to leave a motorbike or car.]'),
        g2_vi=todo('[Nơi gửi xe máy hoặc ô tô.]'),
        g3=t('Children', 'Trẻ em'),
        g3_en='Very welcome. High chairs available, and the kitchen will happily make '
              'something plain.',
        g3_vi='Rất hoan nghênh. Có ghế ăn cho bé, và bếp sẵn sàng làm món đơn giản.',
        g4=t('Large groups', 'Nhóm đông'),
        g4_en='We can seat ' + todo('[N]') + ' on the second floor. Email '
              '<a href="mailto:' + EMAIL + '">' + EMAIL + '</a>.',
        g4_vi='Chúng tôi có thể phục vụ ' + todo('[N]') + ' khách ở tầng hai. Email '
              '<a href="mailto:' + EMAIL + '">' + EMAIL + '</a>.',
        fallback_js=repr(
            '<div class="fallback">'
            '<h3><span data-l="en" lang="en">Booking opens soon</span>'
            '<span data-l="vi" lang="vi">Sắp mở đặt bàn</span></h3>'
            '<p data-l="en" lang="en">Online reservations open closer to our October '
            'opening. Until then, email <a href="mailto:' + EMAIL + '">' + EMAIL + '</a> '
            'and we will hold you a table on the first week.</p>'
            '<p data-l="vi" lang="vi">Đặt bàn trực tuyến sẽ mở gần ngày khai trương '
            'tháng 10. Trong thời gian này, hãy gửi email tới '
            '<a href="mailto:' + EMAIL + '">' + EMAIL + '</a> và chúng tôi sẽ giữ bàn '
            'cho bạn trong tuần đầu tiên.</p>'
            '<p style="margin-bottom:0"><a class="btn solid" href="mailto:' + EMAIL + '">'
            '<span data-l="en" lang="en">Email us</span>'
            '<span data-l="vi" lang="vi">Gửi email</span></a></p>'
            '</div>').replace("'", '"', 0),
    )

    return page('/visit/', 'visit',
        'Visit & book — Sol, Tây Hồ, Hanoi', 'Ghé thăm & đặt bàn — Sol, Tây Hồ, Hà Nội',
        'Address, opening hours and table reservations for Sol in Tây Hồ, Hanoi. '
        'Opening October 2026.',
        'Địa chỉ, giờ mở cửa và đặt bàn tại Sol, Tây Hồ, Hà Nội. Khai trương tháng 10 năm 2026.',
        body, head_extra=SCHEMA)



# ==========================================================================
# CAREERS — /jobs/
# The listing is built from ROLES below. The three role pages that were
# already live are re-wrapped in the site shell with their content untouched
# (build/../src/jobs/*.html is the source of truth for that copy).
# To open a new role: add it to ROLES, drop its detail page in src/jobs/,
# rebuild. To close one: status='filled', filled_en/filled_vi.
# ==========================================================================
ROLES = [
    dict(slug='restaurant-accountant', src='restaurant-accountant.html',
         name_en='Restaurant Accountant', name_vi='Kế toán nhà hàng',
         sub_en='Sol & ASU House Bakery', sub_vi='Sol & ASU House Bakery',
         blurb_en='Own the finance function across Sol and ASU House Bakery. '
                  'You are the finance function, not one seat in a large team.',
         blurb_vi='Phụ trách toàn bộ tài chính của Sol và ASU House Bakery. '
                  'Bạn chính là bộ phận tài chính, không phải một ghế trong một đội lớn.',
         pay='20,000,000 VND', extra_en='→ Finance Manager', extra_vi='→ Trưởng phòng Tài chính',
         status='open'),
    dict(slug='sous-chef', src='sous-chef.html',
         name_en='Sous Chef', name_vi='Bếp phó',
         sub_en='Pizza & Kitchen Operations', sub_vi='Pizza & vận hành bếp',
         blurb_en='Own the dough programme and run the wood-fired oven alongside the '
                  'Head Chef, leading 4–5 line cooks.',
         blurb_vi='Phụ trách chương trình bột và vận hành lò củi cùng Bếp trưởng, '
                  'dẫn dắt 4–5 đầu bếp.',
         pay='18,000,000 VND', extra_en='2–4M service charge + 10% KPI bonus',
         extra_vi='2–4 triệu phí phục vụ + 10% thưởng KPI',
         status='filled', filled_en='September 2026', filled_vi='tháng 9 năm 2026'),
    dict(slug='restaurant-supervisor', src='restaurant-supervisor.html',
         name_en='Restaurant Supervisor', name_vi='Giám sát nhà hàng',
         sub_en='Front of house', sub_vi='Khu phục vụ',
         blurb_en='Full ownership of the dining room and bar — the floor, the team, '
                  'the budget and the guest experience.',
         blurb_vi='Toàn quyền phụ trách phòng ăn và quầy bar — sàn, đội ngũ, ngân sách '
                  'và trải nghiệm khách.',
         pay='16,000,000 VND', extra_en='2–4M service charge + 10% KPI bonus',
         extra_vi='2–4 triệu phí phục vụ + 10% thưởng KPI',
         status='filled', filled_en='September 2026', filled_vi='tháng 9 năm 2026'),
]

BENEFITS = [
    ('A share of the venue’s 5% service charge and tip pool, paid quarterly, for the floor and kitchen roles.',
     'Một phần trong 5% phí phục vụ và quỹ tip của nhà hàng, trả hàng quý, cho các vị trí phục vụ và bếp.'),
    ('A 13th-month bonus according to company KPIs, and an annual salary review based on performance.',
     'Thưởng tháng 13 theo KPI công ty, và xét tăng lương hàng năm theo hiệu quả công việc.'),
    ('Full statutory insurance — BHXH, BHYT, BHTN — from the day your labour contract starts.',
     'Đầy đủ bảo hiểm theo luật — BHXH, BHYT, BHTN — từ ngày hợp đồng lao động bắt đầu.'),
    ('12 days paid annual leave a year, plus one extra day for every 3 years of service, subject to company policy.',
     '12 ngày nghỉ phép có lương mỗi năm, cộng thêm một ngày cho mỗi 3 năm làm việc, theo chính sách công ty.'),
    ('11 paid public holidays a year including Tết. Holiday work is paid at statutory premium rates.',
     '11 ngày nghỉ lễ có lương mỗi năm, bao gồm Tết. Làm việc ngày lễ được trả theo mức phụ trội luật định.'),
    ('A funded WSET Level 3 or Certified Sommelier qualification after 12 months, for the floor team.',
     'Được tài trợ chứng chỉ WSET Level 3 hoặc Certified Sommelier sau 12 tháng, cho đội phục vụ.'),
    ('A staff meal cooked by our kitchen before dinner service, and a discount across Sol and ASU House Bakery.',
     'Bữa ăn nhân viên do bếp nấu trước ca tối, và ưu đãi giảm giá tại Sol và ASU House Bakery.'),
]


def _rolecard(r):
    if r['status'] == 'open':
        return """      <a class="rolecard" href="/jobs/%(slug)s.html">
        <div class="rc-head"><h3>%(name)s</h3><p class="rc-sub">%(sub)s</p></div>
        <p class="rc-blurb" data-l="en" lang="en">%(blurb_en)s</p>
        <p class="rc-blurb" data-l="vi" lang="vi">%(blurb_vi)s</p>
        <p class="rc-pay">%(pay)s</p>
        <p class="rc-extra">%(extra)s</p>
        <span class="rc-go">%(go)s</span>
      </a>""" % dict(slug=r['slug'], name=t(r['name_en'], r['name_vi']),
                     sub=t(r['sub_en'], r['sub_vi']), blurb_en=r['blurb_en'],
                     blurb_vi=r['blurb_vi'], pay=r['pay'],
                     extra=t(r['extra_en'], r['extra_vi']),
                     go=t('View role →', 'Xem vị trí →'))


def build_jobs():
    open_roles = [r for r in ROLES if r['status'] == 'open']
    filled = [r for r in ROLES if r['status'] == 'filled']

    cards = '\n'.join(_rolecard(r) for r in open_roles)
    cards += """
      <div class="rolecard team">
        <div class="rc-head"><h3>%s</h3><p class="rc-sub">%s</p></div>
        <p class="rc-blurb" data-l="en" lang="en">%s</p>
        <p class="rc-blurb" data-l="vi" lang="vi">%s</p>
        <p class="rc-extra" data-l="en" lang="en">%s</p>
        <p class="rc-extra" data-l="vi" lang="vi">%s</p>
        <span class="rc-go"><a href="mailto:jobs@sol.pizza?subject=Opening%%20team%%20%%E2%%80%%94%%20">%s</a></span>
      </div>""" % (
        t('Opening team — floor and kitchen', 'Đội ngũ khai trương — phục vụ và bếp'),
        t('Hiring now for our October opening', 'Tuyển ngay cho khai trương tháng 10'),
        'Servers, bartenders, baristas, line cooks and kitchen porters for the first team '
        'in the new room. The Restaurant Supervisor and Head Chef are finalising each role; '
        'send us a CV now and we will come back to you as they open.',
        'Nhân viên phục vụ, pha chế, barista, đầu bếp và phụ bếp cho đội ngũ đầu tiên trong '
        'không gian mới. Giám sát nhà hàng và Bếp trưởng đang hoàn thiện từng vị trí; hãy gửi CV '
        'ngay và chúng tôi sẽ liên hệ lại khi các vị trí mở.',
        todo('[Long / Ngọc: list each role here with pay and hours once decided]'),
        todo('[Long / Ngọc: liệt kê từng vị trí kèm lương và giờ làm khi đã chốt]'),
        t('Email jobs@sol.pizza →', 'Gửi email tới jobs@sol.pizza →'))

    filledhtml = '\n'.join(
        '      <li><a href="/jobs/%s.html">%s<span class="st">%s</span></a></li>' % (
            r['slug'], t(r['name_en'], r['name_vi']),
            t('Filled ' + r['filled_en'], 'Đã tuyển ' + r['filled_vi']))
        for r in filled)

    benefits = '\n'.join(
        '      <li><span data-l="en" lang="en">%s</span><span data-l="vi" lang="vi">%s</span></li>' % b
        for b in BENEFITS)

    body = """<main id="main">
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="standfirst" data-l="en" lang="en">{sf_en}</p>
    <p class="standfirst" data-l="vi" lang="vi">{sf_vi}</p>
  </div>
</section>

<section class="band" style="padding-top:48px">
  <div class="wrap prose">
    <p class="kicker">{k1}</p>
    <h2>{h2a}</h2>
    <div class="rolegrid">
{cards}
    </div>
    <p class="kicker" style="margin-top:34px">{k2}</p>
    <ul class="filledlist">
{filled}
    </ul>
  </div>
</section>

<section class="band tint">
  <div class="wrap prose">
    <p class="kicker">{k3}</p>
    <h2>{h2b}</h2>
    <p class="lede" data-l="en" lang="en">{a1_en}</p>
    <p class="lede" data-l="vi" lang="vi">{a1_vi}</p>
    <p data-l="en" lang="en">{a2_en}</p>
    <p data-l="vi" lang="vi">{a2_vi}</p>
    <p data-l="en" lang="en">{a3_en}</p>
    <p data-l="vi" lang="vi">{a3_vi}</p>
  </div>
</section>

<section class="band">
  <div class="wrap prose">
    <h2>{h2c}</h2>
    <ul class="benefits">
{benefits}
    </ul>
  </div>
</section>

<section class="band olive" id="apply">
  <div class="wrap prose">
    <h2>{h2d}</h2>
    <p data-l="en" lang="en">{ap_en}</p>
    <p data-l="vi" lang="vi">{ap_vi}</p>
    <p><a class="btn" href="mailto:jobs@sol.pizza">{cta}</a></p>
    <p style="font-size:14px;margin-top:22px;color:rgba(249,233,211,.85)">
      <a href="/privacy/">{priv_en}</a> · <a href="/privacy/#vi">{priv_vi}</a></p>
  </div>
</section>
</main>
""".format(
        eyebrow=t('We are hiring · Tây Hồ, Hanoi', 'Tuyển dụng · Tây Hồ, Hà Nội'),
        h1=t('Come and build the new Sol', 'Cùng xây dựng Sol mới'),
        sf_en='We open this October. The kitchen and the floor are being hired now, '
              'and every application gets a reply.',
        sf_vi='Chúng tôi khai trương tháng 10 này. Bếp và khu phục vụ đang tuyển ngay bây giờ, '
              'và mọi hồ sơ đều nhận được phản hồi.',
        k1=t('Open roles', 'Vị trí đang tuyển'),
        h2a=t('Where we need you', 'Chúng tôi cần bạn ở đâu'),
        cards=cards,
        k2=t('Recently filled', 'Vừa tuyển xong'),
        filled=filledhtml,
        k3=t('About Sol', 'Về Sol'),
        h2b=t('A new chapter, the same standards.', 'Một chương mới, cùng một tiêu chuẩn.'),
        a1_en='Sol is starting a new chapter this year — a new home, a refreshed brand and a '
              'growing team — while staying focused on what has always mattered most to us: '
              'great food, made with high-quality ingredients.',
        a1_vi='Năm nay Sol bắt đầu một chương mới — một ngôi nhà mới, thương hiệu được làm mới '
              'và đội ngũ đang lớn dần — trong khi vẫn tập trung vào điều luôn quan trọng nhất với '
              'chúng tôi: món ăn ngon, làm từ nguyên liệu chất lượng cao.',
        a2_en='Based in Tây Hồ, Sol is a modern American-Italian restaurant with pizza at its '
              'heart, paired with a carefully selected wine list and a warm, relaxed atmosphere.',
        a2_vi='Đặt tại Tây Hồ, Sol là nhà hàng Mỹ–Ý hiện đại với pizza làm trung tâm, đi cùng '
              'danh sách rượu vang được chọn lọc kỹ và không gian ấm áp, thư giãn.',
        a3_en='As we prepare to open the new space, we are looking for people who care about '
              'good food, genuine hospitality, and doing things well.',
        a3_vi='Khi chuẩn bị mở không gian mới, chúng tôi tìm những người quan tâm đến món ăn ngon, '
              'lòng hiếu khách chân thành, và làm mọi việc cho tử tế.',
        h2c=t('What you get, whichever role you take', 'Quyền lợi, dù bạn ở vị trí nào'),
        benefits=benefits,
        h2d=t('How to apply', 'Cách ứng tuyển'),
        ap_en='Send your CV to <a href="mailto:jobs@sol.pizza">jobs@sol.pizza</a> with the role '
              'name in the subject line. Each role page lists exactly what to include. We review '
              'applications within 5 working days and reply to every applicant — including the '
              'ones we cannot take forward.',
        ap_vi='Gửi CV tới <a href="mailto:jobs@sol.pizza">jobs@sol.pizza</a> với tên vị trí ở dòng '
              'tiêu đề. Mỗi trang vị trí ghi rõ cần gửi những gì. Chúng tôi xem xét hồ sơ trong '
              '5 ngày làm việc và trả lời mọi ứng viên — kể cả những người chúng tôi không thể '
              'tiếp tục.',
        cta=t('Email jobs@sol.pizza', 'Gửi email tới jobs@sol.pizza'),
        priv_en='Applicant privacy notice', priv_vi='Thông báo bảo mật ứng viên',
    )

    page('/jobs/', 'jobs',
         'Careers at Sol — Tây Hồ, Hanoi', 'Tuyển dụng tại Sol — Tây Hồ, Hà Nội',
         'Sol is hiring in Tây Hồ, Hanoi ahead of its October opening: Restaurant Accountant, '
         'plus the opening floor and kitchen team.',
         'Sol đang tuyển dụng tại Tây Hồ, Hà Nội trước khai trương tháng 10: Kế toán nhà hàng '
         'và đội ngũ phục vụ, bếp.',
         body, body_attrs=' data-page="index"', sticky='jobs')

    for r in ROLES:
        _rewrap_role(r, open_roles)


def _rewrap_role(r, open_roles):
    """Put an existing role page inside the site shell without touching its copy."""
    h = open(os.path.join(SRC, 'jobs', r['src']), encoding='utf-8').read()
    hero = re.search(r'<div class="hero"><div class="wrap">(.*?)</div></div>\s*<main', h, re.S).group(1)
    inner = re.search(r'<main><div class="wrap">(.*?)</div></main>', h, re.S).group(1)
    title = re.search(r'<title>(.*?)</title>', h, re.S).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h).group(1)

    # Stale deadline fact and the "other openings" block go on every page.
    hero = re.sub(r'<div><dt>Closes</dt><dd>[^<]*</dd></div>', '', hero)
    inner = re.sub(r'<div class="others">.*?</div></div>', '', inner, flags=re.S)

    filled = r['status'] == 'filled'
    if filled:
        # a start date is stale once the role is filled
        hero = re.sub(r'<div><dt>Starts</dt><dd>[^<]*</dd></div>', '', hero)
        hero = hero.replace('</dl>', '<div><dt>%s</dt><dd>%s</dd></div></dl>' % (
            t('Status', 'Trạng thái'), t('Filled, ' + r['filled_en'], 'Đã tuyển, ' + r['filled_vi'])))
        hero = re.sub(r'<div><a class="btn" href="#apply">.*?</a></div>', '', hero, flags=re.S)
        inner = re.sub(r'<section class="apply" id="apply">.*?</section>', '', inner, flags=re.S)
        bar = ('<div class="filledbar"><div class="wrap">'
               '<span data-l="en" lang="en">This role was filled in %s. The description stays '
               'here for reference.</span>'
               '<span data-l="vi" lang="vi">Vị trí này đã tuyển xong vào %s. Mô tả được giữ lại '
               'để tham khảo.</span>'
               '<a href="/jobs/">%s</a></div></div>\n') % (
                   r['filled_en'], r['filled_vi'], t('See open roles →', 'Xem vị trí đang tuyển →'))
        robots = '<meta name="robots" content="noindex,follow">'
        page_attr = 'role-filled'
        sticky = 'none'
    else:
        hero = hero.replace('</dl>', '<div><dt>%s</dt><dd>%s</dd></div></dl>' % (
            t('Applications', 'Ứng tuyển'), t('Open — reviewed as they arrive', 'Đang mở — xét duyệt liên tục')))
        inner = inner.replace(
            '<p><strong>Applications close 3 September 2026</strong></p>',
            '<p><strong>' + t('Applications are open and reviewed as they arrive.',
                              'Hồ sơ đang được nhận và xét duyệt liên tục.') + '</strong></p>')
        bar = ''
        robots = ''
        page_attr = 'role'
        sticky = 'apply'

    vi_note = ('<p class="vi-note" data-l="vi" lang="vi">Bản mô tả công việc này hiện chỉ có '
               'bằng tiếng Anh. Bạn có thể ứng tuyển bằng tiếng Việt hoặc tiếng Anh.</p>\n')

    body = ('<main id="main" class="role">\n' + bar +
            '<section class="hero role"><div class="wrap">' + hero + '</div></section>\n'
            '<div class="wrap prose" style="padding-top:44px">\n' + vi_note + inner +
            '\n</div>\n</main>\n')

    page('/jobs/%s.html' % r['slug'], r['slug'], title, title, desc, desc, body,
         head_extra=robots,
         body_attrs=' data-page="%s" data-role="%s" data-slug="%s"' % (page_attr, r['name_en'], r['slug']),
         out=os.path.join(DIST, 'jobs', r['slug'] + '.html'), nav_path='/jobs/',
         og='%s/jobs/og-%s.png' % (SITE, r['slug']), sticky=sticky)


# ==========================================================================
# SUPPORT FILES
# ==========================================================================
def build_support():
    pages = ['/', '/menu/', '/story/', '/visit/', '/jobs/'] + \
            ['/jobs/%s.html' % r['slug'] for r in ROLES if r['status'] == 'open']
    urls = []
    for p in pages:
        pri = '1.0' if p == '/' else ('0.9' if p in ('/menu/', '/visit/') else '0.6')
        urls.append(
            '  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority>\n'
            '    <xhtml:link rel="alternate" hreflang="en" href="%s%s"/>\n'
            '    <xhtml:link rel="alternate" hreflang="vi" href="%s%s?lang=vi"/>\n'
            '  </url>' % (SITE, p, TODAY, pri, SITE, p, SITE, p))
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
               '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
               + '\n'.join(urls) + '\n</urlset>\n')
    open(os.path.join(DIST, 'sitemap.xml'), 'w').write(sitemap)

    open(os.path.join(DIST, 'robots.txt'), 'w').write(
        'User-agent: *\nAllow: /\nDisallow: /privacy/\n\nSitemap: %s/sitemap.xml\n' % SITE)

    # The apex now has a real homepage, so the old /  ->  /jobs/ rule must go.
    open(os.path.join(DIST, '_redirects'), 'w').write(
        '# The apex now serves the real homepage — the old rule that pointed /\n'
        '# at /jobs/index.html has been removed.\n'
        '/careers      /jobs/        301\n'
        '/careers/*    /jobs/:splat  301\n'
        '/book         /visit/#book  301\n'
        '/reservations /visit/#book  301\n'
        '/menu.html    /menu/        301\n')

    # 404
    body404 = """<main id="main">
<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow">404</p>
    <h1>{h1}</h1>
    <p class="standfirst" data-l="en" lang="en">{p_en}</p>
    <p class="standfirst" data-l="vi" lang="vi">{p_vi}</p>
    <p style="margin-top:26px"><a class="btn" href="/">{cta}</a></p>
  </div>
</section>
</main>
""".format(
        h1=t('That page is not on the menu.', 'Trang này không có trong thực đơn.'),
        p_en='The link may be old, or we may have moved something. Try the menu, or go home.',
        p_vi='Có thể liên kết đã cũ, hoặc chúng tôi đã chuyển trang. Hãy thử thực đơn, hoặc quay về trang chủ.',
        cta=t('Back to the homepage', 'Về trang chủ'))
    doc = HEAD_TPL.format(title_en='Page not found — Sol', title_vi='Không tìm thấy trang — Sol',
                          desc_en='Page not found.', desc_vi='Không tìm thấy trang.',
                          site=SITE, path='/404.html', slug='home', ogtype='website',
                          ga=GA_ID, fbpix=FB_PIX, head_extra='<meta name="robots" content="noindex">',
                          body_attrs=' data-page="404"', og=SITE + '/og-home.png')
    doc += header('/404') + body404 + footer()
    open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8').write(doc)


def copy_existing():
    """Carry the already-live sections across untouched."""
    # /privacy/ is carried across untouched. /jobs/ is rebuilt by build_jobs()
    # from the original role pages, so only their OG images come across here.
    shutil.copytree(os.path.join(SRC, 'privacy'), os.path.join(DIST, 'privacy'), dirs_exist_ok=True)
    os.makedirs(os.path.join(DIST, 'jobs'), exist_ok=True)
    for f in os.listdir(os.path.join(SRC, 'jobs')):
        if f.endswith('.png'):
            shutil.copy2(os.path.join(SRC, 'jobs', f), os.path.join(DIST, 'jobs', f))
    for f in ('favicon.svg', 'pixel.js'):
        if os.path.exists(os.path.join(SRC, f)):
            shutil.copy2(os.path.join(SRC, f), os.path.join(DIST, f))
    os.makedirs(os.path.join(DIST, 'assets'), exist_ok=True)
    shutil.copy2(os.path.join(HERE, 'sol.css'),   os.path.join(DIST, 'assets', 'sol.css'))
    shutil.copy2(os.path.join(HERE, 'fonts.css'), os.path.join(DIST, 'assets', 'fonts.css'))
    shutil.copy2(os.path.join(HERE, 'sol.js'),    os.path.join(DIST, 'assets', 'sol.js'))
    shutil.copytree(os.path.join(HERE, 'fonts'), os.path.join(DIST, 'assets', 'fonts'),
                    dirs_exist_ok=True)
    # share cards, rendered by og.js into build/og/png
    for f in os.listdir(os.path.join(HERE, 'og', 'png')):
        shutil.copy2(os.path.join(HERE, 'og', 'png', f), os.path.join(DIST, f))


# ==========================================================================
# OPTIMISE
# CSS and JS are minified and given content-hashed filenames so Cloudflare can
# cache them for a year; the HTML is left readable and is served with
# must-revalidate, so a redeploy is picked up straight away. OG images are
# palette-quantised (they are flat brand colours, so this is lossless to the
# eye and roughly a third of the size).
# ==========================================================================
import hashlib, subprocess, json as _json

def _hash(b): return hashlib.sha1(b).hexdigest()[:8]

def optimise():
    assets = os.path.join(DIST, 'assets')
    node = os.path.join(ROOT, 'node_modules')
    rename = {}

    # --- CSS via csso, then inlined into every page ----------------------------
    # One fewer render-blocking round trip per page view. The readable source
    # stays in build/sol.css and build/fonts.css; edit there and rebuild.
    css_min = b''
    for name in ('fonts', 'sol'):
        src = os.path.join(assets, name + '.css')
        css = open(src, encoding='utf-8').read()
        css_min += subprocess.run(['node', '-e',
            'const c=require(process.argv[1]);let s="";process.stdin.on("data",d=>s+=d)'
            '.on("end",()=>process.stdout.write(c.minify(s,{comments:false}).css))',
            os.path.join(node, 'csso')], input=css.encode(), capture_output=True, check=True).stdout
        os.remove(src)
    inline_css = '<style>' + css_min.decode('utf-8') + '</style>'

    # --- JS via terser -----------------------------------------------------
    for path, key in ((os.path.join(assets, 'sol.js'), '/assets/sol.js'),
                      (os.path.join(DIST, 'pixel.js'), None)):
        js = open(path, encoding='utf-8').read()
        out = subprocess.run(['node', os.path.join(node, 'terser', 'bin', 'terser'),
                              '--compress', '--mangle', '--comments', 'false'],
                             input=js.encode(), capture_output=True, check=True).stdout
        if key:
            h = _hash(out); new = 'sol.%s.js' % h
            open(os.path.join(assets, new), 'wb').write(out); os.remove(path)
            rename[key] = '/assets/' + new
        else:
            open(path, 'wb').write(out)

    # --- rewrite references in every HTML file --------------------------------
    for root, _, files in os.walk(DIST):
        for f in files:
            if not f.endswith('.html'): continue
            fp = os.path.join(root, f)
            h = open(fp, encoding='utf-8').read()
            for a, b in rename.items(): h = h.replace(a, b)
            h = h.replace('<link rel="stylesheet" href="/assets/fonts.css">\n'
                          '<link rel="stylesheet" href="/assets/sol.css">', inline_css)
            open(fp, 'w', encoding='utf-8').write(h)

    # --- OG images: quantise -----------------------------------------------------
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

    # --- _headers: caching, security, early hints ------------------------------
    open(os.path.join(DIST, '_headers'), 'w').write("""# Cloudflare Pages headers.
# HTML: always revalidate, so a redeploy shows up immediately.
# /assets: content-hashed filenames, cached for a year.
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Cache-Control: public, max-age=0, must-revalidate
  Link: </assets/fonts/be-vietnam-pro-latin-400-normal.woff2>; rel=preload; as=font; crossorigin, </assets/fonts/eb-garamond-latin-600-normal.woff2>; rel=preload; as=font; crossorigin

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
""")

# ==========================================================================
# BOOTSTRAP — make a clean checkout buildable
# Fonts come from the @fontsource npm packages (npm ci), share-card PNGs
# from build/assets.b64.json (a text manifest, see build/pack_assets.py).
# Nothing binary needs to live in git.
# ==========================================================================
import base64, json as _json0

FONT_PLAN = {
    'eb-garamond':    {'family': 'EB Garamond',    'weights': [400, 600],      'subsets': ['latin', 'latin-ext', 'vietnamese']},
    'be-vietnam-pro': {'family': 'Be Vietnam Pro', 'weights': [400, 600, 700], 'subsets': ['latin', 'latin-ext', 'vietnamese']},
}

def ensure_fonts():
    """Copy the needed woff2 files out of node_modules and write build/fonts.css."""
    fd = os.path.join(HERE, 'fonts'); os.makedirs(fd, exist_ok=True)
    nm = os.path.join(ROOT, 'node_modules', '@fontsource')
    if not os.path.isdir(nm):
        if os.path.exists(os.path.join(HERE, 'fonts.css')) and os.listdir(fd):
            return  # already have a font set from an earlier run
        raise SystemExit('fonts: run `npm ci` first (needs @fontsource/eb-garamond and @fontsource/be-vietnam-pro)')
    css = []
    for pkg, cfg in FONT_PLAN.items():
        uni = _json0.load(open(os.path.join(nm, pkg, 'unicode.json')))
        for sub in cfg['subsets']:
            for w in cfg['weights']:
                fn = '%s-%s-%s-normal.woff2' % (pkg, sub, w)
                shutil.copy2(os.path.join(nm, pkg, 'files', fn), os.path.join(fd, fn))
                css.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;\n"
                           "  src:url('/assets/fonts/%s') format('woff2');\n  unicode-range:%s;}" % (cfg['family'], w, fn, uni[sub]))
    open(os.path.join(HERE, 'fonts.css'), 'w').write(
        "/* Self-hosted webfonts, generated by build/gen.py from the @fontsource packages.\n"
        "   Split by unicode-range so a browser only downloads the Vietnamese block when\n"
        "   it has Vietnamese text to draw. */\n" + '\n'.join(css) + '\n')

def unpack_assets():
    m = _json0.load(open(os.path.join(HERE, 'assets.b64.json')))
    for rel, b64 in m.items():
        out = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if not os.path.exists(out):
            open(out, 'wb').write(base64.b64decode(b64))



if __name__ == '__main__':
    ensure_fonts()
    unpack_assets()
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    copy_existing()
    for fn in (build_home, build_menu, build_story, build_visit):
        print('wrote', fn())
    build_jobs(); print('wrote /jobs/')
    build_support()
    print('wrote support files')
    optimise()
    print('optimised')
