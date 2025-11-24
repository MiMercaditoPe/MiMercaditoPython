
# -*- coding: utf-8 -*-
"""
datasetListasCompras_script.py

Script para cargar, explorar y limpiar el dataset listas_de_compras.csv.
Generado automáticamente para análisis y optimización de compras semanales.
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
    print("\n--- Resumen del dataset de listas de compras ---")
    print("Columnas:", df.columns.tolist())
    print("\nTipos de datos:")
    print(df.dtypes)
    print("\nDescripción numérica:")
    print(df.describe(include='number').T)
    print("\nPrimeras filas:")
    print(df.head())

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # Conversión de tipos
    num_cols = ["id_lista", "id_familia", "id_producto", "cantidad"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["prioridad"] = df["prioridad"].fillna("Media").astype(str).str.capitalize()
    print("Datos limpios, tipos convertidos y valores nulos manejados.")
    return df

def plot_distributions(df: pd.DataFrame):
    plt.figure(figsize=(8,4))
    sns.histplot(df["cantidad"], bins=15, kde=True)
    plt.title("Distribución de cantidades en listas de compra")
    plt.savefig("output/listas_cantidades.png")
    plt.close()

    plt.figure(figsize=(8,4))
    sns.countplot(data=df, x="prioridad", order=df["prioridad"].value_counts().index)
    plt.title("Distribución de prioridades en las listas de compra")
    plt.savefig("output/listas_prioridad.png")
    plt.close()
    print("Gráficos generados: listas_cantidades.png, listas_prioridad.png")

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
    parser = argparse.ArgumentParser(description="Procesamiento del dataset de listas de compras")
    parser.add_argument("--input", "-i", type=str, default="data/listas_de_compras.csv")
    parser.add_argument("--output", "-o", type=str, default="data/listas_de_compras_clean.csv")
    args = parser.parse_args()
    main(args.input, args.output)
