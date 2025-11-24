import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
import math
import random
# =============================================================================
# TÉCNICA: MST (Minimum Spanning Tree) - Algoritmo de Kruskal
# =============================================================================
# OBJETIVO: 
#   Conectar todas las tiendas seleccionadas utilizando la menor distancia 
#   posible (ahorro de recorrido/gasolina).
#
# CÓMO FUNCIONA:
#   1. Crea un GRAFO completo donde todas las tiendas están conectadas con todas.
#   2. Calcula la distancia (peso) entre cada par de tiendas.
#   3. Aplica KRUSKAL: Ordena las distancias de menor a mayor y va eligiendo
#      las conexiones más cortas, siempre y cuando no formen un ciclo cerrado.
#   4. Resultado: Un árbol que une todos los puntos con el costo mínimo total.
# =============================================================================


try:
 
    df_tiendas = pd.read_csv('data/generated_tiendas.csv')
except FileNotFoundError:
    df_tiendas = pd.read_csv('../data/generated_tiendas.csv')

print(f"✅ Cargadas {len(df_tiendas)} tiendas para el análisis de rutas.")

# --- 2. SIMULAR UBICACIONES (Coordenadas X, Y) ---
# basadas en el ID para que siempre salgan igual.
posiciones = {}
for _, row in df_tiendas.iterrows():
    x = (row['id_tienda'] * 37) % 100
    y = (row['id_tienda'] * 73) % 100
    posiciones[row['id_tienda']] = (x, y)

# --- 3. CREAR EL GRAFO COMPLETO  ---
G = nx.Graph()

# Añadir Nodos (Tiendas)
for id_t, pos in posiciones.items():
    nombre = df_tiendas.loc[df_tiendas['id_tienda'] == id_t, 'nombre_tienda'].values[0]
    distrito = df_tiendas.loc[df_tiendas['id_tienda'] == id_t, 'distrito'].values[0]
    etiqueta = f"{nombre}\n({distrito})"
    G.add_node(id_t, pos=pos, label=etiqueta)

# Añadir Aristas (Caminos posibles entre todas)
print("🛣️ Calculando distancias entre todas las tiendas...")
for t1, t2 in combinations(df_tiendas['id_tienda'], 2):
    p1 = posiciones[t1]
    p2 = posiciones[t2]
    distancia = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    G.add_edge(t1, t2, weight=distancia)

# --- 4. ALGORITMO MST (KRUSKAL) ---
print("🧠 Ejecutando Algoritmo de Kruskal (MST)...")
mst_grafo = nx.minimum_spanning_tree(G, algorithm='kruskal')

# Calcular cuánto nos ahorramos
peso_total = mst_grafo.size(weight='weight')
print(f"✅ Ruta optimizada calculada.")
print(f"   Distancia total mínima: {peso_total:.2f} unidades de distancia.")

# --- 5. VISUALIZACIÓN ---
plt.figure(figsize=(14, 10))
pos = nx.get_node_attributes(G, 'pos')

# Dibujar
nx.draw_networkx_nodes(G, pos, node_size=700, node_color='#66c2a5', edgecolors='black')


nombres = nx.get_node_attributes(G, 'label')
nx.draw_networkx_labels(G, pos, labels=nombres, font_size=8, font_weight='bold')


nx.draw_networkx_edges(mst_grafo, pos, edge_color='#d53e4f', width=2.5)

# Detalles 
plt.title(f"Algoritmo MST (Kruskal): Ruta de Reparto Óptima\nConecta todas las tiendas con la mínima distancia ({peso_total:.2f})", fontsize=14)
plt.axis('off')

# Guardar
output_path = 'output/ruta_tiendas_mst.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"📸 Gráfico de la ruta guardado en: {output_path}")
