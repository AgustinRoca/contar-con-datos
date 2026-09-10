"""
Arma data/processed/world_map_country_level_inner.svg (el contorno de
paises, coloreado segun tasa de suicidio y con tooltips, que se inyecta
adentro del <svg> del mapa mundial de la pieza) a partir de:

  - data/raw/world_map/world-map.svg: el mapa sin colorear (CC BY-SA 3.0,
    "Simple World Map" de Al MacDonald y Fritz Lekschas). Cada pais es un
    <path id="xx"> o, si tiene islas/exclaves, un <g id="xx"> con varios
    <path> adentro; "xx" es el codigo ISO 3166-1 en minuscula (o "_algo"
    si el territorio no tiene uno).
  - data/processed/who_suicide_rate_by_country_2021.csv: la tasa por pais
    (ver scripts/process/process_who_suicide_rates.py).

Que hace, en orden:
  1. Fusiona las Islas Malvinas (id "fk" en el mapa original) adentro del
     grupo de Argentina (id "ar"): sus <path> pasan a ser hijos de "ar", sin
     su propio id/class, para que compartan tooltip y el resaltado al pasar
     el mouse con el resto de Argentina.
  2. A cada pais/territorio que sigue existiendo como entidad propia le
     agrega fill (segun el bin de tasa que le toque, o gris si no hay dato
     de la OMS para ese codigo), stroke, y un data-tooltip con el valor
     (Argentina ademas lleva su nombre adelante y una clase extra
     "country-ar", para el marcador aparte que dibuja la pieza).
  3. Preserva el resto tal cual: mismo orden de paises, mismos <path d="...">
     (la geometria no se toca).

Entrada:  data/raw/world_map/world-map.svg
          data/processed/who_suicide_rate_by_country_2021.csv
Salida:   data/processed/world_map_country_level_inner.svg
"""
import csv
import re
from pathlib import Path

RAW_MAP = Path("data/raw/world_map/world-map.svg")
RAW_RATES = Path("data/processed/who_suicide_rate_by_country_2021.csv")
OUT = Path("data/processed/world_map_country_level_inner.svg")

GRAY = "#5c564d"
BINS = [
    (2.5, "#f3ece2"),
    (5.0, "#d6ded4"),
    (7.5, "#bad1c6"),
    (10.0, "#9dc4b9"),
    (12.5, "#80b6ab"),
    (15.0, "#64a89d"),
    (17.5, "#479b90"),
    (20.0, "#2b8e82"),
]
TOP_COLOR = "#0e8074"  # 20 o mas


def color_for(value: float) -> str:
    for threshold, color in BINS:
        if value < threshold:
            return color
    return TOP_COLOR


def fmt(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def load_rates() -> dict[str, tuple[str, float]]:
    rates = {}
    with RAW_RATES.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rates[row["iso2"].lower()] = (row["Location"], float(row["FactValueNumeric"]))
    return rates


def split_entities(svg_body: str) -> list[str]:
    """Corta el contenido del <g> raiz en bloques de texto, uno por
    pais/territorio: cada <path id="xx" .../> de una linea, o cada
    <g id="xx">...</g> multi-linea completo."""
    entities = []
    lines = svg_body.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'^\s*<path id="', line):
            entities.append(line)
            i += 1
        elif re.match(r'^\s*<g id="', line):
            block = [line]
            i += 1
            while not re.match(r"^\s*</g>", lines[i]):
                block.append(lines[i])
                i += 1
            block.append(lines[i])
            entities.append("".join(block))
            i += 1
        else:
            i += 1
    return entities


def entity_id(entity: str) -> str:
    return re.match(r'^\s*<(?:path|g) id="([a-zA-Z_]+)"', entity).group(1)


def inject_attrs(entity: str, fill: str, tooltip: str, extra_class: str = "") -> str:
    cls = "country" + (" " + extra_class if extra_class else "")
    attrs = f' fill="{fill}" stroke="var(--paper)" stroke-width="0.4" data-tooltip="{tooltip}" class="{cls}"'
    if entity.lstrip().startswith("<g "):
        return re.sub(r'(<g id="[a-zA-Z_]+")>', r"\1" + attrs + ">", entity, count=1)
    return re.sub(r'(<path id="[a-zA-Z_]+")( d=)', r"\1" + attrs + r"\2", entity, count=1)


def inner_paths(entity: str) -> str:
    """Para el <g id="fk">...</g> de las Malvinas: devuelve solo sus <path>
    hijos, tal cual, para pegarlos adentro de otro grupo."""
    lines = entity.splitlines(keepends=True)
    return "".join(lines[1:-1])


def main() -> None:
    rates = load_rates()
    raw = RAW_MAP.read_text(encoding="utf-8")
    body = re.search(r"<g>\n(.*)\n</g>\n?</svg>", raw, re.S).group(1) + "\n"
    entities = split_entities(body)

    fk = next(e for e in entities if entity_id(e) == "fk")
    entities = [e for e in entities if entity_id(e) != "fk"]

    out_blocks = []
    for entity in entities:
        eid = entity_id(entity)
        info = rates.get(eid)
        if info is None:
            block = inject_attrs(entity, GRAY, "Sin dato de la OMS para este país/territorio")
        elif eid == "ar":
            _, value = info
            tooltip = f"Argentina: {fmt(value)} cada 100.000 (OMS, 2021)"
            # Las Malvinas (fk) se fusionan adentro del grupo de Argentina,
            # antes de su contenido original.
            merged = entity.replace(
                '<g id="ar">\n',
                '<g id="ar">\n' + inner_paths(fk) + "\n",
                1,
            )
            block = inject_attrs(merged, color_for(value), tooltip, extra_class="country-ar")
        else:
            _, value = info
            block = inject_attrs(entity, color_for(value), f"{fmt(value)} cada 100.000 (OMS, 2021)")
        out_blocks.append(block)

    OUT.write_text("".join(out_blocks), encoding="utf-8")
    print(f"{len(entities)} entidades ({sum(1 for e in entities if entity_id(e) in rates)} con dato de la OMS) -> {OUT}")


if __name__ == "__main__":
    main()
