"""
Visualizaciones EXPLORATORIAS del DEIS (data/clean/deis/), sin pulir.
Recortado solo a suicidio (CIE-10 X60-X84) -- no se muestra nada de mortalidad
general ni de otras causas.

Salida: output/exploracion/deis/exploracion_deis.png
"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

Path("output/exploracion/deis").mkdir(parents=True, exist_ok=True)

ANIOS = range(2017, 2025)
dfs = []
for anio in ANIOS:
    d = pd.read_csv(f"data/clean/deis/defweb_{anio}_clean.csv", dtype=str)
    d["anio"] = anio
    dfs.append(d)
df = pd.concat(dfs, ignore_index=True)
df["CUENTA"] = pd.to_numeric(df["CUENTA"], errors="coerce")

SUIC = {f"X{n}" for n in range(60, 85)}
suic = df[df["CAUSA"].isin(SUIC)]

CAUSA_DESC = pd.read_excel("data/raw/deis/descdef1.xlsx", sheet_name="CODMUER")
causa_map = dict(zip(CAUSA_DESC["CODIGO"], CAUSA_DESC["VALOR"]))
causa_map["U07"] = "COVID-19 (sin descripción en el diccionario oficial)"

PROV = {
    "02": "CABA", "06": "Buenos Aires", "10": "Catamarca", "14": "Córdoba",
    "18": "Corrientes", "22": "Chaco", "26": "Chubut", "30": "Entre Ríos",
    "34": "Formosa", "38": "Jujuy", "42": "La Pampa", "46": "La Rioja",
    "50": "Mendoza", "54": "Misiones", "58": "Neuquén", "62": "Río Negro",
    "66": "Salta", "70": "San Juan", "74": "San Luis", "78": "Santa Cruz",
    "82": "Santa Fe", "86": "Santiago del Estero", "90": "Tucumán",
    "94": "Tierra del Fuego", "98": "Otro país",
}

fig, axes = plt.subplots(2, 2, figsize=(13, 10))
fig.suptitle("DEIS 2017-2024 — suicidios (CIE-10 X60-X84), exploración rápida (sin pulir)", fontsize=13)

# 1) Suicidios por año
ax = axes[0, 0]
suic.groupby("anio")["CUENTA"].sum().plot(kind="bar", ax=ax, color="#c44e52")
ax.set_title("Suicidios por año")
ax.set_xlabel("")

# 2) Suicidios por sexo
ax = axes[0, 1]
sexo_map = {"1": "Varón", "2": "Mujer", "9": "Sin especificar", "3": "Cód. 3 (sin doc.)"}
tabla_sexo = suic.groupby("SEXO")["CUENTA"].sum().rename(index=sexo_map)
tabla_sexo.plot(kind="bar", ax=ax, color="#8172b2")
ax.set_title("Suicidios por sexo")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=20)

# 3) Suicidios por provincia normalizados por población
ax = axes[1, 0]
pob = pd.read_csv("data/raw/poblacion_censo2022_por_provincia.csv")
suic_prov = suic[~suic["PROVRES"].isin(["98", "99"])].copy()
suic_prov["provincia"] = suic_prov["PROVRES"].map(PROV)
casos_prov = suic_prov.groupby("provincia")["CUENTA"].sum().rename("casos").reset_index()
tabla = casos_prov.merge(pob, on="provincia", how="inner")
tabla["tasa_anual_100k"] = tabla["casos"] / 8 / tabla["poblacion_2022"] * 100_000
tabla = tabla.sort_values("tasa_anual_100k")
ax.barh(tabla["provincia"], tabla["tasa_anual_100k"], color="#937860")
ax.set_title("Tasa de suicidio cada 100.000 hab./año, por provincia")
ax.tick_params(axis="y", labelsize=7)

# 4) Suicidios por franja etaria fina, solo 2017-2023 (esquema estable de 18 categorías)
ax = axes[1, 1]
suic_edad_estable = suic[suic["anio"] != 2024]
tabla_edad = suic_edad_estable.groupby("GRUPEDAD")["CUENTA"].sum().sort_index()
ax.barh(tabla_edad.index, tabla_edad.values, color="#ccb974")
ax.set_title("Suicidios por franja etaria, 2017-2023\n(excluye 2024, esquema de edad distinto)")
ax.tick_params(axis="y", labelsize=7)
ax.invert_yaxis()

plt.tight_layout()
plt.savefig("output/exploracion/deis/exploracion_deis.png", dpi=130)
print("Guardado en output/exploracion/deis/exploracion_deis.png")

# --- Figura aparte: suicidio comparado contra el total de muertes, agrupando TODAS
#     las causas por capítulo CIE-10 (no una selección ad-hoc de categorías). El
#     único capítulo que se desarma es el XX (causas externas, V01-Y98): ahí se
#     separa "Suicidio" (X60-X84) del resto de las causas externas (accidentes,
#     homicidios, etc.), porque es justamente lo que se quiere destacar.
total_muertes = df["CUENTA"].sum()
total_suicidios = suic["CUENTA"].sum()
pct_suicidio = total_suicidios / total_muertes * 100


def capitulo_cie10(causa: str) -> str:
    letra, numero = causa[0], int(causa[1:])
    if letra in "AB":
        return "Infecciosas y parasitarias (A-B)"
    if letra == "C":
        return "Tumores (C00-D48)"
    if letra == "D":
        return "Tumores (C00-D48)" if numero <= 48 else "Sangre (D50-D89)"
    if letra == "E":
        return "Endócrinas y metabólicas (E)"
    if letra == "F":
        return "Mentales y del comportamiento (F)"
    if letra == "G":
        return "Sistema nervioso (G)"
    if letra == "H":
        return "Ojo (H00-H59)" if numero <= 59 else "Oído (H60-H95)"
    if letra == "I":
        return "Sistema circulatorio (I)"
    if letra == "J":
        return "Sistema respiratorio (J)"
    if letra == "K":
        return "Sistema digestivo (K)"
    if letra == "L":
        return "Piel (L)"
    if letra == "M":
        return "Osteomuscular (M)"
    if letra == "N":
        return "Genitourinario (N)"
    if letra == "O":
        return "Embarazo y parto (O)"
    if letra == "P":
        return "Afecciones perinatales (P)"
    if letra == "Q":
        return "Malformaciones congénitas (Q)"
    if letra == "R":
        return "Síntomas/signos mal definidos (R)"
    if letra in "ST":
        return "Traumatismos y envenenamientos (S-T)"
    if letra == "X" and 60 <= numero <= 84:
        return "SUICIDIO (X60-X84)"
    if letra in "VWXY":
        return "Otras causas externas (V-Y, sin suicidio)"
    if letra == "Z":
        return "Factores de salud / contacto servicios (Z)"
    if letra == "U":
        return "Códigos especiales, incl. COVID-19 (U)"
    return "Sin clasificar"


df["capitulo"] = df["CAUSA"].map(capitulo_cie10)
por_capitulo = df.groupby("capitulo")["CUENTA"].sum().sort_values(ascending=False)
puesto_suicidio = list(por_capitulo.index).index("SUICIDIO (X60-X84)") + 1

colores = ["#c44e52" if c == "SUICIDIO (X60-X84)" else "#4c72b0" for c in por_capitulo.index]

fig2, ax2 = plt.subplots(figsize=(11, 8))
ax2.barh(por_capitulo.index[::-1], por_capitulo.values[::-1], color=colores[::-1])
ax2.set_title(
    f"Suicidio frente a las defunciones agrupadas por capítulo CIE-10, 2017-2024\n"
    f"Total: {total_muertes:,.0f} · Suicidios: {total_suicidios:,.0f} ({pct_suicidio:.2f}% del total) · "
    f"puesto {puesto_suicidio}° de {len(por_capitulo)} capítulos"
    .replace(",", ".")
)
ax2.tick_params(axis="y", labelsize=8)
plt.tight_layout()
plt.savefig("output/exploracion/deis/exploracion_deis_suicidio_vs_total.png", dpi=130)
print("Guardado en output/exploracion/deis/exploracion_deis_suicidio_vs_total.png")
print(por_capitulo.to_string())
print(f"\nSuicidio: {total_suicidios:,.0f} de {total_muertes:,.0f} ({pct_suicidio:.2f}%), "
      f"puesto {puesto_suicidio}° de {len(por_capitulo)} capítulos CIE-10.".replace(",", "."))
