import os
from playwright.sync_api import sync_playwright
from PIL import Image
os.makedirs('site/cv', exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={'width':1200,'height':630}); pg.goto('http://localhost:8766/_og.html'); pg.wait_for_timeout(600)
    pg.screenshot(path='site/og.png')
    for lang,url in [('tr','/'),('en','/en/')]:
        pg=b.new_page(); pg.goto('http://localhost:8766'+url); pg.wait_for_timeout(2200)
        pg.emulate_media(media='print')
        pg.pdf(path=f'site/cv/mustafa-furkan-ozel-cv-{lang}.pdf', format='A4', print_background=True, prefer_css_page_size=True)
    b.close()
Image.open('site/og.png').convert('RGB').save('site/og.png', optimize=True)
os.remove('site/_og.html')
