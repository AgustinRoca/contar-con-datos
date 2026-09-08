"""
Arma las distintas versiones de la pieza a partir de tres fuentes separadas,
para mantener el repo ordenado:

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

Ademas resuelve dos cosas que varian segun donde se publique cada version:

  - el video del cierre: incrustado en base64 para el Artifact (un solo archivo
    autocontenido); referenciado como output/media/*.mp4 aparte para los sitios
    estaticos (asi el navegador lo puede pedir por partes en vez de cargar un
    HTML de +10 MB).
  - la identidad del autor y la mencion al repositorio: "nombrada" (nombre real
    + link al repo de GitHub personal) para el Artifact y para el sitio que va
    en docs/ (github.io con nombre real); "anonima" (pseudonimo, sin link a
    ningun repo identificable) para la entrega al concurso, que exige anonimato.

Genera tres salidas:
  output/pieza_visual.html      -- Artifact (privado), SIN <!DOCTYPE>/<html>/
                                    <head>/<body> propios porque la plataforma
                                    de Artifacts pone los suyos al publicar.
                                    Video inline, identidad nombrada.
  output/pieza_site.html        -- documento HTML completo y valido, para
                                    docs/index.html (GitHub Pages con nombre
                                    real). Video externo, identidad nombrada.
  output/pieza_site_anon.html   -- igual que pieza_site.html pero con identidad
                                    anonima, para la entrega al concurso (ej.
                                    Cloudflare Pages / Netlify, sin git).

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

WA_VIDEO = MEDIA / "whatsapp_video_cierre.mp4"
WA_POSTER = MEDIA / "whatsapp_video_cierre_poster.jpg"

REPO_URL = "https://github.com/AgustinRoca/contar-con-datos"
IDENTITIES = {
    "named": {
        "author": "Agustín Roca",
        "repo_line": (
            f'Scripts de procesamiento y CSVs limpios: '
            f'<a href="{REPO_URL}" target="_blank" rel="noopener">repositorio de GitHub</a>.'
        ),
    },
    "anon": {
        "author": "Bautista",
        "repo_line": "Los scripts de procesamiento y CSVs limpios se harán públicos una vez finalizada la competencia.",
    },
}


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


def with_identity(doc: str, *, identity: str) -> str:
    ident = IDENTITIES[identity]
    return doc.replace("__AUTHOR__", ident["author"]).replace("__REPO_LINE__", ident["repo_line"])


def as_full_document(body_doc: str) -> str:
    title_start = body_doc.find("<title>")
    title_end = body_doc.find("</title>") + len("</title>")
    title_tag = body_doc[title_start:title_end] if title_start != -1 else "<title>Contar con datos</title>"
    body_html = body_doc[:title_start] + body_doc[title_end:] if title_start != -1 else body_doc
    return f"""<!DOCTYPE html>
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


def build(name: str, *, inline_video: bool, identity: str, full_document: bool) -> None:
    doc = with_identity(with_video_refs(html, inline=inline_video), identity=identity)
    if full_document:
        doc = as_full_document(doc)
    path = OUT / name
    path.write_text(doc, encoding="utf-8")
    print(f"Generado {path} ({len(doc):,} caracteres)".replace(",", "."))


build("pieza_visual.html", inline_video=True, identity="named", full_document=False)
build("pieza_site.html", inline_video=False, identity="named", full_document=True)
build("pieza_site_anon.html", inline_video=False, identity="anon", full_document=True)

print(f"Recorda subir tambien la carpeta {MEDIA}/ junto con pieza_site.html / pieza_site_anon.html.")
