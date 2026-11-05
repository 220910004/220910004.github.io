import sys
html='''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:A;src:url(/fonts/archivo.woff2);font-weight:500 760;font-stretch:68% 85%}
@font-face{font-family:M;src:url(/fonts/plex-mono-400.woff2)}
@font-face{font-family:M;src:url(/fonts/plex-mono-500.woff2);font-weight:500}
html,body{margin:0}
.c{width:1200px;height:630px;box-sizing:border-box;background:#ECEEEA;color:#15181B;padding:64px 76px;position:relative;font-family:M}
.top{display:flex;justify-content:space-between;font-size:24px;letter-spacing:.04em;border-bottom:2px solid #15181B;padding-bottom:22px}
.ey{margin-top:58px;font-size:22px;letter-spacing:.12em;color:#4E555C}
h1{font-family:A;font-stretch:68%;font-weight:760;font-size:128px;line-height:.9;margin:14px 0 0}
h1 span{display:block;color:#4E555C;font-weight:520}
.line{position:absolute;left:76px;right:76px;bottom:70px;height:2px;background:#15181B}
.dot{position:absolute;bottom:52px;width:34px;height:34px;border-radius:50%;background:#fff;box-sizing:border-box;box-shadow:0 0 0 6px #ECEEEA}
.w{border:3px solid #15181B}.e{border:5px solid #E2B000}
.now{position:absolute;right:76px;bottom:55px;background:#E2B000;font-weight:500;font-size:20px;padding:6px 12px}
</style></head><body><div class="c">
<div class="top"><span>furkanis.me</span><span>Ankara, Türkiye</span></div>
<div class="ey">MAKİNE MÜHENDİSİ · MECHANICAL ENGINEER</div>
<h1><span>Mustafa Furkan</span>Özel</h1>
<div class="line"></div>
<i class="dot e" style="left:76px"></i><i class="dot e" style="left:190px"></i><i class="dot w" style="left:420px"></i><i class="dot e" style="left:510px"></i><i class="dot w" style="left:610px"></i><i class="dot w" style="left:720px"></i><i class="dot w" style="left:920px"></i><i class="dot e" style="left:965px"></i>
<span class="now">bugün</span>
</div></body></html>'''
open('site/_og.html','w',encoding='utf-8').write(html)
