---
title: SAP2000 Modelini Python ile Kurmak: OAPI'ye Adım Adım Giriş
slug: sap2000-python-api
date: 2026-11-05
lang: tr
seo_title: SAP2000 Modelini Python ile Kurmak (OAPI Rehberi)
summary: SAP2000 modellerini Python ve OAPI ile koddan üretmek: bağlantı, malzeme, kesit, yük, kombinasyon, analiz ve sonuç okuma; sık yapılan hatalarla.
draft: false
---
**Kısaca:** SAP2000, OAPI (Open Application Programming Interface) adı verilen bir programlama arayüzüyle dışarıdan kontrol edilebilir. Python'da `comtypes` paketiyle SAP2000'e bağlanıp malzeme, kesit, çubuk, mesnet, yük ve kombinasyonları kodla tanımlayabilir, analizi çalıştırıp sonuçları doğrudan okuyabilirsiniz. Bu yaklaşım özellikle güneş enerjisi santrali (GES) taşıyıcıları gibi birbirine benzeyen ama ölçüleri değişen modellerde saatler süren elle modellemeyi dakikalara indirir ve tekrar eden hataları ortadan kaldırır.

Bu yazıda sıfırdan basit bir portal çerçeveyi Python ile kuruyor, analiz ediyor ve farklı açıklıklar için kendiliğinden yeniden çözdürüyoruz. Sonda, gerçek projelerde karşılaştığım hataları ve çözümlerini bulacaksınız.

## SAP2000 OAPI nedir?

OAPI, SAP2000'in arayüzde yaptığınız hemen her işlemi bir fonksiyon çağrısı olarak sunan programlama arayüzüdür. Arayüzde "Define › Materials" menüsünden yaptığınız tanım, OAPI'de `SapModel.PropMaterial.SetMaterial(...)` çağrısına karşılık gelir. SAP2000 bu arayüzü Windows'un COM teknolojisiyle dışarı açar; bu yüzden Python, C#, VBA ve MATLAB gibi COM'a erişebilen her dilden kullanılabilir.

Arayüzün resmi belgesi SAP2000 kurulum klasöründeki `CSI_OAPI_Documentation.chm` dosyasıdır. Her fonksiyonun parametreleri, birimleri ve örnek kodu bu dosyada yer alır. Bir fonksiyonun imzasından emin olmadığınızda ilk bakılacak yer burasıdır.

## Neden modeli elle değil kodla kurmalı?

| | Elle modelleme | Python ile modelleme |
|---|---|---|
| Benzer 10 varyant | Her biri ayrı ayrı çizilir | Tek döngüyle üretilir |
| Ölçü değişikliği | Model yeniden düzenlenir | Bir parametre değişir |
| Tekrar eden hata riski | Her modelde yeniden doğar | Bir kez düzeltilir |
| Kayıt ve izlenebilirlik | Ekran görüntüleri ve notlar | Kodun kendisi belgedir |
| Sonuçları rapora aktarmak | Tablolardan kopyala yapıştır | Doğrudan Excel'e veya rapora yazılır |

Kod yazmak ilk modelde daha uzun sürer. Kazanç, aynı tipte ikinci, üçüncü ve onuncu modelde ortaya çıkar.

## Başlamak için neler gerekir?

- **Windows ve kurulu bir SAP2000.** OAPI, COM üzerinden çalıştığı için yalnızca Windows'ta kullanılabilir.
- **Python 3.** SAP2000 ile aynı bit sürümünde (güncel sürümlerde 64 bit) bir Python kurulumu önerilir.
- **comtypes paketi:** `pip install comtypes`
- **OAPI belgesi:** kurulum klasöründeki `CSI_OAPI_Documentation.chm`

## Adım 1: SAP2000'e bağlanmak

Aşağıdaki kod yüklü en güncel SAP2000 sürümünü başlatır ve modele erişim nesnesini (`SapModel`) verir. Bu nesne, sonraki bütün çağrıların giriş noktasıdır.

```python
import comtypes.client

helper = comtypes.client.CreateObject("SAP2000v1.Helper")
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)

sap = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
sap.ApplicationStart()
SapModel = sap.SapModel
```

Zaten açık olan bir SAP2000 penceresine bağlanmak isterseniz `CreateObjectProgID` ve `ApplicationStart` satırlarının yerine `sap = helper.GetObject("CSI.SAP2000.API.SapObject")` kullanabilirsiniz.

## Adım 2: Her çağrının sonucunu kontrol etmek

OAPI fonksiyonları başarılı olduğunda `0`, başarısız olduğunda farklı bir değer döndürür. Hata vermez, sessizce devam eder. Bu yüzden ilk iş küçük bir kontrol fonksiyonu yazmaktır; kodun geri kalanında her çağrıyı bununla sarmak, hatanın nerede olduğunu anında gösterir.

```python
def kontrol(sonuc, adim):
    kod = sonuc[-1] if isinstance(sonuc, (list, tuple)) else sonuc
    if kod != 0:
        raise RuntimeError(f"{adim} başarısız oldu (dönüş kodu: {kod})")
    return sonuc
```

Birden fazla değer döndüren fonksiyonlarda (örneğin yeni çubuğun adı) dönüş kodu listenin son elemanıdır; fonksiyon bu yüzden ikisini de ele alıyor.

## Adım 3: Yeni model, birimler, malzeme ve kesit

```python
KN_M_C = 6   # eUnits: kN, m, °C

def model_baslat(SapModel):
    kontrol(SapModel.InitializeNewModel(KN_M_C), "Model başlatma")
    kontrol(SapModel.File.NewBlank(), "Boş model")

    # S235 yapı çeliği (eMatType: 1 = çelik)
    kontrol(SapModel.PropMaterial.SetMaterial("S235", 1), "Malzeme")
    kontrol(SapModel.PropMaterial.SetMPIsotropic("S235", 210e6, 0.3, 1.2e-5), "Elastik özellikler")
    kontrol(SapModel.PropMaterial.SetWeightAndMass("S235", 1, 78.5), "Birim hacim ağırlığı")

    # 100x100x4 kutu profil: dış yükseklik, dış genişlik, flanş ve gövde kalınlığı (m)
    kontrol(SapModel.PropFrame.SetTube("KUTU100", "S235", 0.10, 0.10, 0.004, 0.004), "Kesit")
```

Birimler model başlatılırken belirlenir ve bütün sayılar o birimde yorumlanır. Burada elastisite modülü 210 GPa, yani kN/m² cinsinden `210e6` olarak girilir. Birim karışıklığı, OAPI ile çalışırken en sık rastlanan ve sonucu sessizce bozan hatadır.

## Adım 4: Geometri ve mesnetler

```python
def cerceve_kur(SapModel, L, H):
    kontrol(SapModel.FrameObj.AddByCoord(0, 0, 0, 0, 0, H, "", "KUTU100", "K1", "Global"), "Sol kolon")
    kontrol(SapModel.FrameObj.AddByCoord(L, 0, 0, L, 0, H, "", "KUTU100", "K2", "Global"), "Sağ kolon")
    kontrol(SapModel.FrameObj.AddByCoord(0, 0, H, L, 0, H, "", "KUTU100", "B1", "Global"), "Kiriş")

    ankastre = [True, True, True, True, True, True]
    for kolon in ("K1", "K2"):
        alt, ust, ret = kontrol(SapModel.FrameObj.GetPoints(kolon, "", ""), "Kolon uçları")
        kontrol(SapModel.PointObj.SetRestraint(alt, ankastre), "Mesnet")
```

`AddByCoord` aynı koordinattaki noktaları birleştirir, bu yüzden kiriş kolon üstlerine kendiliğinden bağlanır. Mesnet atarken nokta adını tahmin etmek yerine `GetPoints` ile çubuğun gerçek uç noktalarını almak, ilerideki birçok hatayı baştan önler.

## Adım 5: Yükler ve kombinasyon

```python
def yukle(SapModel, kar_yuku):
    # eLoadPatternType: 1 = ölü yük, 7 = kar. Ölü yükte öz ağırlık çarpanı 1.
    kontrol(SapModel.LoadPatterns.Add("G", 1, 1), "Ölü yük deseni")
    kontrol(SapModel.LoadPatterns.Add("S", 7, 0), "Kar yükü deseni")

    # Kirişe yerçekimi yönünde (Dir = 10) düzgün yayılı kar yükü, kN/m
    kontrol(SapModel.FrameObj.SetLoadDistributed("B1", "S", 1, 10, 0, 1, kar_yuku, kar_yuku), "Kar yükü")

    kontrol(SapModel.RespCombo.Add("KOMB1", 0), "Kombinasyon")
    kontrol(SapModel.RespCombo.SetCaseList("KOMB1", 0, "G", 1.35), "Kombinasyon: G")
    kontrol(SapModel.RespCombo.SetCaseList("KOMB1", 0, "S", 1.50), "Kombinasyon: S")
```

Bir yük deseni eklendiğinde SAP2000 aynı adla bir yükleme durumunu da kendiliğinden oluşturur; kombinasyonda bu yükleme durumları kullanılır. Katsayılar burada yalnızca örnektir; gerçek projede ilgili yönetmeliğin kombinasyonlarını kullanın.

## Adım 6: Analiz ve sonuç okuma

```python
def analiz_et(SapModel, dosya):
    kontrol(SapModel.File.Save(dosya), "Kaydetme")
    kontrol(SapModel.Analyze.RunAnalysis(), "Analiz")

    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetComboSelectedForOutput("KOMB1")

    s = kontrol(SapModel.Results.FrameForce("B1", 0, 0, [], [], [], [], [], [],
                                            [], [], [], [], [], [], []), "Kiriş iç kuvvetleri")
    M3 = s[13]   # dönen listede moment M3 dizisi
    return max(abs(m) for m in M3)
```

SAP2000 analizden önce modelin kaydedilmesini ister. Sonuç fonksiyonları çıktıları liste olarak döndürür; hangi sırada döndüklerini OAPI belgesindeki fonksiyon imzasından okuyabilirsiniz.

## Adım 7: Parametrik çalışma, asıl kazanç

Önceki adımları fonksiyon olarak yazmanın sebebi bu döngü. Aynı çerçeveyi üç farklı açıklık için kurup çözdürmek dört satır sürüyor:

```python
H = 3.0
for L in (6.0, 8.0, 10.0):
    model_baslat(SapModel)
    cerceve_kur(SapModel, L, H)
    yukle(SapModel, kar_yuku=2.0)
    m_max = analiz_et(SapModel, rf"C:\modeller\cerceve_L{L:.0f}.sdb")
    print(f"L = {L:4.1f} m  ->  kirişte en büyük |M3| = {m_max:6.2f} kNm")

sap.ApplicationExit(False)
```

Aynı yapı; kesit listesini taramak, farklı rüzgar ve kar bölgeleri için çözüm üretmek ya da bir GES sahasındaki farklı masa tiplerini tek seferde modellemek için genişletilebilir. Sonuçları `pandas` ile bir tabloya toplayıp Excel'e yazmak da birkaç satırlık iştir.

## Sık yapılan hatalar ve çözümleri

Aşağıdakiler gerçek GES ve sera projelerinde karşılaştığım, çoğu hata mesajı bile vermeden sonucu bozan durumlar.

### Tasarım sonuçları neden görünmüyor?

İki yaygın sebep var. Birincisi, soğuk şekillendirilmiş (cold-formed) kesitler sıcak haddelenmiş çelikle aynı tasarım modülünde kontrol edilmez: malzeme türü soğuk şekillendirilmiş olarak tanımlandıysa tasarım `SapModel.DesignSteel` altında değil `SapModel.DesignColdFormed` altında yürür. İkincisi, tasarımda kullanılacak kombinasyonlar ayrıca seçilmelidir; bunlar ilgili modülün `SetComboStrength` fonksiyonuyla işaretlenmezse tasarım çalışır ama beklediğiniz kombinasyonlar kontrol edilmez.

### Örnek kod neden benim sürümümde çalışmıyor?

Bazı fonksiyonların imzası SAP2000 sürümleri arasında değişir ve yeni sürüm genellikle sonuna `_1`, `_2` gibi bir ek alır (örneğin soğuk şekillendirilmiş kesit tanımlayan `SetColdC` ve `SetColdC_1`). İnternetten bulduğunuz bir örnek çalışmıyorsa, kendi sürümünüzün `.chm` belgesinde fonksiyonun güncel adına ve parametre sırasına bakın.

### Model neden mekanizma oluyor ya da kararsızlık uyarısı veriyor?

En sık üç sebep: çubuk uçlarına fazla serbestlik (release) verilmesi, mesnetlerin yanlış noktalara atanması ve aynı noktaya hem mesnet hem yay tanımlanması. Ayrıca bir çubuk analiz için parçalara bölündüyse, yay gibi atamaların bütün parçalara uygulandığından emin olun. Kod içinde nokta adlarını sıra numarasıyla tahmin etmek yerine `GetPoints` kullanmak bu hataların çoğunu önler.

### Çaprazlar neden yük taşımıyor gibi görünüyor?

Döngüyle eleman üretirken bazı çubukların (örneğin X çaprazların) eleman listelerine eklenmesi unutulabilir ya da yanlış kesit atanabilir. Modeli kurduktan sonra çubuk sayısını ve kesit atamalarını kodla saydırıp beklenen değerle karşılaştırmak, bu tür eksikleri analizden önce yakalar.

### Burkulma boyları neden yanlış hesaplanıyor?

SAP2000, birbirine bağlı ve aynı doğrultudaki çubukları tasarımda tek bir eleman gibi değerlendirebilir ve desteklenmemiş boyu buna göre hesaplar. Kodla ürettiğiniz parçalı elemanlarda desteklenmemiş boyların gerçek yanal destek noktalarıyla uyuştuğunu kontrol edin; gerekirse tasarım modülünün `SetOverwrite` fonksiyonuyla boyları elle tanımlayın.

## Sık sorulan sorular

### OAPI ile ETABS de kontrol edilebilir mi?

Evet. ETABS de aynı mantıkta bir OAPI sunar; bağlantıda `SAP2000v1` yerine `ETABSv1`, `CSI.SAP2000.API.SapObject` yerine `CSI.ETABS.API.ETABSObject` kullanılır. Fonksiyonların büyük bölümü aynı adlarla çalışır.

### Python yerine Excel VBA kullanabilir miyim?

Kullanabilirsiniz; OAPI dilden bağımsızdır. Python'un üstünlüğü; döngüler, sonuç işleme (`pandas`, `numpy`), grafik ve optimizasyon kütüphaneleriyle aynı yerde çalışabilmesidir.

### Mevcut bir modeli açıp değiştirebilir miyim?

Evet. `SapModel.File.OpenFile(dosya_yolu)` ile kayıtlı bir `.sdb` modelini açıp kesitleri, yükleri ya da kombinasyonları kodla değiştirebilir ve yeniden çözdürebilirsiniz.

### Kod yazmak elle modellemeden gerçekten hızlı mı?

Tek seferlik bir model için genellikle hayır. Aynı tipte birden fazla model, sık değişen ölçüler ya da çok sayıda kesit ve yük senaryosu varsa evet; kazanç her yeni varyantta büyür.

## Kaynaklar

- SAP2000 kurulum klasöründeki `CSI_OAPI_Documentation.chm` (resmi fonksiyon başvuru belgesi)
- [CSI Knowledge Base: OAPI](https://wiki.csiamerica.com/display/kb/OAPI)
- [comtypes, Python için COM paketi](https://github.com/enthought/comtypes)

## Yazar hakkında

[Mustafa Furkan Özel](/), Ankara'da çalışan bir makine mühendisi ve Gazi Üniversitesi'nde doktora öğrencisidir. Güneş enerjisi santralleri ve endüstriyel yapılar için çelik taşıyıcı sistemler tasarlıyor, SAP2000 modellerini Python ile otomatikleştiriyor. Soru ve önerileriniz için: hi@furkanis.me
