---
title: SAP2000'de Kararsızlık Uyarısı: Nedenleri ve Adım Adım Çözümü
slug: sap2000-kararsizlik-uyarisi
date: 2026-11-05
lang: tr
seo_title: SAP2000 Kararsızlık (Instability) Uyarısı Nasıl Çözülür?
summary: SAP2000'deki instability, lost digits of accuracy ve negative stiffness uyarılarının anlamı, en sık nedenleri ve sorunlu düğümü bulup modeli düzeltmenin adımları.
draft: false
---
**Kısaca:** SAP2000'deki kararsızlık (instability) uyarısı, modelin bir kısmının yüke direnecek rijitliğe sahip olmadığını ya da birbirinden çok farklı rijitlikteki elemanların aynı noktada birleştiğini gösterir. En sık nedenler; çubuk uçlarına fazla serbestlik (release) verilmesi, eksik veya hatalı mesnetler, birbirine bağlanmamış düğümler ve aşırı rijit elemanlardır. Sorunlu noktayı bulmanın en hızlı yolu, çözücüyü "Standard Solver" yapıp hangi düğüm ve serbestlik derecesinin (DOF) sorun çıkardığını okumak ve ardından modal analizde çok uzun periyotlu modlara bakmaktır.

Bu uyarı göz ardı edildiğinde analiz çoğu zaman yine biter ve sonuç verir. Ama o sonuçlar güvenilir değildir. Bu yazıda uyarının ne dediğini, nereden kaynaklandığını ve modeli adım adım nasıl düzelteceğinizi anlatıyorum.

## SAP2000 kararsızlık uyarısı ne anlama gelir?

SAP2000, rijitlik denklemlerini 16 basamaklı sayılarla çözer. Model kötü koşullandırılmışsa (ill-conditioned) ya da bir kısmı mekanizma gibi davranıyorsa, çözüm sırasında bu basamakların bir kısmı kaybolur. Analiz penceresinde gördüğünüz "lost digits of accuracy" ifadesi bu kaybı anlatır.

CSI'nin kendi açıklamasına göre Standard Solver kullanıldığında:

| Kaybedilen basamak | SAP2000'in davranışı | Ne yapmalı? |
|---|---|---|
| 6'dan az | Raporlanmaz | Sorun yok |
| 6 ile 11 arası | Bilgi olarak raporlanır | Sonuçları dikkatle kontrol edin |
| 11'den fazla | Kararsızlık uyarısı verilir | Model ya kararsız ya kötü koşullandırılmış; düzeltilmeli |

Analiz özetindeki **negatif rijitlik özdeğeri (negative stiffness eigenvalue)** sayısı da sıfır olmalıdır. Sıfırdan farklıysa model kararsızdır, kötü koşullandırılmıştır ya da P-delta etkisiyle burkulmaktadır.

## Uyarıyı nerede görürüm?

- **Analiz penceresi (Analysis Monitor):** Analiz sırasında mesajlar burada akar.
- **Analyze › Show Last Run Details:** Son analizin mesajlarını yeniden gösterir.
- **.LOG dosyası:** Bütün mesajlar model klasöründeki `.LOG` uzantılı metin dosyasına da yazılır; herhangi bir metin düzenleyiciyle açılabilir.

## Sorunlu düğümü nasıl bulurum?

Varsayılan çözücü (Advanced Solver) yalnızca "önemli sayıda basamak kaybedildi" der, yerini söylemez. Bu yüzden ilk adım çözücüyü değiştirmektir.

1. **Çözücüyü Standard Solver yapın.** Analyze menüsündeki çözücü seçeneklerinden (Advanced SapFire Options) Standard Solver'ı seçip analizi yeniden çalıştırın. Bu çözücü, her denklem için kaybedilen basamak sayısını ve ilgili **düğüm adı ile serbestlik derecesini** (U1, U2, U3, R1, R2, R3) raporlar.
2. **Serbestlik derecesine bakın.** Uyarı R1, R2 ya da R3 gibi bir dönme serbestliğini gösteriyorsa sorun büyük olasılıkla çubuk uç serbestliklerindedir. U1, U2 ya da U3 gibi bir öteleme serbestliğini gösteriyorsa mesnetlere, bağlantılara ve stabilite elemanlarına (çaprazlar) bakın.
3. **Modal analiz yapın.** İlk 10-12 modu inceleyin. Mekanizmalar ve rijit cisim hareketleri, **çok uzun periyotlu** modlar olarak ortaya çıkar; mod şekli sorunlu bölgeyi gösterir.
4. **Deforme şekle bakın.** Ölü yük altındaki deforme şekilde, çevresine göre aşırı yer değiştiren bir düğüm ya da eleman sorunun kaynağıdır. Şekil zor seçiliyorsa düğüm yer değiştirme tablosunu büyükten küçüğe sıralayın.
5. **P-delta'yı geçici olarak kapatın.** Uyarı yalnızca P-delta açıkken çıkıyorsa sorun model kurgusunda değil, gerçek bir burkulma eğilimindedir.

## En sık 6 neden ve çözümü

### 1. Çubuk uçlarında fazla serbestlik (release)

En yaygın nedendir. Bir düğüme bağlanan bütün çubuklarda aynı moment serbestliği bırakılırsa o düğümün dönmesine hiçbir şey direnmez. Bir çubuğun iki ucunda da burulma (T) serbest bırakılırsa çubuk kendi ekseni etrafında serbestçe dönebilir.

**Çözüm:** Her düğümde en az bir çubuğun ilgili serbestlik derecesinde sürekli kalmasını sağlayın. Mafsallı çaprazlarda burulmayı yalnızca bir uçta serbest bırakın. Kafes sistemlerde bütün çubukları iki ucu mafsallı tanımlamak yerine, düğüm dönmelerini mesnetle tutmayı ya da sürekli bir başlık elemanı kullanmayı düşünün.

### 2. Eksik ya da hatalı mesnetler

Kolon altları mafsallı, kolon-kiriş birleşimleri de mafsallıysa ve çapraz yoksa çerçeve yatayda mekanizmadır. Düzlem bir çerçeveyi üç boyutlu modelde düzlem dışı tutmadan çözmek de aynı sonucu verir.

**Çözüm:** Yatay yük taşıyıcı sistemin (çaprazlar, rijit birleşimler ya da ankastre mesnetler) her iki doğrultuda da tanımlı olduğunu kontrol edin. Düzlem bir çerçeve çözüyorsanız analiz seçeneklerinde kullanılabilir serbestlik derecelerini düzleme göre sınırlayın.

### 3. Mesnet ve yay atamalarının çakışması

Zemin-yapı etkileşimini yaylarla modellerken aynı düğüme hem mesnet hem yay atamak ya da yayı yalnızca bazı düğümlere uygulamak sık görülür. Kendi bir GES projemde, kayaya soketli kazıkları yatay yaylarla modellerken ısrarla süren kararsızlık uyarılarının kaynağı tam olarak buydu: üst üste binen mesnet atamaları ve bölünmüş kazık elemanlarının bütün parçalarına uygulanmamış yaylar.

**Çözüm:** Her düğümde bir serbestlik derecesini ya mesnetle ya yayla tanımlayın, ikisini birlikte değil. Eleman analiz için parçalara bölündüyse yayların bütün ara düğümlere uygulandığını kontrol edin. Kazık başında dönme serbestliklerinin nasıl tutulduğuna ayrıca karar verin; bu, sık atlanan bir noktadır.

### 4. Birbirine bağlanmamış düğümler ve öksüz elemanlar

İki çubuğun ucu ekranda birleşmiş gibi görünür ama koordinatları bir milimetre farklıdır. SAP2000 bunları ayrı düğüm sayar ve eleman boşta kalır. Ayrıca birleştirme toleransı (auto merge tolerance) çok küçükse beklenen bağlantılar kurulmaz.

**Çözüm:** Modal analizde birbirinden bağımsız ve ters fazda hareket eden elemanları arayın. Düğüm koordinatlarını tablo halinde kontrol edin ve birleştirme toleransının modelinizin ölçeğine uygun olduğundan emin olun.

### 5. Aşırı rijit elemanlar

"Rijit olsun" diye elastisite modülü milyonlarla çarpılmış bir bağlantı çubuğu, çevresindeki normal elemanlarla aynı denklemde çözüldüğünde ciddi basamak kaybına yol açar.

**Çözüm:** Rijitliği gerçekçi bir mertebede tutun; çevresindeki elemanların 100 ila 1000 katı genellikle yeterlidir. Gerçekten rijit bir bağlantı gerekiyorsa sayıları şişirmek yerine SAP2000'in kısıt (constraint) ya da rijit bölge (end offset) seçeneklerini kullanın.

### 6. Eksik stabilite elemanları

Döngülerle ya da kopyalama ile üretilen modellerde bazı çaprazların hiç oluşturulmaması ya da yanlış kesitle tanımlanması yaygındır. Model kâğıt üzerinde stabildir ama bilgisayardaki hali değildir.

**Çözüm:** Çapraz sayısını ve kesit atamalarını beklenen değerle karşılaştırın. Modeli Python ile üretiyorsanız bu sayımı koda ekleyin (aşağıda örnek var).

## Kontrolü Python ile otomatikleştirmek

Model büyüdükçe serbestlikleri tek tek ekranda kontrol etmek zorlaşır. SAP2000 OAPI ile bütün çubukları tarayıp iki ucunda burulması serbest bırakılmış olanları birkaç satırda listeleyebilirsiniz. Bağlantı kurmayı bilmiyorsanız önce [SAP2000 modelini Python ile kurmak](/yazilar/sap2000-python-api/) yazısına bakın.

```python
# SapModel: açık SAP2000 modeline bağlı nesne
sayi, cubuklar, ret = SapModel.FrameObj.GetNameList(0, [])

sorunlu = []
for ad in cubuklar:
    bas, son, bas_deger, son_deger, ret = SapModel.FrameObj.GetReleases(ad, [], [], [], [])
    # Sıra: P, V2, V3, T, M2, M3  ->  3. indeks burulma (T)
    if bas[3] and son[3]:
        sorunlu.append(ad)

print(f"{sayi} çubuktan {len(sorunlu)} tanesinde burulma iki uçta da serbest:")
print(", ".join(sorunlu) or "yok")
```

Aynı yaklaşımla mesnet atanmış düğümleri (`PointObj.GetRestraint`), yay atanmış düğümleri (`PointObj.GetSpring`) ya da belirli bir kesite sahip çubuk sayısını da listeleyip çakışmaları analizden önce yakalayabilirsiniz.

## Analizden önce kontrol listesi

- Her düğümde, her serbestlik derecesinde en az bir eleman ya da mesnet rijitlik sağlıyor mu?
- Hiçbir çubukta burulma iki uçta birden serbest değil mi?
- Yatay yük taşıyıcı sistem iki doğrultuda da tanımlı mı?
- Aynı düğüme hem mesnet hem yay atanmamış mı?
- Bölünmüş elemanlarda yaylar bütün ara düğümlere uygulandı mı?
- Ekranda birleşik görünen düğümler gerçekten aynı düğüm mü?
- "Rijit" diye tanımlanan elemanların rijitliği makul mertebede mi?
- Modal analizin ilk modlarında beklenmedik uzun periyotlar var mı?

## Sık sorulan sorular

### Kararsızlık uyarısı varken analiz sonuçlarını kullanabilir miyim?

11'den fazla basamak kaybı ya da sıfırdan farklı negatif rijitlik özdeğeri varsa hayır; önce model düzeltilmelidir. 6 ile 11 basamak arası kayıp bilgi amaçlıdır, ancak sonuçlar dikkatle kontrol edilmelidir.

### Advanced Solver neden sorunlu düğümü göstermiyor?

Advanced Solver yalnızca önemli bir basamak kaybı olduğunu bildirir. Kaybedilen basamak sayısını, düğüm adını ve serbestlik derecesini görmek için analizi Standard Solver ile yeniden çalıştırmak gerekir.

### Uyarı yalnızca P-delta açıkken çıkıyorsa ne demektir?

Bu durumda sorun genellikle model kurgusunda değil, yapının gerçek bir burkulma eğiliminde ya da düşey yüklerin çok yüksek olmasındadır. Kesitleri, burkulma boylarını ve stabilite elemanlarını yeniden değerlendirin.

### Mafsallı bir çaprazı nasıl tanımlamalıyım?

İki uçta M2 ve M3 momentlerini serbest bırakmak yeterlidir. Burulmayı (T) yalnızca bir uçta serbest bırakın; iki uçta birden serbest bırakılırsa çubuk kendi ekseni etrafında dönebilir ve kararsızlık uyarısı çıkar.

## Kaynaklar

- [CSI Knowledge Base: Lost digit of accuracy and ill-conditions](https://web.wiki.csiamerica.com/wiki/spaces/etabs/pages/1474683/Lost+digit+of+accuracy+and+Ill-Conditions)
- [SAP2000 yardım belgesi: Analysis Monitor](https://help.csiamerica.com/help/sap2000/26/26.0.0/SAP2000/WebHelp/Menus/Analyze/Analysis_Window.htm)
- SAP2000 kurulum klasöründeki `CSI_OAPI_Documentation.chm` (OAPI fonksiyon başvuru belgesi)

## Yazar hakkında

[Mustafa Furkan Özel](/), Ankara'da çalışan bir makine mühendisi ve Gazi Üniversitesi'nde doktora öğrencisidir. Güneş enerjisi santralleri ve endüstriyel yapılar için çelik taşıyıcı sistemler tasarlıyor, statik hesap raporları hazırlıyor ve inceliyor. Soru ve önerileriniz için: hi@furkanis.me
