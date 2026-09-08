"""
Visualizaciones EXPLORATORIAS de la ENFR (data/clean/enfr/), sin pulir.
Ponderador correcto por edición: PONDERACION (2005/2009/2013), wf1p (2018 -- NO wf3p,
ver data/clean/README.md).

Salida: output/exploracion/enfr/exploracion_enfr.png
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/enfr").mkdir(parents=True, exist_ok=True)

EDAD_LABELS = {1: "18-24", 2: "25-34", 3: "35-49", 4: "50-64", 5: "65+"}
SEXO_LABELS = {1: "Varón", 2: "Mujer"}
ORDEN_EDAD = ["18-24", "25-34", "35-49", "50-64", "65+"]

EDICIONES = {
    2005: dict(path="data/clean/enfr/enfr_2005_clean.csv", peso="ponderacion",
               sexo="chch03", edad="rangedad", depre="cisg06", offset=True),
    2009: dict(path="data/clean/enfr/enfr_2009_clean.csv", peso="ponderacion",
               sexo="bhch03", edad="rangedad", depre="bisg06", offset=True),
    2013: dict(path="data/clean/enfr/enfr_2013_clean.csv", peso="ponderacion",
               sexo="bhch03", edad="rango_edad", depre="bisg06", offset=False),
    2018: dict(path="data/clean/enfr/enfr_2018_clean.csv", peso="wf1p",
               sexo="bhch03", edad="rango_edad", depre="bisg06", offset=False),
}

registros = []
n_por_anio = {}
for anio, cfg in EDICIONES.items():
    df = pd.read_csv(cfg["path"], dtype=str, low_memory=False)
    peso = pd.to_numeric(df[cfg["peso"]], errors="coerce")
    edad = pd.to_numeric(df[cfg["edad"]], errors="coerce")
    sexo = pd.to_numeric(df[cfg["sexo"]], errors="coerce")
    depre = pd.to_numeric(df[cfg["depre"]], errors="coerce")
    sub = pd.DataFrame({"peso": peso, "edad": edad, "sexo": sexo, "depre": depre}).dropna(
        subset=["peso", "edad", "depre"])
    if cfg["offset"]:
        sub["edad"] = sub["edad"] - 1
    sub["franja"] = sub["edad"].map(EDAD_LABELS)
    sub["sexo_lbl"] = sub["sexo"].map(SEXO_LABELS)
    sub["con_ansiedad"] = (sub["depre"] >= 2).astype(int)
    sub["anio"] = anio
    registros.append(sub)
    n_por_anio[anio] = len(sub)

todo = pd.concat(registros, ignore_index=True)


def pct(g, col="con_ansiedad"):
    return (g[col] * g["peso"]).sum() / g["peso"].sum() * 100


fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
fig.suptitle("ENFR 2005-2018 — ansiedad/depresión autoreportada, exploración rápida (sin pulir)"
             f"  ·  n por edición: {n_por_anio}", fontsize=11)

# 1) % con ansiedad/depresión por franja etaria, una línea por edición
ax = axes[0]
tabla = todo.dropna(subset=["franja"]).groupby(["anio", "franja"]).apply(pct, include_groups=False).unstack("anio")
tabla = tabla.reindex(ORDEN_EDAD)
tabla.plot(ax=ax, marker="o")
ax.set_title("% con ansiedad/depresión, por franja etaria y edición")
ax.set_xlabel("")
ax.set_xticks(range(len(ORDEN_EDAD)))
ax.set_xticklabels(ORDEN_EDAD, rotation=0)

# 2) % por sexo, por edición
ax = axes[1]
tabla_sexo = todo.dropna(subset=["sexo_lbl"]).groupby(["anio", "sexo_lbl"]).apply(pct, include_groups=False).unstack("sexo_lbl")
tabla_sexo.plot(kind="bar", ax=ax, color=["#c44e52", "#4c72b0"])
ax.set_title("% con ansiedad/depresión, por sexo y edición")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)

# 3) Composición de severidad de respuesta (1/2/3) por edición
ax = axes[2]
DEPRE_LABELS = {1: "No ansioso/deprimido", 2: "Moderadamente", 3: "Muy ansioso/deprimido"}
comp = todo.copy()
comp["depre_lbl"] = comp["depre"].map(DEPRE_LABELS)
tabla_comp = comp.groupby(["anio", "depre_lbl"])["peso"].sum().unstack("depre_lbl")
tabla_comp = tabla_comp.div(tabla_comp.sum(axis=1), axis=0) * 100
tabla_comp[["No ansioso/deprimido", "Moderadamente", "Muy ansioso/deprimido"]].plot(
    kind="bar", stacked=True, ax=ax, color=["#8fbfe0", "#f2a154", "#c44e52"])
ax.set_title("Composición de severidad, por edición")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)
ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr.png", dpi=130)
print("Guardado en output/exploracion/enfr/exploracion_enfr.png")
print(tabla.round(1))
