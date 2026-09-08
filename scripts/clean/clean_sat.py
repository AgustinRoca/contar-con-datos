"""
Limpieza del SAT (Sistema de Alerta Temprana de Suicidios), Ministerio de Seguridad.

Sigue siendo un dato crudo (misma granularidad: una fila por víctima, mismas columnas,
sin agregar ni recodificar nada) pero con los problemas de calidad detectados en la
exploración corregidos:

  1. Encoding: el archivo original es UTF-8; se re-guarda explícitamente como UTF-8
     para evitar que alguien lo vuelva a abrir con latin1 por error (como pasó antes
     en este proyecto) y arrastre mojibake en texto y nombres de columna.
  2. Espacios en blanco al inicio/final de todas las columnas de texto (encontrado en
     motivo_origen_registro: "Otros" y "Otros " conviven como si fueran categorías
     distintas).

Lo que NO se toca (son características del dato, no bugs):
  - hora_hecho: se detectó una acumulación sospechosa en 00:00:00 y 12:00:00 (posibles
    valores por defecto/estimados). No se puede "arreglar" sin información adicional;
    queda documentado como caveat de uso, no como corrección.
  - suicida_identidad_genero: 50,4% "Sin determinar". Es la completitud real del
    registro, no un error de formato.
  - id_hecho no es único (11 hechos con 2 víctimas, probables pactos): es la estructura
    real del dato, no un duplicado a eliminar.

Entrada:  data/raw/SAT-SS-BU_2017-2024.csv
Salida:   data/clean/SAT-SS-BU_2017-2024_clean.csv
"""
import pandas as pd
from pathlib import Path

RAW = Path("data/raw/SAT-SS-BU_2017-2024.csv")
OUT = Path("data/clean/SAT-SS-BU_2017-2024_clean.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW, encoding="utf-8")

n_filas_in = len(df)

# 1) Strip de espacios en todas las columnas de texto
str_cols = df.select_dtypes(include="object").columns
cambios_por_columna = {}
for c in str_cols:
    antes = df[c]
    despues = antes.str.strip()
    # antes.notna() evita contar NaN como "cambiado" (NaN != NaN da True)
    n = (antes.notna() & (antes != despues)).sum()
    if n:
        cambios_por_columna[c] = int(n)
    df[c] = despues
cambios_strip = sum(cambios_por_columna.values())

df.to_csv(OUT, index=False, encoding="utf-8")

print(f"Filas: {n_filas_in} -> {len(df)} (sin cambio de grano)")
print(f"Valores con espacios recortados: {cambios_strip}, por columna: {cambios_por_columna}")
print(f"motivo_origen_registro ahora: {sorted(df['motivo_origen_registro'].unique())}")
print(f"Guardado en {OUT}")
