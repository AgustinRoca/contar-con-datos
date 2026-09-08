"""
Chequeo de la hipótesis económica para el crecimiento de suicidios en 35-49 años:
¿empeoró el desempleo o el ingreso real de esa franja más que en el resto, 2017-2024?

Usa los 31 microdatos trimestrales de EPH (INDEC) ya descargados en
data/raw/eph/tmp_extract/ (falta 2017 T1, no publicado por INDEC) y el IPC nacional
completo (data/raw/ipc/sh_ipc_11_25.xls) para deflactar ingresos.

Salida: data/processed/eph_desocupacion_por_edad_anual.csv
        data/processed/eph_ingreso_real_por_edad_anual.csv
"""
import glob
import pandas as pd
from pathlib import Path

RAW = Path("data/raw/eph/tmp_extract")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

EDAD_BUCKETS = [(0, 19, "0-19"), (20, 34, "20-34"), (35, 49, "35-49"),
                (50, 64, "50-64"), (65, 200, "65+")]


def bucket(edad):
    for lo, hi, label in EDAD_BUCKETS:
        if lo <= edad <= hi:
            return label
    return None


files = sorted(set(glob.glob(str(RAW / "**/*ndividual*"), recursive=True))
               | set(glob.glob(str(RAW / "**/*ersonas*"), recursive=True)))
print(f"{len(files)} archivos EPH encontrados")

# --- IPC nacional, nivel general, mensual, dic-2016=100 ---
ipc_raw = pd.read_excel("data/raw/ipc/sh_ipc_11_25.xls",
                         sheet_name="Índices IPC Cobertura Nacional", header=None)
fechas = ipc_raw.iloc[5, 1:].tolist()
nivel_general = ipc_raw.iloc[9, 1:].tolist()
ipc = pd.DataFrame({"fecha": fechas, "ipc": nivel_general}).dropna()
ipc["fecha"] = pd.to_datetime(ipc["fecha"])
ipc["anio"] = ipc["fecha"].dt.year
ipc["trimestre"] = ((ipc["fecha"].dt.month - 1) // 3) + 1
ipc_trim = ipc.groupby(["anio", "trimestre"])["ipc"].mean().reset_index()
ipc_base = ipc_trim.sort_values(["anio", "trimestre"]).iloc[-1]["ipc"]

filas_desocup = []
filas_ingreso = []
for f in files:
    df = pd.read_csv(f, sep=";", dtype=str, encoding="latin1", low_memory=False,
                      quotechar='"', on_bad_lines="skip")
    df.columns = [c.strip().strip('"').upper() for c in df.columns]
    if not {"ANO4", "TRIMESTRE", "CH06", "ESTADO"}.issubset(df.columns):
        print("  salteado (faltan columnas):", f)
        continue

    anio = pd.to_numeric(df["ANO4"], errors="coerce")
    trimestre = pd.to_numeric(df["TRIMESTRE"], errors="coerce")
    edad = pd.to_numeric(df["CH06"], errors="coerce")
    estado = pd.to_numeric(df["ESTADO"], errors="coerce")
    pondera = pd.to_numeric(df.get("PONDERA"), errors="coerce")

    base = pd.DataFrame({"anio": anio, "trimestre": trimestre, "edad": edad,
                          "estado": estado, "pondera": pondera})
    base = base.dropna(subset=["anio", "trimestre", "edad", "estado", "pondera"])
    base = base[base["edad"] >= 0]
    base["franja"] = base["edad"].map(bucket)
    base = base.dropna(subset=["franja"])

    pea = base[base["estado"].isin([1, 2])]
    for (a, t, fr), g in pea.groupby(["anio", "trimestre", "franja"]):
        desocupados = g.loc[g["estado"] == 2, "pondera"].sum()
        total_pea = g["pondera"].sum()
        filas_desocup.append({"anio": int(a), "trimestre": int(t), "franja": fr,
                               "tasa_desocupacion": desocupados / total_pea * 100 if total_pea else float("nan")})

    if {"P47T", "PONDII"}.issubset(df.columns):
        ingreso = pd.to_numeric(df["P47T"], errors="coerce")
        pondii = pd.to_numeric(df["PONDII"], errors="coerce")
        bi = pd.DataFrame({"anio": anio, "trimestre": trimestre, "edad": edad,
                            "ingreso": ingreso, "pondii": pondii})
        bi = bi.dropna(subset=["anio", "trimestre", "edad", "ingreso", "pondii"])
        bi = bi[(bi["ingreso"] > 0) & (bi["edad"] >= 0)]
        bi["franja"] = bi["edad"].map(bucket)
        bi = bi.dropna(subset=["franja"])
        for (a, t, fr), g in bi.groupby(["anio", "trimestre", "franja"]):
            ingreso_medio = (g["ingreso"] * g["pondii"]).sum() / g["pondii"].sum()
            filas_ingreso.append({"anio": int(a), "trimestre": int(t), "franja": fr,
                                   "ingreso_nominal_medio": ingreso_medio})

orden = ["0-19", "20-34", "35-49", "50-64", "65+"]

# --- Desocupación ---
desocup = pd.DataFrame(filas_desocup)
anual_desocup = desocup.groupby(["anio", "franja"])["tasa_desocupacion"].mean().reset_index()
piv_desocup = anual_desocup.pivot(index="franja", columns="anio", values="tasa_desocupacion").reindex(orden)
piv_desocup.to_csv(OUT / "eph_desocupacion_por_edad_anual.csv")
print("\nTasa de desocupación promedio anual por franja etaria (%):")
print(piv_desocup.round(1).to_string())
if 2017 in piv_desocup.columns and 2024 in piv_desocup.columns:
    print("\nVariación pp 2017->2024:")
    print((piv_desocup[2024] - piv_desocup[2017]).round(1).to_string())

# --- Ingreso real ---
ingreso_df = pd.DataFrame(filas_ingreso).merge(ipc_trim, on=["anio", "trimestre"], how="left")
ingreso_df["ingreso_real"] = ingreso_df["ingreso_nominal_medio"] * (ipc_base / ingreso_df["ipc"])
anual_ingreso = ingreso_df.groupby(["anio", "franja"])["ingreso_real"].mean().reset_index()
piv_ingreso = anual_ingreso.pivot(index="franja", columns="anio", values="ingreso_real").reindex(orden)
piv_ingreso.to_csv(OUT / "eph_ingreso_real_por_edad_anual.csv")
print("\nIngreso individual real promedio anual (pesos constantes, últ. trimestre de la serie):")
print(piv_ingreso.round(0).to_string())
if 2017 in piv_ingreso.columns and 2024 in piv_ingreso.columns:
    var_pct = ((piv_ingreso[2024] - piv_ingreso[2017]) / piv_ingreso[2017] * 100).round(1)
    print("\nVariación % del ingreso real 2017->2024:")
    print(var_pct.to_string())
