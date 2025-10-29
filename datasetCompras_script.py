# -*- coding: utf-8 -*-
"""
dataset_script.py

Script de ejemplo (en español) para cargar, explorar y limpiar un dataset CSV.
Este archivo fue generado automáticamente y asume que el CSV original se llama:
/mnt/data/dataset_compras_completo.csv

Funciones incluidas:
- load_data(path)
- summarize(df, n=5)
- clean_data(df)
- plot_distributions(df, cols=None, max_cols=6)
- save_clean(df, out_path)

Uso:
python dataset_script.py --input /ruta/a/dataset_compras_completo.csv --output /ruta/a/cleaned.csv

El script realiza:
- Lectura inteligente con pandas (tratando de inferir fechas y tipos)
- Resumen de columnas (nulos, tipos, valores únicos)
- Limpieza básica (nombres de columnas estandarizados, tipos numéricos, manejo de nulos simples)
- Guardado del CSV limpio

Adaptar según las columnas reales de su dataset.
"""

import argparse
import os
from typing import Optional, List

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_data(path: str) -> pd.DataFrame:
    \"\"\"Carga un CSV con lectura robusta y muestra tamaño.\"\"\"
    if not os.path.exists(path):
        raise FileNotFoundError(f\"No se encontró el archivo: {path}\")
    # Intentar inferir fechas y tipos automáticamente
    df = pd.read_csv(path, low_memory=False)
    print(f\"Cargado '{path}' con {df.shape[0]} filas y {df.shape[1]} columnas.\")
    return df

def summarize(df: pd.DataFrame, n: int = 5) -> None:
    \"\"\"Imprime un resumen básico del dataframe.\"\"\"
    print('\\n--- Resumen rápido ---')
    print('Columnas:', df.columns.tolist())
    print('\\nTipos de datos:')
    print(df.dtypes)
    print('\\nValores nulos por columna:')
    print(df.isnull().sum().sort_values(ascending=False).head(20))
    print(f'\\nPrimeras {n} filas:')
    print(df.head(n))
    print('\\nDescripción numérica:')
    print(df.describe(include='number').T)

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    \"\"\"Estandariza nombres de columnas: minusculas, sin espacios, sin caracteres especiales.\"\"\"
    new_cols = []
    for c in df.columns:
        nc = (c.strip()
              .lower()
              .replace(' ', '_')
              .replace('-', '_'))
        # eliminar caracteres no alfanuméricos salvo underscore
        nc = ''.join(ch for ch in nc if ch.isalnum() or ch == '_')
        new_cols.append(nc)
    df.columns = new_cols
    return df

def coerce_numeric(df: pd.DataFrame, cols: Optional[List[str]] = None) -> pd.DataFrame:
    \"\"\"Convierte columnas a numéricas cuando es posible.\"\"\"
    if cols is None:
        # intentar todas las columnas que no sean obviously categorical
        candidate_cols = df.select_dtypes(include=['object']).columns.tolist()
    else:
        candidate_cols = cols
    for c in candidate_cols:
        # intentar convertir, si más del 50% se convierte sin NaN, se aplica
        converted = pd.to_numeric(df[c].str.replace('[^0-9.,-]', '', regex=True).str.replace(',','.'), errors='coerce') if df[c].dtype == 'object' else pd.to_numeric(df[c], errors='coerce')
        valid_frac = converted.notna().mean()
        if valid_frac >= 0.5:
            df[c] = converted
            print(f\"Columna '{c}' convertida a numérica (frac valid: {valid_frac:.2f}).\")
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    \"\"\"Limpieza básica y transformaciones seguras.\"\"\"
    df = df.copy()
    df = clean_column_names(df)
    # Quitar filas completamente vacías
    before = df.shape[0]
    df.dropna(how='all', inplace=True)
    after = df.shape[0]
    print(f\"Filas vacías totales eliminadas: {before - after}\")
    # Convertir objetos numéricos si parece apropiado
    df = coerce_numeric(df)
    # Rellenar nulos simples para columnas numéricas con la mediana
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    for c in num_cols:
        n_null = df[c].isnull().sum()
        if n_null > 0:
            med = df[c].median()
            df[c].fillna(med, inplace=True)
            print(f\"Rellenado {n_null} nulos en '{c}' con median: {med}\")
    # Rellenar nulos en columnas object con cadena vacía (o mantener NaN según preferencia)
    obj_cols = df.select_dtypes(include=['object']).columns.tolist()
    for c in obj_cols:
        n_null = df[c].isnull().sum()
        if n_null > 0:
            df[c].fillna('', inplace=True)
            print(f\"Rellenado {n_null} nulos en '{c}' con cadena vacía.\")
    return df

def plot_distributions(df: pd.DataFrame, cols: Optional[List[str]] = None, max_cols: int = 6) -> None:
    \"\"\"Genera histogramas para columnas numéricas (hasta max_cols).\"\"\"
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    if cols is not None:
        num_cols = [c for c in cols if c in num_cols]
    if not num_cols:
        print(\"No hay columnas numéricas para graficar.\")
        return
    num_cols = num_cols[:max_cols]
    for c in num_cols:
        plt.figure(figsize=(6,3))
        df[c].hist(bins=30)
        plt.title(f'Distribución: {c}')
        plt.xlabel(c)
        plt.ylabel('Frecuencia')
        fname = f'plot_{c}.png'
        plt.tight_layout()
        plt.savefig(fname)
        plt.close()
        print(f'Guardado histograma: {fname}')

def save_clean(df: pd.DataFrame, out_path: str) -> None:
    \"\"\"Guarda el dataframe en CSV (sin índice).\"\"\"
    df.to_csv(out_path, index=False)
    print(f\"CSV limpio guardado en: {out_path}\")

def main(input_path: str, output_path: str) -> None:
    df = load_data(input_path)
    summarize(df)
    df_clean = clean_data(df)
    summarize(df_clean)
    plot_distributions(df_clean)
    save_clean(df_clean, output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script de ejemplo para procesar dataset de compras.')
    parser.add_argument('--input', '-i', type=str, default='/mnt/data/dataset_compras_completo.csv', help='Ruta al CSV de entrada')
    parser.add_argument('--output', '-o', type=str, default='/mnt/data/dataset_compras_completo_cleaned.csv', help='Ruta al CSV de salida (limpio)')
    args = parser.parse_args()
    main(args.input, args.output)
