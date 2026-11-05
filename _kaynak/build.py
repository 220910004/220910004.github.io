"""Build furkanis.me from furkan-ozel.html (the editable source) into site/.

Writing: add a Markdown file to posts/ with a front matter block, e.g.

    ---
    title: SAP2000 modellerini Python ile kurmak
    slug: sap2000-python
    date: 2026-11-20
    lang: tr
    summary: COM/OAPI arayüzüyle GES modellerini koddan üretmek.
    draft: false
    ---
    Yazının gövdesi Markdown olarak...

Analytics: leave both empty to ship no tracking code. On Cloudflare Pages you can
also turn on Web Analytics in the dashboard without any code here.
"""
CF_BEACON_TOKEN = ''      # Cloudflare Web Analytics token
GOATCOUNTER_CODE = ''     # e.g. 'furkanis' for furkanis.goatcounter.com

import re, json, os, glob, base64, shutil, datetime, html as H
import markdown
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset as fsub
from PIL import Image, ImageDraw

SITE = 'https://furkanis.me'
TODAY = datetime.date.today().isoformat()
MON = {'tr': ['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara'],
       'en': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']}

src = open('furkan-ozel.html', encoding='utf-8').read()
json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', src, re.S).group(1))
open('chk.js', 'w').write('\n;\n'.join(re.findall(r'<script>(.*?)</script>', src, re.S)))

for f in glob.glob('logos/*.webp'):
    src = src.replace("logo:'%s'" % f, "logo:'data:image/webp;base64,%s'" % base64.b64encode(open(f, 'rb').read()).decode())
src = src.replace('href="cv/', 'href="/cv/').replace('href="yazilar/"', 'href="/yazilar/"').replace('href="yazilar/rss.xml', 'href="/yazilar/rss.xml')
shutil.rmtree('site/logos', ignore_errors=True)

# ---------- posts ----------
def parse_post(path):
    raw = open(path, encoding='utf-8').read().replace('\r\n', '\n').lstrip('\ufeff')
    m = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S)
    if not m:
        raise SystemExit('HATA %s: dosya "---" satırlarıyla başlayan bilgi bloğuyla başlamalı.' % path)
    meta = {k: v.strip() for k, v in re.findall(r'^(\w+):[ \t]*(.*)$', m.group(1), re.M)}
    for key in ('title', 'slug', 'date', 'summary'):
        if not meta.get(key):
            raise SystemExit('HATA %s: "%s" satırı eksik ya da boş.' % (path, key))
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', meta['date']):
        raise SystemExit('HATA %s: tarih YYYY-AA-GG biçiminde olmalı, örneğin 2026-11-20.' % path)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', meta['slug']):
        raise SystemExit('HATA %s: slug yalnızca küçük harf, rakam ve tire içermeli (Türkçe karakter olmadan), örneğin rüzgar-yuku değil ruzgar-yuku.' % path)
    meta['draft'] = meta.get('draft', 'false').strip().lower() == 'true'
    meta['body_md'] = m.group(2)
    meta['lang'] = meta.get('lang', 'tr').strip()
    meta['words'] = len(re.findall(r'\w+', m.group(2)))
    return meta
posts = sorted([p for p in (parse_post(f) for f in sorted(glob.glob('posts/*.md')) if not os.path.basename(f).startswith('_')) if not p['draft']],
               key=lambda p: p['date'], reverse=True)

def fdate(d, lang):
    y, m, dd = d.split('-'); return '%d %s %s' % (int(dd), MON[lang][int(m)-1], y)

def card(p):
    mins = max(1, round(p['words'] / 200))
    rt = ('%d dk' % mins) if p['lang'] == 'tr' else ('%d min' % mins)
    return ('        <li class="post"><a class="post-link" href="/yazilar/%s/" hreflang="%s">\n'
            '          <span class="post-meta"><time datetime="%s">%s</time> · %s · %s</span>\n'
            '          <span class="post-title" lang="%s">%s</span>\n'
            '          <span class="post-sum" lang="%s">%s</span>\n'
            '        </a></li>\n') % (p['slug'], p['lang'], p['date'], fdate(p['date'], p['lang']), rt,
                                       p['lang'].upper(), p['lang'], H.escape(p['title']), p['lang'], H.escape(p['summary']))

if posts:
    src = re.sub(r'<!--POSTS:CARDS-->.*?<!--/POSTS:CARDS-->', ''.join(card(p) for p in posts), src, flags=re.S)
else:
    src = re.sub(r'\s*<!--POSTS:START-->.*?<!--POSTS:END-->', '', src, flags=re.S)
src = src.replace('<!--POSTS:START-->', '').replace('<!--POSTS:END-->', '')
# lang spans on post cards must not be hidden by the page language switch
src = src.replace('/* writing carousel */', '/* writing carousel */\n.post [lang]{display:revert !important}', 1) if posts else src

head, body = src.split('<div class="wrap">', 1)
head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
main_style = re.search(r'<style>\n/\* Layout.*?</style>', head, re.S).group(0)

# ---------- fonts ----------
post_text = ' '.join(p['title'] + ' ' + p['summary'] + ' ' + p['body_md'] for p in posts)
text = H.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', body, flags=re.S))) + post_text
chars = set(text) | set(chr(c) for c in range(32, 127)) | set('—–·’‘“”…°×ğĞşŞıİöÖüÜçÇâÂîû←→')
chars |= set('OcaŞubMarNisMayHazTemAğuEylEkiKasAraJanFebAprJunJulAugSepOctNovDecbugüntodayyılayyrsmo0123456789')
chars |= set('Tolerans dışı Aradığınız sayfa bu adreste yok Ana sayfaya dön Out of tolerance There is no page at this address Back to the home page')
os.makedirs('site/fonts', exist_ok=True)
def make(srcf, out, axes=None):
    f = TTFont('fontsrc/' + srcf, lazy=False)
    o = fsub.Options(); o.flavor = 'woff2'; o.layout_features = ['*']; o.name_IDs = ['*']; o.notdef_outline = True
    s_ = fsub.Subsetter(o); s_.populate(text=''.join(chars)); s_.subset(f)
    if axes: f = instancer.instantiateVariableFont(f, axes)
    f.flavor = 'woff2'; f.save('site/fonts/' + out)
    return os.path.getsize('site/fonts/' + out)
print({
 'archivo': make('Archivo-VF.ttf', 'archivo.woff2', {'wdth': (68, 85), 'wght': (500, 760)}),
 'plex-sans': make('PlexSans-VF.ttf', 'plex-sans.woff2', {'wdth': 100, 'wght': (400, 500)}),
 'mono-400': make('IBMPlexMono-Regular.ttf', 'plex-mono-400.woff2'),
 'mono-500': make('IBMPlexMono-Medium.ttf', 'plex-mono-500.woff2'),
})
fontcss = ('<link rel="preload" href="/fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>\n'
 '<link rel="preload" href="/fonts/plex-sans.woff2" as="font" type="font/woff2" crossorigin>\n'
 '<link rel="preload" href="/fonts/plex-mono-400.woff2" as="font" type="font/woff2" crossorigin>\n'
 '<style>\n'
 '@font-face{font-family:"Archivo";src:url(/fonts/archivo.woff2) format("woff2");font-weight:500 760;font-stretch:68% 85%;font-style:normal;font-display:swap}\n'
 '@font-face{font-family:"IBM Plex Sans";src:url(/fonts/plex-sans.woff2) format("woff2");font-weight:400 500;font-style:normal;font-display:swap}\n'
 '@font-face{font-family:"IBM Plex Mono";src:url(/fonts/plex-mono-400.woff2) format("woff2");font-weight:400;font-style:normal;font-display:swap}\n'
 '@font-face{font-family:"IBM Plex Mono";src:url(/fonts/plex-mono-500.woff2) format("woff2");font-weight:500;font-style:normal;font-display:swap}\n'
 '</style>\n')
head = re.sub(r'<link rel="preconnect"[^>]*>\n<link rel="preconnect"[^>]*>\n<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', fontcss, head, count=1)
assert 'fonts.googleapis' not in head

# ---------- icons + manifest ----------
INK, MARK, PAPER = (21, 24, 27), (226, 176, 0), (236, 238, 234)
def icon_png(size, pad):
    im = Image.new('RGB', (size, size), PAPER if pad else INK); d = ImageDraw.Draw(im)
    o = int(size * pad); s = size - 2 * o
    d.rectangle([o, o, o + s - 1, o + s - 1], fill=INK)
    d.rectangle([o + int(s * .5625), o + int(s * .6875), o + s - 1, o + s - 1], fill=MARK)
    return im
icon_png(180, .0).save('site/apple-touch-icon.png', optimize=True)
icon_png(192, .0).save('site/icon-192.png', optimize=True)
icon_png(512, .12).save('site/icon-512.png', optimize=True)
open('site/favicon.svg', 'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#15181B"/><rect x="18" y="22" width="14" height="10" fill="#E2B000"/></svg>\n')
json.dump({'name': 'Mustafa Furkan Özel', 'short_name': 'MFÖ', 'start_url': '/', 'display': 'browser',
           'background_color': '#ECEEEA', 'theme_color': '#ECEEEA',
           'icons': [{'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                     {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'}]},
          open('site/site.webmanifest', 'w'), ensure_ascii=False, indent=1)
ICONS = ('<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
         '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
         '<link rel="manifest" href="/site.webmanifest">\n'
         '<link rel="alternate" type="application/rss+xml" title="furkanis.me · Yazılar" href="/yazilar/rss.xml">\n')

ANALYTICS = ''
if CF_BEACON_TOKEN:
    ANALYTICS += '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token": "%s"}\'></script>\n' % CF_BEACON_TOKEN
if GOATCOUNTER_CODE:
    ANALYTICS += '<script data-goatcounter="https://%s.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>\n' % GOATCOUNTER_CODE

def doc(lang, h, b, site_attr=True):
    return ('<!doctype html>\n<html lang="%s" data-lang="%s"%s>\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="theme-color" content="#ECEEEA" media="(prefers-color-scheme: light)">\n'
            '<meta name="theme-color" content="#111315" media="(prefers-color-scheme: dark)">\n'
            % (lang, lang, ' data-site="1"' if site_attr else '')) + ICONS + h + '</head>\n<body>\n' + b + ANALYTICS + '</body>\n</html>\n'

# ---------- home pages ----------
os.makedirs('site/en', exist_ok=True)
open('site/index.html', 'w', encoding='utf-8').write(doc('tr', head, '<div class="wrap">' + body + '\n'))
en_head = head
for a, b in [
 (r'<title>.*?</title>', '<title>Mustafa Furkan Özel | Mechanical Engineer · Ankara</title>'),
 (r'<meta name="description" content=".*?">', '<meta name="description" content="Mechanical engineer in Ankara, Türkiye: structural calculations, steel structure design, solar mounting systems, FEA and CFD in ANSYS, SAP2000 and Python automation.">'),
 (r'<link rel="canonical" href=".*?">', '<link rel="canonical" href="https://furkanis.me/en/">'),
 (r'<meta property="og:url" content=".*?">', '<meta property="og:url" content="https://furkanis.me/en/">'),
 (r'<meta property="og:title" content=".*?">', '<meta property="og:title" content="Mustafa Furkan Özel | Mechanical Engineer · Ankara">'),
 (r'<meta property="og:description" content=".*?">', '<meta property="og:description" content="Mechanical engineer and Ph.D. student at Gazi University. Structural calculations, steel structures, solar projects, FEA and CFD.">'),
 (r'<meta property="og:locale" content="tr_TR">\n<meta property="og:locale:alternate" content="en_US">', '<meta property="og:locale" content="en_US">\n<meta property="og:locale:alternate" content="tr_TR">'),
]:
    en_head, n = re.subn(a, b, en_head, count=1, flags=re.S); assert n == 1, a
open('site/en/index.html', 'w', encoding='utf-8').write(doc('en', en_head, '<div class="wrap">' + body + '\n'))

# ---------- shared bits for sub-pages ----------
SUB_CSS = '''<style>
.sub-bar a{text-decoration:none}
.article{padding-block:3rem 2.5rem; border-bottom:1px solid var(--rule)}
.article .eyebrow{margin:0}
.article h1{font-family:var(--f-display); font-stretch:72%; font-weight:720; font-size:clamp(2.1rem,6vw,3.3rem); line-height:1.02; margin:.7rem 0 1rem; text-wrap:balance; max-width:22ch}
.dek{font-size:var(--s-3); color:var(--ink-2); max-width:52ch; margin:0}
.prose{margin-top:2.4rem; font-size:1.04rem; line-height:1.72; max-width:42rem}
.prose > *{max-width:65ch}
.prose h2{font-family:var(--f-display); font-stretch:85%; font-weight:650; font-size:1.4rem; line-height:1.25; margin:2.4rem 0 .7rem}
.prose h3{font-family:var(--f-display); font-stretch:85%; font-weight:650; font-size:1.1rem; margin:1.8rem 0 .5rem}
.prose p,.prose ul,.prose ol{margin:0 0 1.05rem}
.prose li{margin-bottom:.3rem}
.prose code{font-family:var(--f-mono); font-size:.86em; padding:.05em .3em; box-shadow:inset 0 0 0 1px var(--rule)}
.prose pre{max-width:100%; overflow-x:auto; margin:0 0 1.2rem; padding:1rem 1.1rem; box-shadow:inset 0 0 0 1px var(--rule); font:.84rem/1.6 var(--f-mono)}
.prose pre code{box-shadow:none; padding:0; font-size:inherit}
.prose img{max-width:100%; height:auto}
.prose blockquote{margin:0 0 1.1rem; padding-left:1rem; box-shadow:inset 2px 0 0 var(--mark); color:var(--ink-2)}
.prose table{border-collapse:collapse; display:block; overflow-x:auto; font-size:.92rem; margin-bottom:1.2rem}
.prose th,.prose td{border-bottom:1px solid var(--rule); padding:.45rem .8rem .45rem 0; text-align:left; vertical-align:top}
.related{padding-block:2.2rem; border-bottom:1px solid var(--rule)}
.related h2{margin:0 0 1rem}
.rel-list{list-style:none; margin:0; padding:0; display:grid; gap:0}
.rel-list li{border-top:1px solid var(--rule)}
.rel-list li:first-child{border-top-color:var(--ink)}
.rel-list a{display:grid; grid-template-columns:7.5rem minmax(0,1fr); gap:.2rem 1.2rem; padding:.8rem 0; text-decoration:none; min-height:24px}
.rel-list time{font-family:var(--f-mono); font-size:var(--s-0); color:var(--ink-2); padding-top:.2rem; font-variant-numeric:tabular-nums}
.rel-list span{font-family:var(--f-display); font-stretch:85%; font-weight:650; font-size:var(--s-2); line-height:1.3}
.rel-list a:hover span{text-decoration:underline; text-decoration-color:var(--mark); text-decoration-thickness:2px; text-underline-offset:.2em}
.rel-more{display:inline-flex; margin-top:1rem; font-family:var(--f-mono); font-size:var(--s-0); min-height:24px; align-items:center}
@media (max-width: 560px){ .rel-list a{grid-template-columns:1fr} }
.back{font-family:var(--f-mono); font-size:var(--s-0); display:inline-flex; min-height:24px; align-items:center}
.nf{padding-block:4.5rem 4rem; border-bottom:1px solid var(--rule)}
.nf .big404{font-family:var(--f-display); font-stretch:68%; font-weight:760; font-size:clamp(6rem,24vw,11rem); line-height:.85; margin:.6rem 0 1.4rem}
.nf p{font-size:var(--s-3); max-width:40ch; margin:0 0 .4rem}
.nf .en{font-size:var(--s-1); color:var(--ink-2)}
.nf .back{margin-top:1.6rem; font-size:var(--s-1)}
.nf [lang],.prose [lang],.article [lang]{display:revert !important}
</style>
'''
def sub_head(title, desc, canonical, lang, extra=''):
    return ('<title>%s</title>\n<meta name="description" content="%s">\n' % (H.escape(title), H.escape(desc))
            + ('<link rel="canonical" href="%s">\n' % canonical if canonical else '<meta name="robots" content="noindex">\n')
            + extra + fontcss + main_style + '\n' + SUB_CSS)
def sub_bar(lang):
    home = '/' if lang == 'tr' else '/en/'
    label = 'Ana sayfa' if lang == 'tr' else 'Home'
    return ('<header class="bar sub-bar"><a class="site" href="%s">furkanis.me</a>'
            '<a class="back" href="%s">← %s</a></header>\n') % (home, home, label)
FOOT = ('<footer class="foot"><span>Mustafa Furkan Özel</span>'
        '<span>furkanis.me · Ankara, Türkiye</span></footer>\n')

# ---------- post pages ----------
def related(p):
    others = [q for q in posts if q['slug'] != p['slug']]
    others.sort(key=lambda q: (q['lang'] != p['lang'], ''.join(chr(255 - ord(c)) for c in q['date'])))
    others = others[:3]
    tr = p['lang'] == 'tr'
    home = '/' if tr else '/en/'
    more = ('<a class="rel-more" href="/yazilar/">%s</a>' % ('Tüm yazılar →' if tr else 'All writing →'))
    if not others:
        return '<section class="related">%s</section>\n' % more
    items = ''.join('<li><a href="/yazilar/%s/" hreflang="%s"><time datetime="%s">%s</time><span lang="%s">%s</span></a></li>'
                    % (q['slug'], q['lang'], q['date'], fdate(q['date'], q['lang']), q['lang'], H.escape(q['title'])) for q in others)
    return ('<section class="related" aria-labelledby="rel-h"><h2 class="label" id="rel-h">%s</h2><ul class="rel-list">%s</ul>%s</section>\n'
            % ('Diğer yazılar' if tr else 'More writing', items, more))

shutil.rmtree('site/yazilar', ignore_errors=True)
for p in posts:
    lang = p['lang']; url = '%s/yazilar/%s/' % (SITE, p['slug'])
    content = markdown.markdown(p['body_md'], extensions=['fenced_code', 'tables', 'sane_lists'])
    faq = []
    fm = re.search(r'^## (?:Sık sorulan sorular|Frequently asked questions)\s*\n(.*?)(?=^## |\Z)', p['body_md'], re.S | re.M)
    if fm:
        for q, ans in re.findall(r'^### (.+?)\n+(.+?)(?=^### |\Z)', fm.group(1), re.S | re.M):
            plain = re.sub(r'[`*_]|\[([^\]]*)\]\([^)]*\)', lambda m_: m_.group(1) or '', ans).strip()
            faq.append({'@type': 'Question', 'name': q.strip(), 'acceptedAnswer': {'@type': 'Answer', 'text': plain}})
    ld = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'wordCount': p['words'], 'headline': p['title'], 'description': p['summary'],
          'datePublished': p['date'], 'dateModified': p.get('updated', p['date']), 'inLanguage': lang,
          'mainEntityOfPage': url, 'image': SITE + '/og.png',
          'author': {'@type': 'Person', '@id': SITE + '/#person', 'name': 'Mustafa Furkan Özel', 'url': SITE + '/'}}
    if faq:
        ld = {'@context': 'https://schema.org', '@graph': [dict(ld, **{'@context': None}), {'@type': 'FAQPage', 'mainEntity': faq}]}
        ld['@graph'][0].pop('@context')
    extra = ('<meta property="og:type" content="article">\n<meta property="og:url" content="%s">\n'
             '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n'
             '<meta property="og:image" content="%s/og.png">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
             '<meta property="article:published_time" content="%s">\n<meta name="twitter:card" content="summary_large_image">\n'
             '<script type="application/ld+json">%s</script>\n') % (url, H.escape(p['title']), H.escape(p['summary']), SITE,
                                                                     p['date'], json.dumps(ld, ensure_ascii=False))
    mins = max(1, round(p['words'] / 200))
    meta_line = '%s · %s' % (fdate(p['date'], lang), ('%d dk okuma' % mins) if lang == 'tr' else ('%d min read' % mins))
    page_body = ('<div class="wrap">\n' + sub_bar(lang) +
                 '<main><article class="article">\n<p class="eyebrow"><time datetime="%s">%s</time></p>\n<h1>%s</h1>\n<p class="dek">%s</p>\n'
                 '<div class="prose">\n%s\n</div>\n</article>\n%s</main>\n' % (p['date'], meta_line, H.escape(p['title']), H.escape(p['summary']), content, related(p))
                 + FOOT + '</div>\n')
    os.makedirs('site/yazilar/' + p['slug'], exist_ok=True)
    open('site/yazilar/%s/index.html' % p['slug'], 'w', encoding='utf-8').write(
        doc(lang, sub_head('%s | Mustafa Furkan Özel' % p.get('seo_title', p['title']), p['summary'], url, lang, extra), page_body, site_attr=False))

# ---------- writing index ----------
if posts:
    li = ''.join('<li><a href="/yazilar/%s/" hreflang="%s"><time datetime="%s">%s</time><span lang="%s">%s<em>%s</em></span></a></li>'
                 % (q['slug'], q['lang'], q['date'], fdate(q['date'], q['lang']), q['lang'], H.escape(q['title']), H.escape(q['summary'])) for q in posts)
    ix_ld = {'@context': 'https://schema.org', '@type': 'Blog', 'name': 'furkanis.me · Yazılar', 'url': SITE + '/yazilar/', 'inLanguage': 'tr',
             'author': {'@type': 'Person', '@id': SITE + '/#person', 'name': 'Mustafa Furkan Özel', 'url': SITE + '/'},
             'blogPost': [{'@type': 'BlogPosting', 'headline': q['title'], 'url': '%s/yazilar/%s/' % (SITE, q['slug']), 'datePublished': q['date']} for q in posts]}
    ix_extra = ('<meta property="og:type" content="website">\n<meta property="og:url" content="%s/yazilar/">\n'
                '<meta property="og:title" content="Yazılar | Mustafa Furkan Özel">\n<meta property="og:image" content="%s/og.png">\n'
                '<meta name="twitter:card" content="summary_large_image">\n<script type="application/ld+json">%s</script>\n'
                '<style>.ix .rel-list span em{display:block; font-style:normal; font-family:var(--f-body); font-weight:400; font-size:var(--s-1); color:var(--ink-2); margin-top:.3rem; line-height:1.5}</style>\n'
                ) % (SITE, SITE, json.dumps(ix_ld, ensure_ascii=False))
    ix_body = ('<div class="wrap">\n' + sub_bar('tr') +
               '<main><header class="article"><p class="eyebrow">Yazılar · %d</p><h1>Mühendislik notları</h1>'
               '<p class="dek">Yapısal tasarım, sayısal analiz ve mühendislik otomasyonu üzerine sahadan notlar.</p></header>\n'
               '<section class="related ix"><ul class="rel-list">%s</ul><a class="rel-more" href="/yazilar/rss.xml">RSS ile takip et</a></section></main>\n'
               % (len(posts), li) + FOOT + '</div>\n')
    os.makedirs('site/yazilar', exist_ok=True)
    open('site/yazilar/index.html', 'w', encoding='utf-8').write(doc('tr', sub_head(
        'Yazılar | Mustafa Furkan Özel', 'Mustafa Furkan Özel\'in yapısal tasarım, SAP2000, sonlu elemanlar ve Python ile mühendislik otomasyonu üzerine yazıları.',
        SITE + '/yazilar/', 'tr', ix_extra), ix_body, site_attr=False))

# ---------- RSS ----------
from email.utils import format_datetime
def rfc822(d): return format_datetime(datetime.datetime.strptime(d, '%Y-%m-%d').replace(hour=9, tzinfo=datetime.timezone(datetime.timedelta(hours=3))))
os.makedirs('site/yazilar', exist_ok=True)
items = ''
for p in posts:
    url = '%s/yazilar/%s/' % (SITE, p['slug'])
    body_html = markdown.markdown(p['body_md'], extensions=['fenced_code', 'tables', 'sane_lists'])
    items += ('  <item>\n    <title>%s</title>\n    <link>%s</link>\n    <guid isPermaLink="true">%s</guid>\n'
              '    <pubDate>%s</pubDate>\n    <dc:creator>Mustafa Furkan Özel</dc:creator>\n    <dc:language>%s</dc:language>\n'
              '    <description>%s</description>\n    <content:encoded><![CDATA[%s]]></content:encoded>\n  </item>\n'
              % (H.escape(p['title']), url, url, rfc822(p['date']), p['lang'], H.escape(p['summary']), body_html.replace(']]>', ']]&gt;')))
last = rfc822(posts[0]['date']) if posts else format_datetime(datetime.datetime.now(datetime.timezone.utc))
open('site/yazilar/rss.xml', 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
    '<channel>\n  <title>furkanis.me · Yazılar</title>\n  <link>%s/</link>\n'
    '  <atom:link href="%s/yazilar/rss.xml" rel="self" type="application/rss+xml"/>\n'
    '  <description>Mustafa Furkan Özel: yapısal tasarım, sayısal analiz ve mühendislik otomasyonu üzerine yazılar.</description>\n'
    '  <language>tr</language>\n  <lastBuildDate>%s</lastBuildDate>\n%s</channel>\n</rss>\n' % (SITE, SITE, last, items))

# ---------- 404 ----------
nf_body = ('<div class="wrap">\n' + sub_bar('tr') +
           '<main class="nf">\n<p class="eyebrow">Tolerans dışı · Out of tolerance</p>\n<p class="big404">404</p>\n'
           '<p>Aradığınız sayfa bu adreste yok.</p>\n<p class="en" lang="en">There is no page at this address.</p>\n'
           '<a class="back" href="/">← Ana sayfaya dön</a> <a class="back" href="/en/" lang="en">· Back to the home page</a>\n</main>\n'
           + FOOT + '</div>\n')
open('site/404.html', 'w', encoding='utf-8').write(
    doc('tr', sub_head('Sayfa bulunamadı | furkanis.me', 'Bu adreste bir sayfa yok.', None, 'tr'), nf_body, site_attr=False))

# ---------- robots + sitemap ----------
open('site/robots.txt', 'w').write('User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE)
alt = ('      <xhtml:link rel="alternate" hreflang="tr" href="%s/"/>\n      <xhtml:link rel="alternate" hreflang="en" href="%s/en/"/>\n'
       '      <xhtml:link rel="alternate" hreflang="x-default" href="%s/"/>\n') % (SITE, SITE, SITE)
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
for u in [SITE + '/', SITE + '/en/']:
    sm += '  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n%s  </url>\n' % (u, TODAY, alt)
if posts:
    sm += '  <url>\n    <loc>%s/yazilar/</loc>\n    <lastmod>%s</lastmod>\n  </url>\n' % (SITE, posts[0].get('updated', posts[0]['date']))
for p in posts:
    sm += '  <url>\n    <loc>%s/yazilar/%s/</loc>\n    <lastmod>%s</lastmod>\n  </url>\n' % (SITE, p['slug'], p.get('updated', p['date']))
open('site/sitemap.xml', 'w').write(sm + '</urlset>\n')
# ---------- static files (CNAME, CV PDFs, share image, post images) ----------
if os.path.isdir('static'):
    shutil.copytree('static', 'site', dirs_exist_ok=True)
print('built', len(posts), 'posts')
