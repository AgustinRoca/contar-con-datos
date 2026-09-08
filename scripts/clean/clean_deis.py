"""
Limpieza del DEIS (defunciones por causa, Ministerio de Salud), 8 archivos anuales
2017-2024. Mismo grano y columnas que el original (una fila por combinación
provincia x sexo x causa x muerte materna x grupo de edad, con CUENTA = cantidad de
defunciones) — solo se corrigen errores objetivos de origen:

  1. Encoding: cada año trae su propio encoding de origen (2017-2019 latin1 genuino,
     verificado byte a byte; 2020-2024 UTF-8 con BOM). Se re-guardan los 8 archivos
     como UTF-8 sin BOM, consistente entre años, para que nadie los vuelva a mezclar
     mal como pasó con el SAT.
  2. CAUSA en minúscula: se encontraron 6 códigos CIE-10 en minúscula (k80, k74, b99,
     j18, u07, repartidos en 2018-2021) que romperían cualquier agrupación por causa
     al no calzar con su versión en mayúscula. Se normaliza todo a mayúscula.
  3. Nombres de columna: se les hace strip (por si venían con espacios/BOM pegado).

Lo que NO se toca (caveats de uso, no errores):
  - PROVRES incluye los códigos 98 ("Otro país") y 99 ("Lugar no especificado"),
    además de las 24 provincias. Decidir en el análisis si se excluyen al agregar
    "por provincia" — acá se preservan tal cual vienen.
  - SEXO tiene un código "3" no documentado en el diccionario oficial (que solo
    define 1=Varón, 2=Mujer, 9=Sin especificar): aparece en 10 filas, todas del
    archivo 2024. No se recodifica ni se elimina — es una decisión analítica.
  - GRUPEDAD tiene un esquema de 18 categorías en 2017-2023 y 26 en 2024 (bandas más
    finas). Homologar franjas etarias es una decisión de análisis, no de limpieza.

Entrada:  data/raw/deis/defweb1{7,8,9}.csv, defweb2{0,1,2,3}_0.csv,
          data/raw/datos_sobre_defunciones_2024.csv
Salida:   data/clean/deis/defweb_<anio>_clean.csv (8 archivos)
"""
import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/clean/deis")
OUT.mkdir(parents=True, exist_ok=True)

FILES = {
    2017: (RAW / "deis/defweb17.csv", ",", "latin1"),
    2018: (RAW / "deis/defweb18.csv", ",", "latin1"),
    2019: (RAW / "deis/defweb19.csv", ",", "latin1"),
    2020: (RAW / "deis/defweb20_0.csv", ";", "utf-8-sig"),
    2021: (RAW / "deis/defweb21_0.csv", ";", "utf-8-sig"),
    2022: (RAW / "deis/defweb22_0.csv", ";", "utf-8-sig"),
    2023: (RAW / "deis/defweb23.csv", ";", "utf-8-sig"),
    2024: (RAW / "datos_sobre_defunciones_2024.csv", ";", "utf-8-sig"),
}

resumen = []
for anio, (path, sep, enc) in FILES.items():
    df = pd.read_csv(path, sep=sep, encoding=enc, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    causa_antes = df["CAUSA"].copy()
    df["CAUSA"] = df["CAUSA"].str.upper()
    n_causa_fix = (causa_antes != df["CAUSA"]).sum()

    for c in df.select_dtypes(include=["object", "str"]).columns:
        df[c] = df[c].str.strip()

    out_path = OUT / f"defweb_{anio}_clean.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    resumen.append((anio, len(df), n_causa_fix))
    print(f"{anio}: {len(df)} filas, {n_causa_fix} códigos CAUSA normalizados a mayúscula -> {out_path}")

print("\nResumen:", resumen)
