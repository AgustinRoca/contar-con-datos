"""
ENFR 2018 -- segunda tanda de exploración: variables que no habíamos mirado.
  A) Ansiedad/depresión por quintil de ingreso.
  B) Ansiedad/depresión por cobertura de salud y nivel de instrucción.
  C) Las 6 dimensiones del bloque EQ-5D (bisg01-06) por franja etaria.

Nota: esto comparaba varias ediciones (2005-2018) hasta que se decidio que
la pieza final solo usa 2018 y se dejo de versionar el raw de las otras --
ver scripts/clean/clean_enfr.py. Ahora todo es unicamente 2018.

Salida: output/exploracion/enfr/exploracion_enfr_quintil.png,
        output/exploracion/enfr/exploracion_enfr_socioecon.png,
        output/exploracion/enfr/exploracion_enfr_eq5d.png
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/enfr").mkdir(parents=True, exist_ok=True)

EDAD_LABELS = {1: "18-24", 2: "25-34", 3: "35-49", 4: "50-64", 5: "65+"}
ORDEN_EDAD = ["18-24", "25-34", "35-49", "50-64", "65+"]

PATH_2018 = "data/clean/enfr/enfr_2018_clean.csv"
PESO = "wf1p"


def pct(g, col="con_ansiedad"):
    return (g[col] * g["peso"]).sum() / g["peso"].sum() * 100


df = pd.read_csv(PATH_2018, dtype=str, low_memory=False)
peso_full = pd.to_numeric(df[PESO], errors="coerce")
depre_full = pd.to_numeric(df["bisg06"], errors="coerce")

# --- A) Por quintil de ingreso ---
fig, ax = plt.subplots(figsize=(8, 5.5))
quintil = pd.to_numeric(df["quintil_uc"], errors="coerce")
sub = pd.DataFrame({"peso": peso_full, "quintil": quintil, "depre": depre_full}).dropna()
sub["con_ansiedad"] = (sub["depre"] >= 2).astype(int)
tabla_q = sub.groupby("quintil").apply(pct, include_groups=False)
tabla_q.index = [f"Quintil {int(i)}" for i in tabla_q.index]
tabla_q.plot(ax=ax, marker="o")
ax.set_title("% con ansiedad/depresión por quintil de ingreso del hogar\n(1 = quintil más pobre, 5 = más rico) -- ENFR 2018")
plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr_quintil.png", dpi=130)
print("Guardado output/exploracion/enfr/exploracion_enfr_quintil.png")
print(tabla_q.round(1))
print()

# --- B) Cobertura de salud y nivel de instrucción ---
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

# --- C) Las 6 dimensiones del EQ-5D por franja etaria ---
DIMENSIONES = {
    "bisg01": "Salud general (mala/regular)",
    "bisg02": "Movilidad",
    "bisg03": "Cuidado personal",
    "bisg04": "Actividades cotidianas",
    "bisg05": "Dolor/malestar",
    "bisg06": "Ansiedad/depresión",
}
edad = pd.to_numeric(df["rango_edad"], errors="coerce").map(EDAD_LABELS)

fig, ax = plt.subplots(figsize=(9, 5.5))
for var, nombre in DIMENSIONES.items():
    val = pd.to_numeric(df[var], errors="coerce")
    # bisg01 (salud general) es escala 1-5 donde >=4 es mala/regular; el resto es 1-3 donde >=2 es "algún problema"
    problema = (val >= 4).astype(int) if var == "bisg01" else (val >= 2).astype(int)
    sub = pd.DataFrame({"peso": peso_full, "edad": edad, "problema": problema}).dropna()
    serie = sub.groupby("edad").apply(lambda g: (g["problema"] * g["peso"]).sum() / g["peso"].sum() * 100,
                                       include_groups=False).reindex(ORDEN_EDAD)
    ax.plot(ORDEN_EDAD, serie.values, marker="o", label=nombre)
ax.set_title("Las 6 dimensiones de salud autoreportada (EQ-5D) por edad, ENFR 2018\n% que reporta algún problema/malestar")
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr_eq5d.png", dpi=130)
print("Guardado output/exploracion/enfr/exploracion_enfr_eq5d.png")
