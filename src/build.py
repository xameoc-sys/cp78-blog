#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generador estatico del blog — Correduria Publica No. 78.

Lee content/<seccion>/<slug>.md y escribe el sitio en docs/ para GitHub Pages.
Sin dependencias externas.  Uso:  python3 src/build.py
"""
import html, json, os, re, shutil
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENIDO = os.path.join(RAIZ, "content")
SALIDA = os.path.join(RAIZ, "docs")
SRC = os.path.join(RAIZ, "src")

BASE_URL = "https://xameoc-sys.github.io/cp78-blog"
MARCA = "Correduria Publica No. 78"

SECCIONES = {
    "correduria": {
        "nombre": "Correduria Publica",
        "titulo": "Correduria Publica en Guadalajara",
        "descripcion": ("Que hace un corredor publico, que actos formaliza y cuando conviene "
                        "acudir a uno. Guia practica para empresas y particulares en "
                        "Guadalajara, Zapopan y Jalisco."),
    },
    "fiscal": {
        "nombre": "Derecho Fiscal",
        "titulo": "Derecho Fiscal en Guadalajara",
        "descripcion": ("Guias de derecho fiscal y tributario en Mexico: ISR, IVA, RESICO, "
                        "deducciones, auditorias y defensa ante el SAT, con enfoque practico "
                        "para Guadalajara, Zapopan y Jalisco."),
    },
}

PLANTILLA = """<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descripcion}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_tipo}">
<meta property="og:site_name" content="{marca}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descripcion}">
<meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="{prefijo}style.css">
{jsonld}
</head>
<body>
<header class="sitio">
  <div class="contenido barra">
    <a class="marca" href="{prefijo}index.html">{marca}</a>
    <nav>
      <a href="{prefijo}index.html">Inicio</a>
      <a href="{prefijo}correduria/index.html">Correduria Publica</a>
      <a href="{prefijo}fiscal/index.html">Derecho Fiscal</a>
    </nav>
  </div>
</header>
<main class="contenido">
{cuerpo}
</main>
<footer class="sitio">
  <div class="contenido">
    <p><strong>{marca}</strong> — Guadalajara, Jalisco.</p>
    <p class="aviso">Sitio en construccion: los datos de contacto se agregaran en la siguiente version.</p>
  </div>
</footer>
</body>
</html>
"""


def esc(t):
    return html.escape(t or "", quote=True)


def parsear_md(ruta):
    with open(ruta, encoding="utf-8") as f:
        crudo = f.read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", crudo, re.S)
    if not m:
        raise ValueError("Sin frontmatter: " + ruta)
    meta, cuerpo = m.group(1), m.group(2)
    datos = {"keywords": [], "fecha": date.today().isoformat()}
    for linea in meta.splitlines():
        if not linea.strip() or ":" not in linea:
            continue
        clave, valor = linea.split(":", 1)
        clave, valor = clave.strip(), valor.strip().strip('"')
        if clave == "keywords":
            datos[clave] = [k.strip() for k in valor.split(",") if k.strip()]
        else:
            datos[clave] = valor
    datos["cuerpo_md"] = cuerpo.strip()
    return datos


def md_a_html(md):
    salida, en_ul, en_ol = [], False, False

    def cerrar():
        nonlocal en_ul, en_ol
        if en_ul:
            salida.append("</ul>"); en_ul = False
        if en_ol:
            salida.append("</ol>"); en_ol = False

    def inline(t):
        t = esc(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', t)
        return t

    for bloque in md.split("\n\n"):
        b = bloque.strip()
        if not b:
            continue
        if b.startswith("### "):
            cerrar(); salida.append("<h3>" + inline(b[4:]) + "</h3>")
        elif b.startswith("## "):
            cerrar(); salida.append("<h2>" + inline(b[3:]) + "</h2>")
        elif b.startswith("- "):
            if not en_ul:
                cerrar(); salida.append("<ul>"); en_ul = True
            for item in b.splitlines():
                salida.append("<li>" + inline(item[2:].strip()) + "</li>")
        elif re.match(r"^\d+\.\s", b):
            if not en_ol:
                cerrar(); salida.append("<ol>"); en_ol = True
            for item in b.splitlines():
                salida.append("<li>" + inline(re.sub(r"^\d+\.\s", "", item)) + "</li>")
        else:
            cerrar(); salida.append("<p>" + inline(b) + "</p>")
    cerrar()
    return "\n".join(salida)


def jsonld_articulo(a):
    datos = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": a["titulo"],
        "description": a["descripcion"],
        "datePublished": a["fecha"],
        "dateModified": a.get("actualizado", a["fecha"]),
        "inLanguage": "es-MX",
        "author": {"@type": "Organization", "name": MARCA},
        "publisher": {"@type": "Organization", "name": MARCA},
        "mainEntityOfPage": BASE_URL + "/" + a["seccion"] + "/" + a["slug"] + "/",
        "keywords": ", ".join(a["keywords"]),
    }
    return ('<script type="application/ld+json">'
            + json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c")
            + "</script>")


def escribir(ruta, texto):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


def pagina(titulo, descripcion, canonical, cuerpo, prefijo, jsonld="", og_tipo="website"):
    return PLANTILLA.format(titulo=esc(titulo), descripcion=esc(descripcion),
                            canonical=canonical, cuerpo=cuerpo, prefijo=prefijo,
                            jsonld=jsonld, og_tipo=og_tipo, marca=esc(MARCA))


def item_html(seccion, a):
    return ('<li><a href="' + a["slug"] + '/">' + esc(a["titulo"]) + '</a>'
            '<span class="resumen">' + esc(a["descripcion"]) + '</span></li>')


def main():
    if os.path.isdir(SALIDA):
        shutil.rmtree(SALIDA)
    os.makedirs(SALIDA)
    shutil.copy(os.path.join(SRC, "style.css"), os.path.join(SALIDA, "style.css"))
    open(os.path.join(SALIDA, ".nojekyll"), "w").close()

    articulos = {}
    for seccion in SECCIONES:
        carpeta = os.path.join(CONTENIDO, seccion)
        lista = []
        for archivo in sorted(os.listdir(carpeta)):
            if archivo.endswith(".md"):
                a = parsear_md(os.path.join(carpeta, archivo))
                a["seccion"] = seccion
                lista.append(a)
        articulos[seccion] = lista

    bloques = []
    for seccion, meta in SECCIONES.items():
        enlaces = "\n".join(item_html(seccion, a) for a in articulos[seccion])
        bloques.append('<section class="seccion"><h2><a href="' + seccion + '/index.html">'
                       + esc(meta["nombre"]) + '</a></h2>'
                       '<p class="intro">' + esc(meta["descripcion"]) + '</p>'
                       '<ul class="listado">' + enlaces + '</ul></section>')
    escribir(os.path.join(SALIDA, "index.html"),
             pagina(MARCA + " — Correduria Publica y Derecho Fiscal en Guadalajara",
                    "Blog de correduria publica y derecho fiscal en Guadalajara, Zapopan y "
                    "Jalisco: que hace un corredor publico, que actos formaliza y guias fiscales.",
                    BASE_URL + "/", "\n".join(bloques), "", ""))

    for seccion, meta in SECCIONES.items():
        enlaces = "\n".join(item_html(seccion, a) for a in articulos[seccion])
        escribir(os.path.join(SALIDA, seccion, "index.html"),
                 pagina(meta["titulo"] + " — " + MARCA, meta["descripcion"],
                        BASE_URL + "/" + seccion + "/",
                        "<h1>" + esc(meta["nombre"]) + "</h1>"
                        '<p class="intro">' + esc(meta["descripcion"]) + '</p>'
                        '<ul class="listado">' + enlaces + '</ul>', "../", ""))
        for a in articulos[seccion]:
            cuerpo = ('<article class="post"><h1>' + esc(a["titulo"]) + '</h1>'
                      '<p class="fecha">' + esc(a.get("fecha", "")) + ' · '
                      '<a href="../index.html">' + esc(meta["nombre"]) + '</a></p>'
                      + md_a_html(a["cuerpo_md"]) + '</article>')
            escribir(os.path.join(SALIDA, seccion, a["slug"], "index.html"),
                     pagina(a["titulo"], a["descripcion"],
                            BASE_URL + "/" + seccion + "/" + a["slug"] + "/",
                            cuerpo, "../../", jsonld_articulo(a), "article"))

    urls = [BASE_URL + "/"]
    for seccion in SECCIONES:
        urls.append(BASE_URL + "/" + seccion + "/")
        urls += [BASE_URL + "/" + seccion + "/" + a["slug"] + "/" for a in articulos[seccion]]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += ["<url><loc>" + u + "</loc></url>" for u in urls]
    sm.append("</urlset>")
    escribir(os.path.join(SALIDA, "sitemap.xml"), "\n".join(sm))

    escribir(os.path.join(SALIDA, "robots.txt"),
             "User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n"
             "User-agent: OAI-SearchBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\n"
             "User-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\n\n"
             "Sitemap: " + BASE_URL + "/sitemap.xml\n")

    total = sum(len(v) for v in articulos.values())
    escribir(os.path.join(SALIDA, "llms.txt"),
             "# " + MARCA + "\n\n> Blog de correduria publica y derecho fiscal en "
             "Guadalajara, Jalisco (Mexico).\n\nContenido: " + str(total) + " articulos — "
             + str(len(articulos["correduria"])) + " de correduria publica y "
             + str(len(articulos["fiscal"])) + " de derecho fiscal.\n\n## Secciones\n"
             "- [Correduria Publica](" + BASE_URL + "/correduria/)\n"
             "- [Derecho Fiscal](" + BASE_URL + "/fiscal/)\n")

    print("OK —", total, "articulos")
    for seccion, lista in articulos.items():
        print("  " + seccion + ":", len(lista))


if __name__ == "__main__":
    main()
