"""
Visualizaciones EXPLORATORIAS de la ENFR 2018 (data/clean/enfr/), sin pulir.
Ponderador correcto: wf1p (NO wf3p, ver data/clean/README.md).

Nota: esto comparaba 4 ediciones (2005/2009/2013/2018) hasta que se decidio
que la pieza final solo usa 2018 y se dejo de versionar el raw de las otras
3 -- ver scripts/clean/clean_enfr.py. Ahora muestra unicamente 2018.

Salida: output/exploracion/enfr/exploracion_enfr.png
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/enfr").mkdir(parents=True, exist_ok=True)

EDAD_LABELS = {1: "18-24", 2: "25-34", 3: "35-49", 4: "50-64", 5: "65+"}
SEXO_LABELS = {1: "Varón", 2: "Mujer"}
ORDEN_EDAD = ["18-24", "25-34", "35-49", "50-64", "65+"]

df = pd.read_csv("data/clean/enfr/enfr_2018_clean.csv", dtype=str, low_memory=False)
peso = pd.to_numeric(df["wf1p"], errors="coerce")
edad = pd.to_numeric(df["rango_edad"], errors="coerce")
sexo = pd.to_numeric(df["bhch03"], errors="coerce")
depre = pd.to_numeric(df["bisg06"], errors="coerce")
sub = pd.DataFrame({"peso": peso, "edad": edad, "sexo": sexo, "depre": depre}).dropna(
    subset=["peso", "edad", "depre"])
sub["franja"] = sub["edad"].map(EDAD_LABELS)
sub["sexo_lbl"] = sub["sexo"].map(SEXO_LABELS)
sub["con_ansiedad"] = (sub["depre"] >= 2).astype(int)

n = len(sub)


def pct(g, col="con_ansiedad"):
    return (g[col] * g["peso"]).sum() / g["peso"].sum() * 100


fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
fig.suptitle(f"ENFR 2018 — ansiedad/depresión autoreportada, exploración rápida (sin pulir)  ·  n={n}",
             fontsize=11)

# 1) % con ansiedad/depresión por franja etaria
ax = axes[0]
tabla = sub.dropna(subset=["franja"]).groupby("franja").apply(pct, include_groups=False).reindex(ORDEN_EDAD)
tabla.plot(ax=ax, marker="o")
ax.set_title("% con ansiedad/depresión, por franja etaria")
ax.set_xlabel("")
ax.set_xticks(range(len(ORDEN_EDAD)))
ax.set_xticklabels(ORDEN_EDAD, rotation=0)

# 2) % por sexo
ax = axes[1]
tabla_sexo = sub.dropna(subset=["sexo_lbl"]).groupby("sexo_lbl").apply(pct, include_groups=False)
tabla_sexo.plot(kind="bar", ax=ax, color=["#c44e52", "#4c72b0"])
ax.set_title("% con ansiedad/depresión, por sexo")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)

# 3) Composición de severidad de respuesta (1/2/3)
ax = axes[2]
DEPRE_LABELS = {1: "No ansioso/deprimido", 2: "Moderadamente", 3: "Muy ansioso/deprimido"}
comp = sub.copy()
comp["depre_lbl"] = comp["depre"].map(DEPRE_LABELS)
tabla_comp = comp.groupby("depre_lbl")["peso"].sum()
tabla_comp = (tabla_comp / tabla_comp.sum() * 100).reindex(
    ["No ansioso/deprimido", "Moderadamente", "Muy ansioso/deprimido"])
tabla_comp.plot(kind="bar", ax=ax, color=["#8fbfe0", "#f2a154", "#c44e52"])
ax.set_title("Composición de severidad")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=20)

plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr.png", dpi=130)
print("Guardado en output/exploracion/enfr/exploracion_enfr.png")
print(tabla.round(1))
