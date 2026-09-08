"""
Casos del SAT normalizados por población (Censo 2022, INDEC) — tasa anual promedio
cada 100.000 habitantes por provincia, 2017-2024.

Aproximación: se usa la población del Censo 2022 (un solo punto en el tiempo) como
denominador para los 8 años de casos. No ajusta por crecimiento poblacional dentro
del período, pero alcanza para una exploración rápida de qué provincias destacan
una vez que se saca el efecto "más gente = más casos".

Salida: output/exploracion/sat/exploracion_sat_provincia_tasa.png
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/sat").mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/clean/SAT-SS-BU_2017-2024_clean.csv", encoding="utf-8")
pob = pd.read_csv("data/raw/poblacion_censo2022_por_provincia.csv")

casos = df["provincia_nombre"].value_counts().rename_axis("provincia").reset_index(name="casos")
tabla = casos.merge(pob, on="provincia", how="outer", indicator=True)

# chequeo de integridad del merge antes de graficar nada
sin_match = tabla[tabla["_merge"] != "both"]
if len(sin_match):
    print("ATENCIÓN — provincias sin match entre SAT y población:")
    print(sin_match)
tabla = tabla[tabla["_merge"] == "both"].drop(columns="_merge")

N_ANIOS = 8  # 2017-2024
tabla["tasa_anual_100k"] = tabla["casos"] / N_ANIOS / tabla["poblacion_2022"] * 100_000
tabla = tabla.sort_values("tasa_anual_100k", ascending=True)

promedio_pais = df.shape[0] / N_ANIOS / pob["poblacion_2022"].sum() * 100_000

fig, ax = plt.subplots(figsize=(9, 8))
ax.barh(tabla["provincia"], tabla["tasa_anual_100k"], color="#4c72b0")
ax.axvline(promedio_pais, color="#c44e52", linestyle="--", linewidth=1.3,
           label=f"Promedio país: {promedio_pais:.1f}")
ax.set_title("Tasa anual de suicidios cada 100.000 hab. por provincia\n(promedio 2017-2024, población Censo 2022)")
ax.set_xlabel("Casos cada 100.000 hab. por año")
ax.legend()
plt.tight_layout()
plt.savefig("output/exploracion/sat/exploracion_sat_provincia_tasa.png", dpi=130)

print(tabla[["provincia", "casos", "poblacion_2022", "tasa_anual_100k"]]
      .sort_values("tasa_anual_100k", ascending=False).to_string(index=False))
print(f"\nPromedio país: {promedio_pais:.2f} cada 100.000 hab./año")
print("Guardado en output/exploracion/sat/exploracion_sat_provincia_tasa.png")
