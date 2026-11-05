# furkanis.me kaynak dosyaları

Bu klasör sitenin düzenlenebilir kaynağıdır. Yayındaki dosyalar (repo kökündeki index.html, en/, cv/ vb.) buradan üretilir.
Klasör adı alt çizgiyle başladığı için GitHub Pages bunu yayımlamaz.

- `furkan-ozel.html` — sitenin tek kaynak sayfası (TR ve EN metinler birlikte)
- `build.py` — siteyi `site/` klasörüne üretir (fontları küçültür, /en/ sayfasını, yazıları, RSS'i ve site haritasını oluşturur)
- `og_card.py`, `make_assets.py` — paylaşım görselini ve CV PDF'lerini üretir
- `posts/` — yazılar buraya Markdown olarak eklenir (biçim `build.py` başında anlatılıyor)
- `logos/`, `fontsrc/` — logo ve font kaynakları (fontlar SIL Open Font License)

Gerekenler: Python 3, `pip install fonttools brotli markdown pillow playwright`
Üretim: `python3 build.py`, ardından paylaşım görseli ve PDF'ler için yerel sunucu açıp `og_card.py` ve `make_assets.py`.
