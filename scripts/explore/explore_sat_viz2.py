"""
Visualizaciones EXPLORATORIAS del SAT — segunda tanda, columnas que faltaban:
provincia, lugar del hecho, motivo de origen del registro, clase (civil/fuerza de
seguridad), identidad de género y federal. Mismo criterio que explore_sat_viz.py:
sin pulir, para mirar la forma de los datos.

Salida: output/exploracion/sat/exploracion_sat_2.png
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/sat").mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/clean/SAT-SS-BU_2017-2024_clean.csv", encoding="utf-8")

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("SAT 2017-2024 — exploración rápida, parte 2 (sin pulir)", fontsize=14)

# 1) Provincia (todas, ordenadas)
ax = axes[0, 0]
df["provincia_nombre"].value_counts().plot(kind="barh", ax=ax, color="#4c72b0")
ax.set_title("Casos por provincia (total, sin ajustar por población)")
ax.invert_yaxis()

# 2) Lugar del hecho (ampliado)
ax = axes[0, 1]
df["tipo_lugar_ampliado"].value_counts().plot(kind="barh", ax=ax, color="#55a868")
ax.set_title("Lugar del hecho (ampliado)")
ax.invert_yaxis()

# 3) Motivo de origen del registro
ax = axes[0, 2]
df["motivo_origen_registro"].value_counts().plot(kind="bar", ax=ax, color="#c44e52")
ax.set_title("Motivo de origen del registro")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=30)

# 4) Clase (civil / fuerza de seguridad) — colapsando "sin determinación" aparte
ax = axes[1, 0]
df["suicida_clase"].value_counts().plot(kind="barh", ax=ax, color="#8172b2")
ax.set_title("Clase (civil / fuerza de seguridad)")
ax.invert_yaxis()

# 5) Identidad de género
ax = axes[1, 1]
df["suicida_identidad_genero"].value_counts().plot(kind="bar", ax=ax, color="#937860")
ax.set_title("Identidad de género (50%+ sin determinar)")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=20)

# 6) Federal vs no federal
ax = axes[1, 2]
df["federal"].value_counts().plot(kind="bar", ax=ax, color="#ccb974")
ax.set_title("¿Jurisdicción federal? (muy desbalanceado)")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)

plt.tight_layout()
plt.savefig("output/exploracion/sat/exploracion_sat_2.png", dpi=130)
print("Guardado en output/exploracion/sat/exploracion_sat_2.png")
