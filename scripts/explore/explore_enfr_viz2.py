"""
ENFR -- segunda tanda de exploración: variables que no habíamos mirado.
  A) Ansiedad/depresión por quintil de ingreso, 4 ediciones.
  B) Ansiedad/depresión por cobertura de salud y nivel de instrucción, 2013 y 2018
     (únicas ediciones con esas variables).
  C) Las 6 dimensiones del bloque EQ-5D (bisg01-06) por franja etaria, 2018.

Salida: output/exploracion/enfr/exploracion_enfr_quintil.png, output/exploracion/enfr/exploracion_enfr_socioecon.png,
        output/exploracion/enfr/exploracion_enfr_eq5d.png
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/enfr").mkdir(parents=True, exist_ok=True)

EDAD_LABELS = {1: "18-24", 2: "25-34", 3: "35-49", 4: "50-64", 5: "65+"}
ORDEN_EDAD = ["18-24", "25-34", "35-49", "50-64", "65+"]

EDICIONES = {
    2005: dict(path="data/clean/enfr/enfr_2005_clean.csv", peso="ponderacion",
               edad="rangedad", depre="cisg06", quintil="itf_uc_quintiles", offset=True),
    2009: dict(path="data/clean/enfr/enfr_2009_clean.csv", peso="ponderacion",
               edad="rangedad", depre="bisg06", quintil="itf_uc_quintiles", offset=True),
    2013: dict(path="data/clean/enfr/enfr_2013_clean.csv", peso="ponderacion",
               edad="rango_edad", depre="bisg06", quintil="itf_uc_quintiles", offset=False),
    2018: dict(path="data/clean/enfr/enfr_2018_clean.csv", peso="wf1p",
               edad="rango_edad", depre="bisg06", quintil="quintil_uc", offset=False),
}


def pct(g, col="con_ansiedad"):
    return (g[col] * g["peso"]).sum() / g["peso"].sum() * 100


# --- A) Por quintil de ingreso ---
fig, ax = plt.subplots(figsize=(8, 5.5))
tabla_q = {}
for anio, cfg in EDICIONES.items():
    df = pd.read_csv(cfg["path"], dtype=str, low_memory=False)
    peso = pd.to_numeric(df[cfg["peso"]], errors="coerce")
    quintil = pd.to_numeric(df[cfg["quintil"]], errors="coerce")
    depre = pd.to_numeric(df[cfg["depre"]], errors="coerce")
    sub = pd.DataFrame({"peso": peso, "quintil": quintil, "depre": depre}).dropna()
    sub["con_ansiedad"] = (sub["depre"] >= 2).astype(int)
    tabla_q[anio] = sub.groupby("quintil").apply(pct, include_groups=False)
tabla_q = pd.DataFrame(tabla_q)
tabla_q.index = [f"Quintil {int(i)}" for i in tabla_q.index]
tabla_q.plot(ax=ax, marker="o")
ax.set_title("% con ansiedad/depresión por quintil de ingreso del hogar\n(1 = quintil más pobre, 5 = más rico)")
plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr_quintil.png", dpi=130)
print("Guardado output/exploracion/enfr/exploracion_enfr_quintil.png")
print(tabla_q.round(1))
print()

# --- B) Cobertura de salud y nivel de instrucción, 2013 y 2018 ---
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
NIVEL_LABELS = {1: "Sin instrucción", 2: "Primario incompl.", 3: "Primario compl.",
                4: "Secundario incompl.", 5: "Secundario compl.", 6: "Terciario incompl.",
                7: "Terciario compl."}
COBERTURA_LABELS = {1: "Obra social/prepaga", 2: "Solo pública"}

tabla_cob = {}
tabla_niv = {}
for anio in (2013, 2018):
    cfg = EDICIONES[anio]
    df = pd.read_csv(cfg["path"], dtype=str, low_memory=False)
    peso = pd.to_numeric(df[cfg["peso"]], errors="coerce")
    depre = pd.to_numeric(df[cfg["depre"]], errors="coerce")
    cobertura = pd.to_numeric(df["cobertura_salud"], errors="coerce")
    nivel = pd.to_numeric(df["nivel_instruccion"], errors="coerce")
    base = pd.DataFrame({"peso": peso, "depre": depre, "cobertura": cobertura, "nivel": nivel}).dropna(
        subset=["peso", "depre"])
    base["con_ansiedad"] = (base["depre"] >= 2).astype(int)

    sub_c = base[base["cobertura"].isin([1, 2])]
    tabla_cob[anio] = sub_c.groupby("cobertura").apply(pct, include_groups=False).rename(index=COBERTURA_LABELS)

    sub_n = base[base["nivel"].isin(range(1, 8))]
    tabla_niv[anio] = sub_n.groupby("nivel").apply(pct, include_groups=False)

tabla_cob = pd.DataFrame(tabla_cob)
tabla_niv = pd.DataFrame(tabla_niv)
tabla_niv.index = [NIVEL_LABELS.get(int(i), i) for i in tabla_niv.index]

tabla_cob.plot(kind="bar", ax=axes[0], color=["#4c72b0", "#c44e52"])
axes[0].set_title("% con ansiedad/depresión, por cobertura de salud")
axes[0].tick_params(axis="x", rotation=20)

tabla_niv.loc[list(NIVEL_LABELS.values())].plot(kind="barh", ax=axes[1], color=["#4c72b0", "#c44e52"])
axes[1].set_title("% con ansiedad/depresión, por nivel de instrucción")
axes[1].invert_yaxis()

plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr_socioecon.png", dpi=130)
print("Guardado output/exploracion/enfr/exploracion_enfr_socioecon.png")
print(tabla_cob.round(1))
print(tabla_niv.round(1))
print()

# --- C) Las 6 dimensiones del EQ-5D por franja etaria, 2018 ---
DIMENSIONES = {
    "bisg01": "Salud general (mala/regular)",
    "bisg02": "Movilidad",
    "bisg03": "Cuidado personal",
    "bisg04": "Actividades cotidianas",
    "bisg05": "Dolor/malestar",
    "bisg06": "Ansiedad/depresión",
}
df18 = pd.read_csv(EDICIONES[2018]["path"], dtype=str, low_memory=False)
peso = pd.to_numeric(df18[EDICIONES[2018]["peso"]], errors="coerce")
edad = pd.to_numeric(df18[EDICIONES[2018]["edad"]], errors="coerce").map(EDAD_LABELS)

fig, ax = plt.subplots(figsize=(9, 5.5))
for var, nombre in DIMENSIONES.items():
    val = pd.to_numeric(df18[var], errors="coerce")
    # bisg01 (salud general) es escala 1-5 donde >=4 es mala/regular; el resto es 1-3 donde >=2 es "algún problema"
    problema = (val >= 4).astype(int) if var == "bisg01" else (val >= 2).astype(int)
    sub = pd.DataFrame({"peso": peso, "edad": edad, "problema": problema}).dropna()
    serie = sub.groupby("edad").apply(lambda g: (g["problema"] * g["peso"]).sum() / g["peso"].sum() * 100,
                                       include_groups=False).reindex(ORDEN_EDAD)
    ax.plot(ORDEN_EDAD, serie.values, marker="o", label=nombre)
ax.set_title("Las 6 dimensiones de salud autoreportada (EQ-5D) por edad, ENFR 2018\n% que reporta algún problema/malestar")
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig("output/exploracion/enfr/exploracion_enfr_eq5d.png", dpi=130)
print("Guardado output/exploracion/enfr/exploracion_enfr_eq5d.png")
