"""
Limpieza de la ENFR (Encuesta Nacional de Factores de Riesgo, INDEC), edición
2018 -- la unica que termino usandose en la pieza final (el grafico de
ansiedad/depresión por quintil de ingreso). Mismo grano y columnas que el
original (una fila por persona encuestada) -- solo se corrigen errores
objetivos de origen:

  1. Formato de contenedor: el original es .txt delimitado por "|", con
     comillas. Se re-guarda como CSV estándar (separador coma), mismo
     contenido.
  2. Encoding: verificado con chardet, UTF-8 con BOM -- no había bug de
     encoding acá. Se re-guarda sin BOM.
  3. Nombres de columna: se pasan a minúscula (ya venían en minúscula en esta
     edición, se deja explícito por si cambia en el futuro).
  4. Celdas que son un único espacio en blanco (" "), usado como forma de
     codificar "no aplica / sin dato": se normalizan a NaN real.

Lo que NO se toca (caveats de uso, no errores):
  - El ponderador correcto depende de la variable: bisg06 (ansiedad/
    depresión) es de la entrevista general y corresponde ponderar con wf1p,
    NO con wf3p (que es la sub-muestra de mediciones bioquímicas, wf3p=0 en
    82% de las filas). Se conservan las 3 columnas de ponderador tal cual
    vienen.

Nota: se exploraron también las ediciones 2005, 2009 y 2013 (para chequear si
el mismo gradiente por ingreso se repetía en años anteriores -- ver
scripts/explore/explore_enfr_viz.py y explore_enfr_viz2.py), pero esa
comparación no llegó a la pieza final y los raw de esas 3 ediciones no se
versionaron en el repo. Para volver a correr esos dos scripts de exploración
hace falta reconseguir esos 3 archivos a mano desde
https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-32-68.

Entrada:  data/raw/enfr/2018/ENFR 2018 - Base usuario.txt
Salida:   data/clean/enfr/enfr_2018_clean.csv
"""
import pandas as pd
from pathlib import Path

RAW = Path("data/raw/enfr/2018/ENFR 2018 - Base usuario.txt")
OUT = Path("data/clean/enfr")
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW, sep="|", encoding="utf-8-sig", dtype=str, low_memory=False, quotechar='"')
df.columns = [c.strip().strip('"').lower() for c in df.columns]

n_espacio_puro = 0
for c in df.select_dtypes(include=["object", "str"]).columns:
    antes = df[c]
    despues = antes.str.strip()
    n_espacio_puro += ((antes.notna()) & (antes != despues) & (despues == "")).sum()
    # espacio puro -> NaN; contenido real con espacios de más -> recortado
    despues = despues.replace("", pd.NA)
    df[c] = despues

out_path = OUT / "enfr_2018_clean.csv"
df.to_csv(out_path, index=False, encoding="utf-8")
print(f"2018: {df.shape[0]} filas x {df.shape[1]} cols, "
      f"{n_espacio_puro} celdas de espacio-puro normalizadas a NaN -> {out_path}")
