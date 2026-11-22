#!/usr/bin/env python3
"""Arma la lista de canales para el generador de guía a partir de guia/fuentes.txt.

Uso: build_channels.py <carpeta sites de iptv-org/epg> <fuentes.txt> <salida.channels.xml>

A cada canal le asigna un id propio y único con el formato PAIS|sitio|site_id,
así la app sabe de qué país es cada guía aunque la fuente no traiga un id estándar.
"""
import glob
import os
import re
import sys

sites_dir, fuentes, salida = sys.argv[1:4]

vistos = set()
filas = []
errores = []

for linea in open(fuentes, encoding="utf-8"):
    linea = linea.strip()
    if not linea or linea.startswith("#"):
        continue
    partes = linea.split()
    entrada = partes[0]
    pais = partes[1].upper() if len(partes) > 1 else "-"
    # Opcional: "solo:espn,fox,tudn" deja únicamente los canales cuyo nombre contiene alguna de esas palabras.
    solo = []
    for extra in partes[2:]:
        if extra.lower().startswith("solo:"):
            solo = [x.strip().lower() for x in extra[5:].split(",") if x.strip()]

    base = os.path.join(sites_dir, entrada)
    if os.path.isdir(base):
        archivos = sorted(glob.glob(os.path.join(base, "*.channels.xml")))
    else:
        archivos = [base + ".channels.xml"]

    encontrados = 0
    limite = int(os.environ.get("LIMITE_POR_FUENTE", "0"))  # solo para pruebas
    for archivo in archivos:
        if not os.path.isfile(archivo):
            continue
        texto = open(archivo, encoding="utf-8").read()
        for m in re.finditer(r"<channel\b([^>]*)>(.*?)</channel>", texto, re.S):
            if limite and encontrados >= limite:
                break
            attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
            site = attrs.get("site")
            sid = attrs.get("site_id")
            if not site or not sid:
                continue
            if solo:
                nombre = re.sub(r"<[^>]+>", "", m.group(2)).strip().lower()
                if not any(w in nombre for w in solo):
                    continue
            lang = attrs.get("lang", "es")
            cid = f"{pais}|{site}|{sid}" if pais != "-" else f"{site}|{sid}"
            if cid in vistos:
                continue
            vistos.add(cid)
            filas.append(
                f'  <channel site="{site}" site_id="{sid}" lang="{lang}" xmltv_id="{cid}">{m.group(2).strip()}</channel>'
            )
            encontrados += 1
    print(f"{entrada} ({pais}): {encontrados} canales")
    if encontrados == 0:
        errores.append(entrada)

import os
import html as _html
extras = os.path.join(os.path.dirname(os.path.abspath(fuentes)), "extras.txt")
if os.path.exists(extras):
    for linea in open(extras, encoding="utf-8"):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        site, sid, pais_x, nombre = (linea.split("|", 3) + ["", "", "", ""])[:4]
        cid = f"{pais_x}|{site}|{sid}"
        if cid in vistos:
            continue
        vistos.add(cid)
        filas.append(
            f'  <channel site="{site}" site_id="{sid}" lang="es" xmltv_id="{cid}">{_html.escape(nombre, quote=False)}</channel>'
        )
        print(f"extra: {nombre}")

with open(salida, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<channels>\n')
    f.write("\n".join(filas))
    f.write("\n</channels>\n")

print(f"Total: {len(filas)} canales")
if errores:
    print("AVISO: no se encontraron canales en: " + ", ".join(errores))
if not filas:
    sys.exit("No hay canales para descargar.")
