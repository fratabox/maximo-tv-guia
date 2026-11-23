#!/usr/bin/env python3
"""Genera guide-tv.json: versión liviana de la guía para apps de TV (webOS).

Uso: compactar.py guide.xml salida.json
Solo deja los canales con programas y la ventana de tiempo que la TV usa (hasta 36 h hacia adelante).
"""
import html
import json
import re
import sys
import time

TZ = re.compile(r"(\d{14})\s*([+-]\d{4})?")


def epoch(s):
    m = TZ.match(s or "")
    if not m:
        return 0
    t = time.strptime(m.group(1), "%Y%m%d%H%M%S")
    import calendar
    v = calendar.timegm(t)
    z = m.group(2)
    if z:
        off = int(z[1:3]) * 3600 + int(z[3:5]) * 60
        v -= off if z[0] == "+" else -off
    return v


def main():
    src, out = sys.argv[1:3]
    x = open(src, encoding="utf-8").read()
    names = {}
    for m in re.finditer(r'<channel id="([^"]+)">\s*<display-name[^>]*>([^<]*)', x):
        names[html.unescape(m.group(1))] = html.unescape(m.group(2))
    ahora = int(time.time())
    desde, hasta = ahora - 3600, ahora + 36 * 3600
    progs = {}
    for m in re.finditer(r'<programme start="([^"]+)" stop="([^"]+)" channel="([^"]+)">(.*?)</programme>', x, re.S):
        s, e = epoch(m.group(1)), epoch(m.group(2))
        if e <= desde or s >= hasta or e <= s:
            continue
        cid = html.unescape(m.group(3))
        t = re.search(r"<title[^>]*>([^<]*)</title>", m.group(4))
        if not t:
            continue
        d = re.search(r"<desc[^>]*>([^<]*)</desc>", m.group(4))
        desc = html.unescape(d.group(1)).strip()[:150] if d else ""
        progs.setdefault(cid, []).append([s, e, html.unescape(t.group(1)).strip(), desc])
    canales = []
    for cid, lista in progs.items():
        if cid in names:
            lista.sort(key=lambda p: p[0])
            canales.append({"i": cid, "n": names[cid], "p": lista})
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"gen": ahora, "c": canales}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"guide-tv.json: {len(canales)} canales, {sum(len(c['p']) for c in canales)} programas")


if __name__ == "__main__":
    main()
