"""
Arma data/processed/who_suicide_rate_by_country_2021.csv (tasa de suicidio
ajustada por edad, por pais, usada para el mapa mundial) a partir del export
crudo de la OMS (indicador MH_12, Global Health Observatory).

Filtra el ano 2021 y "Both sexes" (un solo valor por pais, sin desagregar por
sexo), y convierte el codigo de pais de ISO3 (como lo da la OMS) a ISO2 (lo
que usa el SVG del mapa, que identifica cada <path>/<g> por su codigo ISO2 en
minuscula).

Entrada:  data/raw/who_suicide_rates/data.csv
Salida:   data/processed/who_suicide_rate_by_country_2021.csv (iso2, Location,
          FactValueNumeric)
"""
import pandas as pd
import pycountry
from pathlib import Path

RAW = Path("data/raw/who_suicide_rates/data.csv")
OUT = Path("data/processed/who_suicide_rate_by_country_2021.csv")


def iso3_to_iso2(iso3: str) -> str | None:
    country = pycountry.countries.get(alpha_3=iso3)
    return country.alpha_2.lower() if country else None


df = pd.read_csv(RAW)
df = df[(df["Period"] == 2021) & (df["Dim1"] == "Both sexes")]
df = df[["SpatialDimValueCode", "Location", "FactValueNumeric"]].copy()

df["iso2"] = df["SpatialDimValueCode"].map(iso3_to_iso2)
sin_iso2 = df[df["iso2"].isna()]
if len(sin_iso2):
    print(f"Aviso: {len(sin_iso2)} filas sin equivalente ISO2 (se descartan):")
    print(sin_iso2[["SpatialDimValueCode", "Location"]].to_string(index=False))
df = df.dropna(subset=["iso2"])

df = df[["iso2", "Location", "FactValueNumeric"]].sort_values("iso2")
df.to_csv(OUT, index=False)
print(f"{len(df)} paises -> {OUT}")
