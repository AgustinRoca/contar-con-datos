"""
Arma output/pieza_visual.html (el archivo que se publica como Artifact) a partir de
tres fuentes separadas, para mantener el repo ordenado:

  output/pieza_template.html  -- esqueleto HTML (titulo + body), con
                                  <link rel="stylesheet" href="pieza.css"> y
                                  <script src="pieza.js"></script> como referencias
  output/pieza.css            -- todos los estilos
  output/pieza.js             -- toda la logica interactiva (quizzes, pictogramas,
                                  tooltips, toggles SAT/DEIS, globo)

La plataforma de Artifacts no permite que el HTML publicado cargue un .css o .js
externo en tiempo de ejecucion: tiene que ser un solo archivo autocontenido. Este
script hace el "inlineado" (pegar el CSS dentro de <style> y el JS dentro de
<script>) para producir ese archivo final, sin tener que editar tres archivos
como si fueran uno solo.

Genera dos salidas a partir de la misma plantilla:
  output/pieza_visual.html -- SIN <!DOCTYPE>/<html>/<head>/<body> propios, porque
                               la plataforma de Artifacts envuelve el contenido
                               con su propio esqueleto al publicar; este es el
                               archivo que se sube como Artifact.
  output/pieza_site.html   -- documento HTML completo y valido (doctype, charset
                               utf-8, viewport, head/body), listo para subir tal
                               cual a GitHub Pages u otro hosting estatico.

Uso:
    python scripts/build_pieza.py
"""
import base64
from pathlib import Path

OUT = Path("output")
MEDIA = OUT / "media"
template = (OUT / "pieza_template.html").read_text(encoding="utf-8")
css = (OUT / "pieza.css").read_text(encoding="utf-8").rstrip("\n")
js = (OUT / "pieza.js").read_text(encoding="utf-8").rstrip("\n")

html = template.replace(
    '<link rel="stylesheet" href="pieza.css">',
    f"<style>\n{css}\n</style>",
)
html = html.replace(
    '<script src="pieza.js"></script>',
    f"<script>\n{js}\n</script>",
)

# Video de WhatsApp en el cierre: en pieza_visual.html (Artifact, un solo
# archivo autocontenido) va incrustado en base64; en pieza_site.html (sitio
# estatico real) se referencia como archivo aparte en output/media/, asi el
# navegador lo puede pedir por partes en vez de cargar un HTML de +10 MB.
WA_VIDEO = MEDIA / "whatsapp_video_cierre.mp4"
WA_POSTER = MEDIA / "whatsapp_video_cierre_poster.jpg"


def with_video_refs(doc: str, *, inline: bool) -> str:
    if inline and WA_VIDEO.exists() and WA_POSTER.exists():
        video_b64 = base64.b64encode(WA_VIDEO.read_bytes()).decode("ascii")
        poster_b64 = base64.b64encode(WA_POSTER.read_bytes()).decode("ascii")
        video_src = f"data:video/mp4;base64,{video_b64}"
        poster_src = f"data:image/jpeg;base64,{poster_b64}"
    else:
        video_src = "media/whatsapp_video_cierre.mp4"
        poster_src = "media/whatsapp_video_cierre_poster.jpg"
    return doc.replace("__WA_VIDEO_SRC__", video_src).replace("__WA_POSTER_SRC__", poster_src)


visual_html = with_video_refs(html, inline=True)
(OUT / "pieza_visual.html").write_text(visual_html, encoding="utf-8")
print(f"Generado {OUT / 'pieza_visual.html'} ({len(visual_html):,} caracteres)".replace(",", "."))

# pieza_site.html: mismo contenido, pero como documento HTML completo y valido,
# para subir directo a GitHub Pages (Artifacts pone su propio doctype/head/body,
# pero un sitio estatico real necesita el suyo, con charset utf-8 explicito para
# que los acentos no se rompan segun como el servidor sirva el archivo).
site_body = with_video_refs(html, inline=False)
title_start = site_body.find("<title>")
title_end = site_body.find("</title>") + len("</title>")
title_tag = site_body[title_start:title_end] if title_start != -1 else "<title>Contar con datos</title>"
body_html = site_body[:title_start] + site_body[title_end:] if title_start != -1 else site_body

site_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{title_tag}
</head>
<body>
{body_html}
</body>
</html>
"""

(OUT / "pieza_site.html").write_text(site_html, encoding="utf-8")
print(f"Generado {OUT / 'pieza_site.html'} ({len(site_html):,} caracteres)".replace(",", "."))
print(f"Recorda subir tambien la carpeta {MEDIA}/ junto con pieza_site.html.")
