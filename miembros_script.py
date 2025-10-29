# -*- coding: utf-8 -*-
\"\"\"miembros_script.py

Script para cargar, resumir y limpiar el archivo miembros.csv ubicado en /mnt/data/.
Funciones:
- load_data(path)
- summarize(df)
- clean_data(df)
- save_clean(df, out_path)

Personalizar según las columnas reales del CSV.
\"\"\"

import argparse
import os
import pandas as pd
import numpy as np

def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró: {path}")
    df = pd.read_csv(path, low_memory=False)
    print(f"Cargado {path} con {df.shape[0]} filas y {df.shape[1]} columnas.")
    return df

def summarize(df):
    print('\\n--- Resumen ---')
    print(df.dtypes)
    print('\\nNulos por columna:')
    print(df.isnull().sum())

def clean_column_names(df):
    df = df.copy()
    df.columns = [ ''.join(ch for ch in c.strip().lower().replace(' ', '_') if ch.isalnum() or ch=='_') for c in df.columns ]
    return df

def clean_data(df):
    df = df.copy()
    df = clean_column_names(df)
    df.dropna(how='all', inplace=True)
    # Rellenado simple: objetos -> '', numéricos -> mediana
    num_cols = df.select_dtypes(include=['number']).columns
    for c in num_cols:
        if df[c].isnull().any():
            df[c].fillna(df[c].median(), inplace=True)
    obj_cols = df.select_dtypes(include=['object']).columns
    for c in obj_cols:
        if df[c].isnull().any():
            df[c].fillna('', inplace=True)
    return df

def save_clean(df, out_path):
    df.to_csv(out_path, index=False)
    print(f"Guardado limpio en: {out_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input','-i', default='/mnt/data/miembros.csv')
    parser.add_argument('--output','-o', default='/mnt/data/miembros_cleaned.csv')
    args = parser.parse_args()
    df = load_data(args.input)
    summarize(df)
    dfc = clean_data(df)
    summarize(dfc)
    save_clean(dfc, args.output)
