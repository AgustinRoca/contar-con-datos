"""
Visualizaciones EXPLORATORIAS del SAT (data/clean/), sin pretensión de diseño
final. El objetivo es mirar la forma de los datos antes de decidir qué
preguntas vale la pena perseguir, no producir un gráfico para publicar.

Salida:
  output/exploracion/sat/exploracion_sat.png (grilla de 6 subplots: por año,
    mes, franja etaria fina, sexo, modalidad, hora del hecho)
  output/exploracion/sat/exploracion_sat_2.png (segunda tanda: provincia,
    lugar del hecho, motivo de origen del registro, clase, identidad de
    género, federal)
  output/exploracion/sat/exploracion_sat_provincia_tasa.png (casos
    normalizados por población del Censo 2022, tasa anual cada 100.000
    hab. por provincia)
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/sat").mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/clean/SAT-SS-BU_2017-2024_clean.csv", encoding="utf-8")

# === 1) grilla de 6 subplots: forma general de los datos ===
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("SAT 2017-2024 — exploración rápida (sin pulir)", fontsize=14)

# 1.1) Casos por año
ax = axes[0, 0]
df["anio"].value_counts().sort_index().plot(kind="bar", ax=ax, color="#4c72b0")
ax.set_title("Casos por año")
ax.set_xlabel("")

# 1.2) Casos por mes (estacionalidad, todos los años juntos)
ax = axes[0, 1]
df["mes"].value_counts().sort_index().plot(kind="bar", ax=ax, color="#4c72b0")
ax.set_title("Casos por mes (2017-2024 acumulado)")
ax.set_xlabel("")

# 1.3) Franja etaria
ax = axes[0, 2]
orden_edad = ["5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49",
              "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85-89", "90 y más",
              "Sin determinar"]
df["suicida_tr_edad"].value_counts().reindex(orden_edad).plot(kind="barh", ax=ax, color="#55a868")
ax.set_title("Casos por franja etaria (fina)")
ax.invert_yaxis()

# 1.4) Sexo
ax = axes[1, 0]
df["suicida_sexo"].value_counts().plot(kind="bar", ax=ax, color="#c44e52")
ax.set_title("Casos por sexo")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)

# 1.5) Modalidad (ampliado)
ax = axes[1, 1]
df["modalidad_ampliado"].value_counts().head(8).plot(kind="barh", ax=ax, color="#8172b2")
ax.set_title("Modalidad (top 8, ampliado)")
ax.invert_yaxis()

# 1.6) Hora del hecho: solo la hora 0 se separa en 00:00:00 exacto (posible dato no
#      disponible, según lo visto: 42,3% de esa hora cae justo ahí, muy por encima del
#      piso ~25-30% de las demás horas) vs el resto de esa misma hora. Las demás horas
#      quedan sin desglosar porque su % "en punto" está dentro de lo normal.
ax = axes[1, 2]
t = pd.to_datetime(df["hora_hecho"], format="%H:%M:%S", errors="coerce")
es_00_00_00 = df["hora_hecho"] == "00:00:00"
tabla_horas = pd.DataFrame({"hora": t.dt.hour, "es_00_00_00": es_00_00_00}).dropna(subset=["hora"])
conteo = tabla_horas.groupby(["hora", "es_00_00_00"]).size().unstack(fill_value=0)
conteo = conteo.reindex(range(24), fill_value=0)
conteo[False].plot(kind="bar", ax=ax, color="#4c72b0", label="Resto")
conteo[True].plot(kind="bar", ax=ax, bottom=conteo[False], color="#e08214", label="00:00:00 (posible dato no disponible)")
ax.set_title("Casos por hora — naranja = 00:00:00 exacto")
ax.set_xlabel("")
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("output/exploracion/sat/exploracion_sat.png", dpi=130)
print("Guardado en output/exploracion/sat/exploracion_sat.png")

# === 2) segunda tanda: columnas que faltaban ===
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("SAT 2017-2024 — exploración rápida, parte 2 (sin pulir)", fontsize=14)

# 2.1) Provincia (todas, ordenadas)
ax = axes[0, 0]
df["provincia_nombre"].value_counts().plot(kind="barh", ax=ax, color="#4c72b0")
ax.set_title("Casos por provincia (total, sin ajustar por población)")
ax.invert_yaxis()

# 2.2) Lugar del hecho (ampliado)
ax = axes[0, 1]
df["tipo_lugar_ampliado"].value_counts().plot(kind="barh", ax=ax, color="#55a868")
ax.set_title("Lugar del hecho (ampliado)")
ax.invert_yaxis()

# 2.3) Motivo de origen del registro
ax = axes[0, 2]
df["motivo_origen_registro"].value_counts().plot(kind="bar", ax=ax, color="#c44e52")
ax.set_title("Motivo de origen del registro")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=30)

# 2.4) Clase (civil / fuerza de seguridad) — colapsando "sin determinación" aparte
ax = axes[1, 0]
df["suicida_clase"].value_counts().plot(kind="barh", ax=ax, color="#8172b2")
ax.set_title("Clase (civil / fuerza de seguridad)")
ax.invert_yaxis()

# 2.5) Identidad de género
ax = axes[1, 1]
df["suicida_identidad_genero"].value_counts().plot(kind="bar", ax=ax, color="#937860")
ax.set_title("Identidad de género (50%+ sin determinar)")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=20)

# 2.6) Federal vs no federal
ax = axes[1, 2]
df["federal"].value_counts().plot(kind="bar", ax=ax, color="#ccb974")
ax.set_title("¿Jurisdicción federal? (muy desbalanceado)")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)

plt.tight_layout()
plt.savefig("output/exploracion/sat/exploracion_sat_2.png", dpi=130)
print("Guardado en output/exploracion/sat/exploracion_sat_2.png")

# === 3) tasa por provincia, normalizada por población (Censo 2022) ===
# Aproximación: se usa la población del Censo 2022 (un solo punto en el tiempo) como
# denominador para los 8 años de casos. No ajusta por crecimiento poblacional dentro
# del período, pero alcanza para una exploración rápida de qué provincias destacan
# una vez que se saca el efecto "más gente = más casos".
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
