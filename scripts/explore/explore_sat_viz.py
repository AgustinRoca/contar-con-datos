"""
Visualizaciones EXPLORATORIAS del SAT (data/clean/), sin pretensión de diseño final.
El objetivo es mirar la forma de los datos antes de decidir qué preguntas vale la
pena perseguir, no producir un gráfico para publicar.

Salida: output/exploracion/sat/exploracion_sat.png (grilla de 6 subplots)
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/sat").mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/clean/SAT-SS-BU_2017-2024_clean.csv", encoding="utf-8")

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("SAT 2017-2024 — exploración rápida (sin pulir)", fontsize=14)

# 1) Casos por año
ax = axes[0, 0]
df["anio"].value_counts().sort_index().plot(kind="bar", ax=ax, color="#4c72b0")
ax.set_title("Casos por año")
ax.set_xlabel("")

# 2) Casos por mes (estacionalidad, todos los años juntos)
ax = axes[0, 1]
df["mes"].value_counts().sort_index().plot(kind="bar", ax=ax, color="#4c72b0")
ax.set_title("Casos por mes (2017-2024 acumulado)")
ax.set_xlabel("")

# 3) Franja etaria
ax = axes[0, 2]
orden_edad = ["5-9","10-14","15-19","20-24","25-29","30-34","35-39","40-44","45-49",
              "50-54","55-59","60-64","65-69","70-74","75-79","80-84","85-89","90 y más",
              "Sin determinar"]
df["suicida_tr_edad"].value_counts().reindex(orden_edad).plot(kind="barh", ax=ax, color="#55a868")
ax.set_title("Casos por franja etaria (fina)")
ax.invert_yaxis()

# 4) Sexo
ax = axes[1, 0]
df["suicida_sexo"].value_counts().plot(kind="bar", ax=ax, color="#c44e52")
ax.set_title("Casos por sexo")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)

# 5) Modalidad (ampliado)
ax = axes[1, 1]
df["modalidad_ampliado"].value_counts().head(8).plot(kind="barh", ax=ax, color="#8172b2")
ax.set_title("Modalidad (top 8, ampliado)")
ax.invert_yaxis()

# 6) Hora del hecho: solo la hora 0 se separa en 00:00:00 exacto (posible dato no
#    disponible, según lo visto: 42,3% de esa hora cae justo ahí, muy por encima del
#    piso ~25-30% de las demás horas) vs el resto de esa misma hora. Las demás horas
#    quedan sin desglosar porque su % "en punto" está dentro de lo normal.
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
