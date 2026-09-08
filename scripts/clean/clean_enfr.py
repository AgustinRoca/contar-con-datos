"""
Limpieza de la ENFR (Encuesta Nacional de Factores de Riesgo, INDEC), 4 ediciones
(2005, 2009, 2013, 2018). Mismo grano y columnas que el original (una fila por
persona encuestada) -- solo se corrigen errores objetivos de origen:

  1. Formato de contenedor: los 4 originales son .txt delimitados por "|", con
     comillas inconsistentes entre ediciones (2005/2009 sin comillas, 2013/2018 con
     comillas). Se re-guardan los 4 como CSV estándar (separador coma, comillas
     donde corresponda), mismo contenido.
  2. Encoding: verificado con chardet, las 4 ediciones son UTF-8 (con o sin BOM) --
     no había bug de encoding acá. Se re-guardan sin BOM, consistentes entre sí.
  3. Nombres de columna: se pasan a minúscula en las 4 ediciones (2005/2009/2013
     venían en MAYÚSCULA, 2018 en minúscula) -- mismo nombre, sin recodificar a un
     esquema común entre años, eso es una decisión de análisis.
  4. Celdas que son un único espacio en blanco (" "): en 2005 y 2009 se usa un
     espacio como forma de codificar "no aplica / sin dato" en más de 1,5 y 2,8
     millones de celdas respectivamente (verificado: son SIEMPRE espacio puro, cero
     casos de texto real con espacios de más). Se normalizan a NaN real.

Lo que NO se toca (caveats de uso, no errores -- ver data/clean/README.md):
  - El ponderador correcto de 2018 depende de la variable: bisg06 (ansiedad/
    depresión) es de la entrevista general y corresponde ponderar con wf1p, NO con
    wf3p (que es la sub-muestra de mediciones bioquímicas, wf3p=0 en 82% de las
    filas). Se conservan las 3 columnas de ponderador tal cual vienen.
  - RANGEDAD en 2005/2009 parece venir corrida un código respecto de 2013/2018
    (códigos 2-6 en vez de 1-5). No se re-mapea acá -- es una inferencia, no un
    error tipográfico evidente.

Entrada:  data/raw/enfr/{2005,2009,2013,2018}/...
Salida:   data/clean/enfr/enfr_<año>_clean.csv (4 archivos)
"""
import pandas as pd
from pathlib import Path

RAW = Path("data/raw/enfr")
OUT = Path("data/clean/enfr")
OUT.mkdir(parents=True, exist_ok=True)

FILES = {
    2005: (RAW / "2005/ENFR-2005 Base Usuario.txt", {}),
    2009: (RAW / "2009/ENFR-2009 Base Usuario.txt", {}),
    2013: (RAW / "2013/ENFR2013_baseusuario.txt", {"quotechar": '"'}),
    2018: (RAW / "2018/ENFR 2018 - Base usuario.txt", {"quotechar": '"'}),
}

for anio, (path, kw) in FILES.items():
    df = pd.read_csv(path, sep="|", encoding="utf-8-sig", dtype=str, low_memory=False, **kw)
    df.columns = [c.strip().strip('"').lower() for c in df.columns]

    n_espacio_puro = 0
    for c in df.select_dtypes(include=["object", "str"]).columns:
        antes = df[c]
        despues = antes.str.strip()
        n_espacio_puro += ((antes.notna()) & (antes != despues) & (despues == "")).sum()
        # espacio puro -> NaN; contenido real con espacios de más -> recortado
        despues = despues.replace("", pd.NA)
        df[c] = despues

    out_path = OUT / f"enfr_{anio}_clean.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"{anio}: {df.shape[0]} filas x {df.shape[1]} cols, "
          f"{n_espacio_puro} celdas de espacio-puro normalizadas a NaN -> {out_path}")
