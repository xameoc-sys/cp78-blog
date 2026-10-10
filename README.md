# Blog — Correduria Publica No. 78

Blog estatico (sin dependencias) con dos secciones:

- **Correduria Publica** (15 articulos)
- **Derecho Fiscal** (15 articulos)

## Como funciona

- content/<seccion>/<slug>.md — fuente de verdad del contenido (frontmatter + Markdown).
- src/build.py — genera el sitio en docs/ (HTML, sitemap.xml, robots.txt, llms.txt).
- src/style.css — estilos.
- src/contenido.py + src/seed.py — contenido inicial (ya volcado a content/).

## Editar

1. Edita o agrega un archivo en content/correduria/ o content/fiscal/.
   Frontmatter: titulo, descripcion, keywords, fecha, slug.
2. Regenera: python3 src/build.py
3. Publica: git add -A && git commit -m "contenido" && git push

## Pendiente

- Cambiar BASE_URL en src/build.py cuando haya dominio propio.
- Agregar datos de contacto reales (hoy son placeholder en el pie).
