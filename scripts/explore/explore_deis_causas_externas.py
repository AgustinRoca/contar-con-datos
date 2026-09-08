"""
Suicidio comparado únicamente contra el resto de las CAUSAS EXTERNAS (capítulo
CIE-10 V01-Y98: accidentes, homicidios, eventos de intención no determinada, etc.),
que es el capítulo al que el suicidio pertenece formalmente -- para ver su peso
relativo dentro de ese grupo específico, no contra enfermedades.

Salida: output/exploracion/deis/exploracion_deis_causas_externas.png
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/deis").mkdir(parents=True, exist_ok=True)

ANIOS = range(2017, 2025)
dfs = []
for anio in ANIOS:
    d = pd.read_csv(f"data/clean/deis/defweb_{anio}_clean.csv", dtype=str)
    dfs.append(d)
df = pd.concat(dfs, ignore_index=True)
df["CUENTA"] = pd.to_numeric(df["CUENTA"], errors="coerce")

SUIC = {f"X{n}" for n in range(60, 85)}


def subgrupo_causa_externa(causa: str) -> str:
    letra, numero = causa[0], int(causa[1:])
    if letra == "X" and 60 <= numero <= 84:
        return "SUICIDIO (X60-X84)"
    if letra == "V":
        return "Accidentes de tránsito (V)"
    if letra == "W":
        return "Otros accidentes: caídas, ahogamiento, etc. (W)"
    if letra == "X" and numero <= 59:
        return "Otros accidentes: envenenamiento, fuego, etc. (X00-X59)"
    if (letra == "X" and numero >= 85) or (letra == "Y" and numero <= 9):
        return "Agresiones / homicidios (X85-Y09)"
    if letra == "Y" and 10 <= numero <= 34:
        return "Intención no determinada (Y10-Y34)"
    if letra == "Y" and numero >= 35:
        return "Otras causas externas (Y35-Y98)"
    return None  # no es capítulo de causas externas


df["subgrupo_externa"] = df["CAUSA"].map(subgrupo_causa_externa)
externas = df.dropna(subset=["subgrupo_externa"])

tabla = externas.groupby("subgrupo_externa")["CUENTA"].sum().sort_values()
total_externas = tabla.sum()
pct_suicidio = tabla["SUICIDIO (X60-X84)"] / total_externas * 100

colores = ["#c44e52" if s == "SUICIDIO (X60-X84)" else "#4c72b0" for s in tabla.index]

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.barh(tabla.index, tabla.values, color=colores)
for i, (etiqueta, valor) in enumerate(tabla.items()):
    ax.text(valor + total_externas * 0.01, i, f"{valor:,.0f}".replace(",", "."),
            va="center", fontsize=8)
ax.set_title(
    f"Suicidio dentro del capítulo de causas externas (V01-Y98), 2017-2024\n"
    f"Total causas externas: {total_externas:,.0f} · Suicidio: {pct_suicidio:.1f}% de ese total"
    .replace(",", ".")
)
plt.tight_layout()
plt.savefig("output/exploracion/deis/exploracion_deis_causas_externas.png", dpi=130)
print("Guardado en output/exploracion/deis/exploracion_deis_causas_externas.png")
print(tabla.sort_values(ascending=False).to_string())
print(f"\nSuicidio = {pct_suicidio:.1f}% de todas las causas externas de muerte.")
