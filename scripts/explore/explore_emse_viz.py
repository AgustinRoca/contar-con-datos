"""
Visualizaciones EXPLORATORIAS de la EMSE 2018 (data/clean/emse/), sin pulir.

Salida: output/exploracion/emse/exploracion_emse.png
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/emse").mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/clean/emse/emse_2018_clean.csv", low_memory=False)
w = df["weight"]

EDAD_LABELS = {1: "≤11", 2: "12", 3: "13", 4: "14", 5: "15", 6: "16", 7: "17", 8: "18+"}
edad = df["q1"].map(EDAD_LABELS)

ideacion = (df["q24"] == 1)
plan = (df["q25"] == 1)
intento = df["q26"].isin([2, 3, 4, 5])
sexo = df["q2"].map({1: "Varón", 2: "Mujer"})
soledad = df["q22"]
SOLEDAD_LABELS = {1: "Nunca", 2: "Rara vez", 3: "Algunas veces", 4: "Casi siempre", 5: "Siempre"}


def pct(mask, peso):
    sub = pd.DataFrame({"m": mask, "w": peso}).dropna()
    return (sub["m"] * sub["w"]).sum() / sub["w"].sum() * 100


fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
fig.suptitle("EMSE 2018 — ideación/intento suicida en adolescentes, exploración rápida (sin pulir)", fontsize=12)

# 1) Ideación/plan/intento por edad (13 a 17, n robusto)
ax = axes[0]
edades_robustas = ["13", "14", "15", "16", "17"]
tabla = pd.DataFrame({
    "Ideación": [pct(ideacion[edad == e], w[edad == e]) for e in edades_robustas],
    "Plan": [pct(plan[edad == e], w[edad == e]) for e in edades_robustas],
    "Intento": [pct(intento[edad == e], w[edad == e]) for e in edades_robustas],
}, index=edades_robustas)
tabla.plot(kind="bar", ax=ax, color=["#4c72b0", "#dd8452", "#c44e52"])
ax.set_title("Ideación/plan/intento por edad (13-17 años)")
ax.set_xlabel("Edad")
ax.tick_params(axis="x", rotation=0)

# 2) Ideación/intento por sexo
ax = axes[1]
tabla_sexo = pd.DataFrame({
    "Ideación": [pct(ideacion[sexo == s], w[sexo == s]) for s in ["Varón", "Mujer"]],
    "Intento": [pct(intento[sexo == s], w[sexo == s]) for s in ["Varón", "Mujer"]],
}, index=["Varón", "Mujer"])
tabla_sexo.plot(kind="bar", ax=ax, color=["#4c72b0", "#c44e52"])
ax.set_title("Ideación e intento por sexo")
ax.tick_params(axis="x", rotation=0)

# 3) Ideación suicida según frecuencia de sentirse solo/a (últimos 12 meses)
ax = axes[2]
serie = soledad.map(SOLEDAD_LABELS)
orden_soledad = ["Nunca", "Rara vez", "Algunas veces", "Casi siempre", "Siempre"]
tabla_sol = pd.Series([pct(ideacion[serie == s], w[serie == s]) for s in orden_soledad], index=orden_soledad)
tabla_sol.plot(kind="bar", ax=ax, color="#8172b2")
ax.set_title('% con ideación suicida, según frecuencia de\nsentirse solo/a (últimos 12 meses)')
ax.tick_params(axis="x", rotation=20)

plt.tight_layout()
plt.savefig("output/exploracion/emse/exploracion_emse.png", dpi=130)
print("Guardado en output/exploracion/emse/exploracion_emse.png")
print(tabla.round(1))
print()
print(tabla_sexo.round(1))
print()
print(tabla_sol.round(1))
