# -*- coding: utf-8 -*-
"""Vuelca el contenido inicial a archivos Markdown editables en content/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contenido import CORREDURIA, FISCAL

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FECHA = "2026-10-10"

def escribir(seccion, posts):
    carpeta = os.path.join(RAIZ, "content", seccion)
    os.makedirs(carpeta, exist_ok=True)
    for p in posts:
        with open(os.path.join(carpeta, p["slug"] + ".md"), "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write("titulo: " + p["titulo"] + "\n")
            f.write("descripcion: " + p["descripcion"] + "\n")
            f.write("keywords: " + p["keywords"] + "\n")
            f.write("fecha: " + FECHA + "\n")
            f.write("slug: " + p["slug"] + "\n")
            f.write("---\n\n")
            f.write(p["cuerpo"].strip() + "\n")
    print(seccion, "->", len(posts), "archivos")

escribir("correduria", CORREDURIA)
escribir("fiscal", FISCAL)
