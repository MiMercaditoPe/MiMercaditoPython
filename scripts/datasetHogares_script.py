
# -*- coding: utf-8 -*-
"""
datasetHogares_script.py

Script para cargar, explorar y limpiar el dataset hogares.csv.
Generado automáticamente para análisis de familias urbanas de Lima.
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    df = pd.read_csv(path)
    print(f"Cargado '{path}' con {df.shape[0]} filas y {df.shape[1]} columnas.")
    return df

def summarize(df: pd.DataFrame):
    print("\n--- Resumen del dataset de hogares ---")
    print("Columnas:", df.columns.tolist())
    print("\nTipos de datos:")
    print(df.dtypes)
    print("\nDescripción numérica:")
    print(df.describe(include='number').T)
    print("\nPrimeras filas:")
    print(df.head())

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Limpieza de nombres de columnas
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # Manejo de nulos
    df.fillna({"nombre_representante": "", "distrito": ""}, inplace=True)
    # Conversión de tipos
    df["num_miembros"] = pd.to_numeric(df["num_miembros"], errors="coerce")
    df["ingreso_mensual_soles"] = pd.to_numeric(df["ingreso_mensual_soles"], errors="coerce")
    print("Datos limpios y tipos normalizados.")
    return df

def plot_distributions(df: pd.DataFrame):
    plt.figure(figsize=(8,4))
    sns.histplot(df["ingreso_mensual_soles"], kde=True, bins=10)
    plt.title("Distribución de ingresos mensuales")
    plt.savefig("hogares_ingresos.png")
    plt.close()

    plt.figure(figsize=(8,4))
    sns.countplot(data=df, x="num_miembros")
    plt.title("Distribución de número de miembros por hogar")
    plt.savefig("hogares_miembros.png")
    plt.close()
    print("Gráficos generados: hogares_ingresos.png, hogares_miembros.png")

def save_clean(df: pd.DataFrame, out_path: str):
    df.to_csv(out_path, index=False)
    print(f"Archivo limpio guardado en: {out_path}")

def main(input_path: str, output_path: str):
    df = load_data(input_path)
    summarize(df)
    df = clean_data(df)
    summarize(df)
    plot_distributions(df)
    save_clean(df, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesamiento del dataset de hogares")
    parser.add_argument("--input", "-i", type=str, default="hogares.csv")
    parser.add_argument("--output", "-o", type=str, default="hogares_clean.csv")
    args = parser.parse_args()
    main(args.input, args.output)
