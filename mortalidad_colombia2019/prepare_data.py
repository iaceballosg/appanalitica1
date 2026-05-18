"""
prepare_data.py – Run once locally to generate data_2019.parquet
Usage:  python prepare_data.py
Place the three DANE Excel files in the same directory before running.
"""
import pandas as pd
import os

BASE = os.path.dirname(__file__)

def main():
    print("Loading raw data…")
    df = pd.read_excel(os.path.join(BASE, "Anexo1_NoFetal2019_CE_15-03-23.xlsx"))
    divipola = pd.read_excel(os.path.join(BASE, "Divipola_CE_.xlsx"))
    cod_muerte = pd.read_excel(os.path.join(BASE, "Anexo2_CodigosDeMuerte_CE_15-03-23.xlsx"), header=8)

    depto_map = (
        divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO"]]
        .drop_duplicates()
        .set_index("COD_DEPARTAMENTO")["DEPARTAMENTO"]
        .to_dict()
    )
    cod3_map = (
        cod_muerte
        .set_index("Código de la CIE-10 tres caracteres")[
            "Descripción  de códigos mortalidad a tres caracteres"
        ]
        .to_dict()
    )

    df["DEPARTAMENTO"] = df["COD_DEPARTAMENTO"].map(depto_map).fillna("DESCONOCIDO")
    df["COD3"] = df["COD_MUERTE"].astype(str).str[:3]
    df["DESC_CAUSA"] = df["COD3"].map(cod3_map).fillna("Sin descripción")
    df["SEXO_LABEL"] = df["SEXO"].map({1: "Masculino", 2: "Femenino", 3: "Indeterminado"})

    out = os.path.join(BASE, "data_2019.parquet")
    df.to_parquet(out, index=False)
    print(f"✅ Saved {len(df):,} rows → {out}")

if __name__ == "__main__":
    main()
