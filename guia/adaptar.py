#!/usr/bin/env python3
"""Adapta la guía a la lista del usuario para TiviMate y otras apps.

Uso: adaptar.py guide.xml nombres.txt salida.xml

Cada canal de la guía recibe, como nombres alternativos, los nombres exactos de los canales de
la lista del usuario que le corresponden (guia/nombres.txt: grupo<TAB>nombre, sin direcciones).
"""
import html
import re
import sys
import unicodedata
from collections import Counter

CT = {"ar": "AR", "arg": "AR", "argentina": "AR", "uy": "UY", "uru": "UY", "uruguay": "UY",
      "es": "ES", "esp": "ES", "espana": "ES", "spain": "ES", "mex": "MX", "mx": "MX", "mexico": "MX",
      "col": "CO", "colombia": "CO", "chi": "CL", "chile": "CL", "per": "PE", "peru": "PE"}
Q = {"hd", "fhd", "uhd", "sd", "4k", "8k", "h265", "hevc", "h264", "50fps", "60fps", "raw", "hq", "lq",
     "ppv", "bar", "live", "event"}
ALIAS = {"a3series": "atreseries", "antena 3 internacional": "antena 3", "natgeo": "national geographic",
         "natgeo mundo": "national geographic", "natgeo wild": "nat geo wild", "nat geo wild n": "nat geo wild",
         "tv5 monde": "tv5monde", "el nueve": "canal 9", "el trece": "canal 13",
         "television publica": "tv publica", "history channel": "history", "discovery tlc": "tlc",
         "discovery hgtv": "hgtv", "discovery home health": "discovery home and health",
         "discovery familia": "discovery kids", "fox deportes": "fox sports", "sony channel": "sony",
         "espn 1": "espn", "tyc sports int": "tyc sports", "fox sports 1": "fox sports", "gol tv": "gol",
         "tudn mex": "tudn", "tudn usa": "tudn", "tudn us": "tudn", "canal 12": "teledoce",
         "canal 12 la tele": "teledoce", "canal 4 monte carlo": "canal 4", "canal 4 montecarlo": "canal 4",
         "montecarlo": "canal 4", "dsports": "directv sports", "dsports plus": "directv sports plus"}
CAT_PREFIX = {"cine", "deportes", "doc", "docs", "tv", "series"}
GRUPO_PAIS = {"espana": "ES", "uruguay": "UY", "argentina": "AR"}


def plain(s):
    s = unicodedata.normalize("NFD", s)
    s = re.sub("[̀-ͯ]", "", s).lower().replace("&", " ")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def norm(raw):
    raw = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", raw)
    country, out = None, []
    for t in plain(raw).split():
        if t in CT:
            country = country or CT[t]
            continue
        if t in Q:
            continue
        out.append("m" if t == "movistar" else t)
    k = " ".join(out)
    return ALIAS.get(k, k), country


def cargar_guia(path):
    x = open(path, encoding="utf-8").read()
    chans = {}
    for m in re.finditer(r'<channel id="([^"]+)">\s*<display-name[^>]*>([^<]*)', x):
        chans[html.unescape(m.group(1))] = html.unescape(m.group(2))
    cuenta = Counter(html.unescape(c) for c in re.findall(r'<programme [^>]*channel="([^"]+)"', x))
    return x, chans, cuenta


def asociar(chans, cuenta, nombres):
    por = {}
    for cid, name in chans.items():
        k, c = norm(name)
        idc = cid[:2] if len(cid) > 3 and cid[2] == "|" else None
        por.setdefault(k, []).append((cid, c or idc))
    claves = list(por)

    def elegir(lst, cc):
        pool = [e for e in lst if e[1] == cc] or [e for e in lst if e[1] is None] if cc else lst
        pool = [e for e in pool if cuenta.get(e[0], 0) > 0] or pool
        return max(pool, key=lambda e: cuenta.get(e[0], 0))[0] if pool else None

    res = {}
    for grupo, nombre in nombres:
        k, c = norm(nombre)
        if plain(grupo).startswith("canales"):
            p = k.split(" ")
            if len(p) > 1 and p[0] in CAT_PREFIX:
                k = " ".join(p[1:])
                k = ALIAS.get(k, k)
        if not k:
            continue
        cc = c or GRUPO_PAIS.get(plain(grupo))
        cid = elegir(por[k], cc) if k in por else None
        if cid is None:
            cand = []
            for kk in claves:
                if kk != k and ((len(k) >= 4 and kk.startswith(k + " ")) or (len(kk) >= 4 and k.startswith(kk + " "))):
                    cand += por[kk]
            if cc:
                cand = [e for e in cand if e[1] in (cc, None)]
            ids = {e[0] for e in cand}
            if len(ids) == 1:
                cid = next(iter(ids))
        if cid and cuenta.get(cid, 0) > 0:
            res.setdefault(cid, []).append(nombre)
    return res


def main():
    guia, nombres_txt, salida = sys.argv[1:4]
    x, chans, cuenta = cargar_guia(guia)
    nombres = [tuple(l.rstrip("\n").split("\t", 1)) for l in open(nombres_txt, encoding="utf-8") if "\t" in l]
    res = asociar(chans, cuenta, nombres)

    def reemplazo(m):
        cid = html.unescape(m.group(1))
        extra = "".join(f"<display-name>{html.escape(n, quote=False)}</display-name>" for n in dict.fromkeys(res.get(cid, [])))
        return m.group(0) + extra

    x = re.sub(r'<channel id="([^"]+)">\s*<display-name[^>]*>[^<]*</display-name>', reemplazo, x)
    open(salida, "w", encoding="utf-8").write(x)
    print(f"Canales de tu lista asociados: {sum(len(set(v)) for v in res.values())} de {len(nombres)}")


if __name__ == "__main__":
    main()
