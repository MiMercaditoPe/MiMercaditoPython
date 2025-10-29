import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# === 1. Cargar el dataset completo (CSV) ===
df = pd.read_csv('dataset_compras_completo.csv', encoding='utf-8')
print("✅ Dataset cargado correctamente")
print("Filas:", len(df))
print("Columnas:", list(df.columns))

# === 2. Crear el grafo base ===
G = nx.Graph()

# Usa las dos primeras columnas como relación (por ejemplo, cliente-producto, tienda-producto, etc.)
col1 = df.columns[0]
col2 = df.columns[1]

for _, fila in df.iterrows():
    G.add_node(fila[col1])
    G.add_node(fila[col2])
    G.add_edge(fila[col1], fila[col2])

print("Nodos totales:", G.number_of_nodes())
print("Enlaces totales:", G.number_of_edges())

# === 3. Visualización del grafo ===
plt.figure(figsize=(8, 6))
nx.draw(G, node_size=20, with_labels=False)
plt.title("Grafo del Dataset de Compras Completo")
plt.show()

# === 4. Guardar imagen del grafo ===
plt.savefig('grafo_dataset_completo.png', dpi=300)
print("🖼️ Grafo guardado como grafo_dataset_completo.png")
