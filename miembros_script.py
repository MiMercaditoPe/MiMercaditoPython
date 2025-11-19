# -*- coding: utf-8 -*-
"""miembros_script.py

Script para cargar, resumir y limpiar el archivo miembros.csv ubicado en /mnt/data/.
Funciones:
- load_data(path)
- summarize(df)
- clean_data(df)
- save_clean(df, out_path)

Personalizar según las columnas reales del CSV.
""" # <-- Este es el cierre del docstring (Línea 12 corregida)

import argparse
import os
import pandas as pd
import numpy as np

def load_data(path):
    """Carga los datos del CSV y verifica que el archivo exista."""
    if not os.path.exists(path):
        # Uso de f-string para incluir la variable 'path' en el mensaje de error.
        raise FileNotFoundError(f"No se encontró: {path}")
    
    df = pd.read_csv(path, low_memory=False)
    print(f"Cargado {path} con {df.shape[0]} filas y {df.shape[1]} columnas.")
    return df

def summarize(df):
    """Muestra un resumen de los tipos de datos y los valores nulos."""
    print('\n--- Resumen ---')
    print(df.dtypes)
    print('\nNulos por columna:')
    print(df.isnull().sum())

def clean_column_names(df):
    """Limpia los nombres de las columnas a minúsculas y snake_case."""
    df = df.copy()
    # Limpia el nombre: quita espacios, minúsculas, reemplaza espacios por '_',
    # y mantiene solo caracteres alfanuméricos o '_'.
    df.columns = [ 
        ''.join(ch for ch in c.strip().lower().replace(' ', '_') if ch.isalnum() or ch=='_') 
        for c in df.columns 
    ]
    return df

def clean_data(df):
    """Realiza la limpieza principal de los datos."""
    df = df.copy()
    df = clean_column_names(df)
    
    # Elimina filas que son COMPLETAMENTE nulas
    df.dropna(how='all', inplace=True)
    
    # Rellenado de Nulos (Imputación)
    # 1. Columnas Numéricas: Rellenar nulos con la Mediana
    num_cols = df.select_dtypes(include=['number']).columns
    for c in num_cols:
        if df[c].isnull().any():
            df[c].fillna(df[c].median(), inplace=True)
            
    # 2. Columnas de Objeto (Texto/Categóricas): Rellenar nulos con una cadena vacía
    obj_cols = df.select_dtypes(include=['object']).columns
    for c in obj_cols:
        if df[c].isnull().any():
            df[c].fillna('', inplace=True)
            
    return df

def save_clean(df, out_path):
    """Guarda el DataFrame limpio en un nuevo archivo CSV."""
    df.to_csv(out_path, index=False)
    print(f"Guardado limpio en: {out_path}")

if __name__ == '__main__':
    # Configura los argumentos de entrada/salida para el script
    parser = argparse.ArgumentParser(description="Script de limpieza de datos de miembros.")
    parser.add_argument('--input','-i', default='/mnt/data/miembros.csv', help='Ruta al archivo CSV de entrada.')
    parser.add_argument('--output','-o', default='./miembros_cleaned.csv', help='Ruta para guardar el archivo CSV limpio.')
    args = parser.parse_args()
    
    # Ejecución del flujo de trabajo
    print("--- 1. CARGA DE DATOS ---")
    try:
        df = load_data(args.input)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        exit() # Salir si el archivo de entrada no se encuentra
        
    print("\n--- 2. RESUMEN DE DATOS ORIGINALES ---")
    summarize(df)
    
    print("\n--- 3. LIMPIEZA DE DATOS ---")
    dfc = clean_data(df)
    
    print("\n--- 4. RESUMEN DE DATOS LIMPIOS ---")
    summarize(dfc)
    
    print("\n--- 5. GUARDAR DATOS ---")
    save_clean(dfc, args.output)