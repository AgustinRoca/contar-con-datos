"""
Limpieza de la EMSE 2018 (Encuesta Mundial de Salud Escolar, Ministerio de Salud).
Mismo grano y columnas que el original (una fila por estudiante encuestado) --
a diferencia de los datasets anteriores, la exploración de este NO encontró bugs de
origen (encoding correcto, sin duplicados, ponderador sin ceros/nulos, valores
perdidos ya codificados como NaN real). El único ajuste es cosmético:

  1. Columnas de códigos enteros (edad, sexo, respuestas q1-q81, indicadores qnXX)
     se leen como float por los NaN (quedan "1.0", "2.0" en vez de "1", "2"). Se
     convierten a entero nullable (Int64) las columnas donde el 100% de los valores
     no nulos son enteros -- no toca ninguna columna con decimales reales (weight,
     promedios, etc.).

Entrada:  data/raw/emse/2018/EMSE_DatosAbiertos.csv
Salida:   data/clean/emse/emse_2018_clean.csv
"""
import pandas as pd
from pathlib import Path

RAW = Path("data/raw/emse/2018/EMSE_DatosAbiertos.csv")
OUT = Path("data/clean/emse/emse_2018_clean.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW, sep=None, engine="python")

n_cols_convertidas = 0
for c in df.columns:
    if pd.api.types.is_float_dtype(df[c]):
        no_nulos = df[c].dropna()
        if len(no_nulos) and (no_nulos == no_nulos.round()).all():
            df[c] = df[c].astype("Int64")
            n_cols_convertidas += 1

df.to_csv(OUT, index=False, encoding="utf-8")
print(f"{len(df)} filas x {len(df.columns)} columnas, "
      f"{n_cols_convertidas} columnas de float a entero nullable -> {OUT}")
