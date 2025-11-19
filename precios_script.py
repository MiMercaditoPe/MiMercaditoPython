# -*- coding: utf-8 -*-
"""precios_script.py # <--- CORREGIDO: Se eliminó la barra invertida inicial

Script para cargar y preparar 'precios.csv' en /mnt/data/.
Incluye:
- conversión numérica robusta (eliminar símbolos de moneda)
- detección de moneda si aplica
- resumen básico
""" # <--- Cierre del docstring (Línea 10 corregida)

import argparse
import os
import pandas as pd
import numpy as np
import re

def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró: {path}")
    df = pd.read_csv(path, low_memory=False)
    print(f"Cargado {path} con {df.shape[0]} filas y {df.shape[1]} columnas.")
    return df

def clean_column_names(df):
    df = df.copy()
    df.columns = [ ''.join(ch for ch in c.strip().lower().replace(' ', '_') if ch.isalnum() or ch=='_') for c in df.columns ]
    return df

def parse_currency_series(s: pd.Series) -> pd.Series:
    """Intenta extraer número de una serie que contiene símbolos de moneda y miles."""
    if s.dtype == 'object':
        # Esta regex elimina cualquier cosa que no sea dígito, coma, punto o guion, y luego reemplaza comas por puntos.
        cleaned = s.astype(str).str.replace(r'[^0-9,.\-]', '', regex=True).str.replace(',', '.')
        return pd.to_numeric(cleaned, errors='coerce')
    else:
        return pd.to_numeric(s, errors='coerce')

def summarize(df):
    print('\n--- Resumen ---')
    print(df.dtypes)
    print('\nNulos por columna:')
    print(df.isnull().sum())

def clean_data(df):
    df = df.copy()
    df = clean_column_names(df)
    df.dropna(how='all', inplace=True)
    # Intentar convertir columnas que parezcan precios
    for c in df.columns:
        if 'price' in c or 'precio' in c or 'cost' in c or 'monto' in c:
            df[c] = parse_currency_series(df[c])
            print(f"Intentada conversión a numérica para: {c}")
    # Rellenar numéricos con mediana
    num_cols = df.select_dtypes(include=['number']).columns
    for c in num_cols:
        if df[c].isnull().any():
            df[c].fillna(df[c].median(), inplace=True)
    # Rellenar objetos
    for c in df.select_dtypes(include=['object']).columns:
        df[c].fillna('', inplace=True)
    return df

def save_clean(df, out_path):
    df.to_csv(out_path, index=False)
    print(f"Guardado limpio en: {out_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script para limpiar y preparar datos de precios.")
    parser.add_argument('--input','-i', default='/mnt/data/precios.csv', help='Ruta al archivo CSV de entrada.')
    parser.add_argument('--output','-o', default='./precios_cleaned.csv', help='Ruta para guardar el archivo CSV limpio.')
    args = parser.parse_args()
    
    print("--- 1. CARGA DE DATOS ---")
    try:
        df = load_data(args.input)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        exit()
        
    print("\n--- 2. RESUMEN DE DATOS ORIGINALES ---")
    summarize(df)
    
    print("\n--- 3. LIMPIEZA Y CONVERSIÓN DE DATOS ---")
    dfc = clean_data(df)
    
    print("\n--- 4. RESUMEN DE DATOS LIMPIOS ---")
    summarize(dfc)
    
    print("\n--- 5. GUARDAR DATOS ---")
    save_clean(dfc, args.output)