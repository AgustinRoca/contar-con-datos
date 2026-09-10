"""
Arma las distintas versiones de la pieza a partir de fuentes separadas, para
que el repo quede ordenado por tipo de cosa en vez de todo mezclado en un
HTML gigante:

  content/*.json               -- TEXTO EDITORIAL: titulos, parrafos, preguntas
                                   de quiz, citas, fuentes del pie. Un archivo
                                   por seccion de la pieza (hero, parte1,
                                   parte2, parte3, cierre, footer, shared).
                                   Para cambiar una frase de la pieza, se edita
                                   ACA, no en el HTML.
  assets/svg/*.svg              -- GRAFICOS: cada chart y cada divisor
                                   decorativo en su propio archivo .svg
                                   (incluye el mapa mundial, separado en el
                                   contorno de paises + el marcador de
                                   Argentina).
  output/pieza_template.html    -- ESQUELETO HTML: la estructura de la pagina
                                   (secciones, clases, botones), con
                                   {{TXT:archivo.clave}} donde va un texto de
                                   content/ y {{SVG:nombre}} donde va un
                                   grafico de assets/svg/.
  output/pieza.css              -- todos los estilos
  output/pieza.js               -- toda la logica interactiva (quizzes,
                                   pictogramas, tooltips, toggles SAT/DEIS,
                                   globo)

Este script hace el "armado": inyecta el texto y los graficos en el
esqueleto, y despues pega el CSS dentro de <style> y el JS dentro de
<script> (la plataforma de Artifacts no permite que el HTML publicado cargue
un .css o .js externo en tiempo de ejecucion: tiene que ser un solo archivo
autocontenido).

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
import json
import re
from pathlib import Path

OUT = Path("output")
MEDIA = OUT / "media"
SVG_DIR = Path("assets/svg")
CONTENT_DIR = Path("content")
template = (OUT / "pieza_template.html").read_text(encoding="utf-8")
css = (OUT / "pieza.css").read_text(encoding="utf-8").rstrip("\n")
js = (OUT / "pieza.js").read_text(encoding="utf-8").rstrip("\n")

# El template no tiene los graficos SVG (ni el mapa mundial) pegados adentro:
# cada uno vive en su propio archivo bajo assets/svg/, y aca se inyectan en
# el lugar marcado con {{SVG:nombre_de_archivo}}.
#
# Excepcion: el contorno de paises del mapa mundial no se duplica en
# assets/svg/, porque ya es la salida de un pipeline de datos (ver
# scripts/process/) que vive en data/processed/; el build lo lee de ahi
# directo para que haya un solo lugar donde regenerarlo.
_SVG_TOKEN = re.compile(r"\{\{SVG:([a-zA-Z0-9_]+)\}\}")
_SVG_OVERRIDES = {
    "world_map_countries": Path("data/processed/world_map_country_level_inner.svg"),
}


def _inject_svgs(match: "re.Match[str]") -> str:
    name = match.group(1)
    path = _SVG_OVERRIDES.get(name, SVG_DIR / f"{name}.svg")
    if not path.exists():
        raise SystemExit(f"No se encontro {path} (referenciado como {{{{SVG:{name}}}}} en el template).")
    return path.read_text(encoding="utf-8").rstrip("\n")


template = _SVG_TOKEN.sub(_inject_svgs, template)

# El texto editorial (titulos, parrafos, preguntas de quiz, citas, fuentes)
# tampoco esta pegado en el template: vive en content/<archivo>.json, uno por
# seccion de la pieza, y se inyecta donde el template marca {{TXT:archivo.clave}}.
# Un valor que es una lista (por ahora, solo footer.sources) se renderiza como
# una lista de <li> uno por elemento.
#
# El contenido de content/*.json no tiene tags HTML: usa una sintaxis
# markdown-lite que _render_markdown() convierte a HTML aca, en el build, para
# que los JSON queden como texto plano sin markup mezclado con el contenido:
#   **texto**   -> <strong>
#   *texto*     -> <em>
#   `texto`     -> <span class="accent"> (resalta una frase en el color del titulo)
#   [texto](url)-> <a target="_blank" rel="noopener noreferrer">
#   salto de linea real -> <br>
_TXT_TOKEN = re.compile(r"\{\{TXT:([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\}\}")
_content_cache: dict[str, dict] = {}

_MD_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MD_ACCENT = re.compile(r"`(.+?)`")
_MD_ITALIC = re.compile(r"\*(.+?)\*")
# El grupo de la URL admite un nivel de parentesis balanceados adentro (hay
# URLs reales, como la de la OMS o la del Lancet, que traen un "(...)" en el
# medio), para no cortar el link en el primer ")" que aparece.
_MD_LINK = re.compile(r"\[([^\]]+)\]\(((?:[^()]|\([^()]*\))*)\)")


def _render_markdown(text: str) -> str:
    text = _MD_BOLD.sub(r"<strong>\1</strong>", text)
    text = _MD_ACCENT.sub(r'<span class="accent">\1</span>', text)
    text = _MD_ITALIC.sub(r"<em>\1</em>", text)
    text = _MD_LINK.sub(r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', text)
    return text.replace("\n", "<br>")


def _content_for(fname: str) -> dict:
    if fname not in _content_cache:
        path = CONTENT_DIR / f"{fname}.json"
        if not path.exists():
            raise SystemExit(f"No se encontro {path} (referenciado en el template).")
        _content_cache[fname] = json.loads(path.read_text(encoding="utf-8"))
    return _content_cache[fname]


def _inject_text(match: "re.Match[str]") -> str:
    fname, key = match.group(1), match.group(2)
    content = _content_for(fname)
    if key not in content:
        raise SystemExit(f"content/{fname}.json no tiene la clave '{key}' (referenciada como {{{{TXT:{fname}.{key}}}}}).")
    value = content[key]
    if isinstance(value, list):
        return "\n".join(f"      <li>{_render_markdown(item)}</li>" for item in value)
    return _render_markdown(value)


template = _TXT_TOKEN.sub(_inject_text, template)

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
FAVICON = OUT / "img" / "ribbon.png"

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


def with_favicon(doc: str) -> str:
    favicon_b64 = base64.b64encode(FAVICON.read_bytes()).decode("ascii")
    return doc.replace("__FAVICON_SRC__", f"data:image/png;base64,{favicon_b64}")


def as_full_document(body_doc: str) -> str:
    # El <title> y el <link rel="icon"> de la plantilla van pegados uno al
    # otro arriba de todo; los dos se mueven al <head> del documento final,
    # el resto queda en el <body>.
    title_start = body_doc.find("<title>")
    if title_start == -1:
        head_extra = "<title>Contar con datos</title>"
        body_html = body_doc
    else:
        after_title = body_doc.find("</title>", title_start) + len("</title>")
        icon_start = body_doc.find('<link rel="icon"', after_title)
        head_end = body_doc.find(">", icon_start) + 1 if 0 <= icon_start - after_title < 5 else after_title
        head_extra = body_doc[title_start:head_end]
        body_html = body_doc[:title_start] + body_doc[head_end:]
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{head_extra}
</head>
<body>
{body_html}
</body>
</html>
"""


def build(name: str, *, inline_video: bool, identity: str, full_document: bool) -> None:
    doc = with_favicon(with_identity(with_video_refs(html, inline=inline_video), identity=identity))
    if full_document:
        doc = as_full_document(doc)
    path = OUT / name
    path.write_text(doc, encoding="utf-8")
    print(f"Generado {path} ({len(doc):,} caracteres)".replace(",", "."))


# pieza_visual.html (para el Artifact) ya no se usa; descomentar si hiciera
# falta de nuevo.
# build("pieza_visual.html", inline_video=True, identity="named", full_document=False)
build("pieza_site.html", inline_video=False, identity="named", full_document=True)
build("pieza_site_anon.html", inline_video=False, identity="anon", full_document=True)

print(f"Recorda subir tambien la carpeta {MEDIA}/ junto con pieza_site.html / pieza_site_anon.html.")
