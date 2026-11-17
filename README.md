# Máximo TV · Guía de programación

Este repositorio genera automáticamente, cada 8 horas, una guía de programación en formato XMLTV para la app **Máximo TV**. No contiene la app, listas de canales ni contenido de video.

**Archivo de la guía:** `https://github.com/fratabox/maximo-tv-guia/releases/download/guia/guide.xml.gz`

## Cómo funciona

1. El proceso **Actualizar guía** (`.github/workflows/update-guide.yml`) usa el generador abierto [iptv-org/epg](https://github.com/iptv-org/epg).
2. Toma las fuentes listadas en `guia/fuentes.txt` y arma un solo archivo con todos los canales.
3. Lo publica en la sección **Releases** con la etiqueta `guia`.

## Agregar o quitar fuentes

Editá `guia/fuentes.txt`: una fuente por línea, con el formato `sitio PAÍS` (por ejemplo `cableplus.com.uy UY`). Las fuentes disponibles son las carpetas de [iptv-org/epg/sites](https://github.com/iptv-org/epg/tree/master/sites). Algunos sitios bloquean las descargas automáticas desde GitHub; la última prueba está anotada en el mismo archivo.

## Aviso

Los horarios provienen de sitios de terceros y se usan para consulta personal. Si el titular de alguno de esos sitios pide que se retire, se quita de `guia/fuentes.txt`.
