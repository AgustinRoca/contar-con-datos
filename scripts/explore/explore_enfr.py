"""
Visualizaciones EXPLORATORIAS de la ENFR 2018 (data/clean/enfr/), sin pulir.
Ponderador correcto: wf1p (NO wf3p, ver data/clean/README.md).

Nota: esto comparaba varias ediciones (2005-2018) hasta que se decidio que
la pieza final solo usa 2018 y se dejo de versionar el raw de las otras --
ver scripts/clean/clean_enfr.py. Ahora todo es unicamente 2018.

Salida:
  output/exploracion/enfr/exploracion_enfr.png (por franja etaria, por sexo,
    composición de severidad de la respuesta)
  output/exploracion/enfr/exploracion_enfr_quintil.png (por quintil de
    ingreso del hogar)
  output/exploracion/enfr/exploracion_enfr_socioecon.png (por cobertura de
    salud y nivel de instrucción)
  output/exploracion/enfr/exploracion_enfr_eq5d.png (las 6 dimensiones del
    bloque EQ-5D, bisg01-06, por franja etaria)
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/enfr").mkdir(parents=True, exist_ok=True)

EDAD_LABELS = {1: "18-24", 2: "25-34", 3: "35-49", 4: "50-64", 5: "65+"}
SEXO_LABELS = {1: "Varón", 2: "Mujer"}
ORDEN_EDAD = ["18-24", "25-34", "35-49", "50-64", "65+"]

PATH_2018 = "data/clean/enfr/enfr_2018_clean.csv"
PESO = "wf1p"

df = pd.read_csv(PATH_2018, dtype=str, low_memory=False)
peso_full = pd.to_numeric(df[PESO], errors="coerce")
depre_full = pd.to_numeric(df["bisg06"], errors="coerce")


def pct(g, col="con_ansiedad"):
    return (g[col] * g["peso"]).sum() / g["peso"].sum() * 100


# === 1) por franja etaria, por sexo, composición de severidad ===
edad = pd.to_numeric(df["rango_edad"], errors="coerce")
sexo = pd.to_numeric(df["bhch03"], errors="coerce")
sub = pd.DataFrame({"peso": peso_full, "edad": edad, "sexo": sexo, "depre": depre_full}).dropna(
    subset=["peso", "edad", "depre"])
sub["franja"] = sub["edad"].map(EDAD_LABELS)
sub["sexo_lbl"] = sub["sexo"].map(SEXO_LABELS)
sub["con_ansiedad"] = (sub["depre"] >= 2).astype(int)

n = len(sub)

fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
fig.suptitle(f"ENFR 2018 — ansiedad/depresión autoreportada, exploración rápida (sin pulir)  ·  n={n}",
             fontsize=11)

# 1.1) % con ansiedad/depresión por franja etaria
ax = axes[0]
tabla = sub.dropna(subset=["franja"]).groupby("franja").apply(pct, include_groups=False).reindex(ORDEN_EDAD)
tabla.plot(ax=ax, marker="o")
ax.set_title("% con ansiedad/depresión, por franja etaria")
ax.set_xlabel("")
ax.set_xticks(range(len(ORDEN_EDAD)))
ax.set_xticklabels(ORDEN_EDAD, rotation=0)

# 1.2) % por sexo
ax = axes[1]
tabla_sexo = sub.dropna(subset=["sexo_lbl"]).groupby("sexo_lbl").apply(pct, include_groups=False)
tabla_sexo.plot(kind="bar", ax=ax, color=["#c44e52", "#4c72b0"])
ax.set_title("% con ansiedad/depresión, por sexo")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)

# 1.3) Composición de severidad de respuesta (1/2/3)
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
print()

# === 2) por quintil de ingreso ===
fig, ax = plt.subplots(figsize=(8, 5.5))
quintil = pd.to_numeric(df["quintil_uc"], errors="coerce")
sub_q = pd.DataFrame({"peso": peso_full, "quintil": quintil, "depre": depre_full}).dropna()
sub_q["con_ansiedad"] = (sub_q["depre"] >= 2).astype(int)
tabla_q = sub_q.groupby("quintil").apply(pct, include_groups=False)
tabla_q.index = [f"Quintil {int(i)}" for i in tabla_q.index]
tabla_q.plot(ax=ax, marker="o")
ax.set_title("% con ansiedad/depresión por quintil de ingreso del hogar\n(1 = quintil más pobre, 5 = más rico) -- ENFR 2018")
plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr_quintil.png", dpi=130)
print("Guardado output/exploracion/enfr/exploracion_enfr_quintil.png")
print(tabla_q.round(1))
print()

# === 3) cobertura de salud y nivel de instrucción ===
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
NIVEL_LABELS = {1: "Sin instrucción", 2: "Primario incompl.", 3: "Primario compl.",
                4: "Secundario incompl.", 5: "Secundario compl.", 6: "Terciario incompl.",
                7: "Terciario compl."}
COBERTURA_LABELS = {1: "Obra social/prepaga", 2: "Solo pública"}

cobertura = pd.to_numeric(df["cobertura_salud"], errors="coerce")
nivel = pd.to_numeric(df["nivel_instruccion"], errors="coerce")
base = pd.DataFrame({"peso": peso_full, "depre": depre_full, "cobertura": cobertura, "nivel": nivel}).dropna(
    subset=["peso", "depre"])
base["con_ansiedad"] = (base["depre"] >= 2).astype(int)

sub_c = base[base["cobertura"].isin([1, 2])]
tabla_cob = sub_c.groupby("cobertura").apply(pct, include_groups=False).rename(index=COBERTURA_LABELS)

sub_n = base[base["nivel"].isin(range(1, 8))]
tabla_niv = sub_n.groupby("nivel").apply(pct, include_groups=False)
tabla_niv.index = [NIVEL_LABELS.get(int(i), i) for i in tabla_niv.index]

tabla_cob.plot(kind="bar", ax=axes[0], color="#4c72b0")
axes[0].set_title("% con ansiedad/depresión, por cobertura de salud")
axes[0].tick_params(axis="x", rotation=20)

tabla_niv.loc[list(NIVEL_LABELS.values())].plot(kind="barh", ax=axes[1], color="#4c72b0")
axes[1].set_title("% con ansiedad/depresión, por nivel de instrucción")
axes[1].invert_yaxis()

fig.suptitle("ENFR 2018", fontsize=10)
plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr_socioecon.png", dpi=130)
print("Guardado output/exploracion/enfr/exploracion_enfr_socioecon.png")
print(tabla_cob.round(1))
print(tabla_niv.round(1))
print()

# === 4) las 6 dimensiones del EQ-5D por franja etaria ===
DIMENSIONES = {
    "bisg01": "Salud general (mala/regular)",
    "bisg02": "Movilidad",
    "bisg03": "Cuidado personal",
    "bisg04": "Actividades cotidianas",
    "bisg05": "Dolor/malestar",
    "bisg06": "Ansiedad/depresión",
}
edad_lbl = edad.map(EDAD_LABELS)

fig, ax = plt.subplots(figsize=(9, 5.5))
for var, nombre in DIMENSIONES.items():
    val = pd.to_numeric(df[var], errors="coerce")
    # bisg01 (salud general) es escala 1-5 donde >=4 es mala/regular; el resto es 1-3 donde >=2 es "algún problema"
    problema = (val >= 4).astype(int) if var == "bisg01" else (val >= 2).astype(int)
    sub_dim = pd.DataFrame({"peso": peso_full, "edad": edad_lbl, "problema": problema}).dropna()
    serie = sub_dim.groupby("edad").apply(lambda g: (g["problema"] * g["peso"]).sum() / g["peso"].sum() * 100,
                                           include_groups=False).reindex(ORDEN_EDAD)
    ax.plot(ORDEN_EDAD, serie.values, marker="o", label=nombre)
ax.set_title("Las 6 dimensiones de salud autoreportada (EQ-5D) por edad, ENFR 2018\n% que reporta algún problema/malestar")
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr_eq5d.png", dpi=130)
print("Guardado output/exploracion/enfr/exploracion_enfr_eq5d.png")
