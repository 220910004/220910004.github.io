# furkanis.me kaynak dosyaları

Site bu klasörden üretilir. `main` dalına yapılan her kayıttan sonra GitHub Actions (`.github/workflows/yayinla.yml`) `build.py`'yi çalıştırır ve sonucu yayımlar. Repo kökündeki eski üretilmiş dosyalar artık kullanılmıyor.

## Yeni yazı eklemek

1. `_kaynak/posts/` klasöründe **Add file › Create new file**.
2. Dosya adı: `yazinin-adresi.md` (küçük harf, Türkçe karakter yok, boşluk yerine tire).
3. `_sablon.md` dosyasındaki bilgi bloğunu kopyala, doldur, `draft: false` yap.
4. **Commit changes**. Bir iki dakika sonra yazı furkanis.me/yazilar/ altında yayında olur.

Bilgi bloğundaki alanlar: `title`, `slug` (adres), `date` (YYYY-AA-GG), `lang` (tr/en), `summary`, isteğe bağlı `seo_title` ve `updated`, `draft` (true ise yayımlanmaz).
Görseller: `_kaynak/static/yazilar/gorsel/` içine koy, yazıda `![açıklama](/yazilar/gorsel/dosya.png)` diye kullan.

## Klasörler

- `furkan-ozel.html` — ana sayfanın kaynağı (TR ve EN birlikte)
- `build.py` — siteyi `site/` klasörüne üretir
- `posts/` — yazılar (alt çizgiyle başlayan dosyalar yayımlanmaz)
- `static/` — olduğu gibi kopyalanan dosyalar: CNAME, CV PDF'leri, paylaşım görseli
- `logos/`, `fontsrc/` — logo ve font kaynakları (fontlar SIL Open Font License)
- `og_card.py`, `make_assets.py` — paylaşım görselini ve CV PDF'lerini yeniden üretmek için (yerelde, Playwright gerekir)
