import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv('dataset_compras_completo.csv', encoding='utf-8')


col_familia = 'nombre_representante' # Columna B
col_producto = 'producto'            # Columna D
col_tienda = 'nombre_tienda'         # Columna H

# ===  grafo ===
G = nx.Graph()

print("Construyendo el grafo tripartito...")
for _, fila in df.iterrows():
    # Obtener los valores de cada entidad en la fila
    nodo_familia = fila[col_familia]
    nodo_producto = fila[col_producto]
    nodo_tienda = fila[col_tienda]

    # Añadir los 3 tipos de nodos con su atributo 'tipo'
    G.add_node(nodo_familia, tipo='Familia', label=str(nodo_familia))
    G.add_node(nodo_producto, tipo='Producto', label=str(nodo_producto))
    G.add_node(nodo_tienda, tipo='Tienda', label=str(nodo_tienda))

    # Crear las aristas (Conexiones de la compra)
    # 1. Familia -> Producto (Qué compró la familia)
    G.add_edge(nodo_familia, nodo_producto)
    # 2. Producto -> Tienda (Dónde se compró ese producto)
    G.add_edge(nodo_producto, nodo_tienda)
    # 3. Familia -> Tienda (Dónde compró la familia)
    G.add_edge(nodo_familia, nodo_tienda)

print("Grafo construido.")

# =========================================================
# === EXPORTAR A GEXF PARA GEPHI ===
# =========================================================
# Usamos un nuevo nombre para no confundirnos
output_gexf_file = 'grafo_compras_FINAL_nombres.gexf' 
nx.write_gexf(G, output_gexf_file)
print(f"✅ Grafo exportado a '{output_gexf_file}' para Gephi.")


plt.figure(figsize=(12, 10))
pos = nx.spring_layout(G, k=0.5, iterations=20, seed=42) # Layout rápido
nx.draw(
    G,
    pos,
    node_size=10,
    with_labels=False,
    edge_color="#EEEEEE",
    alpha=0.6
)
plt.title("Visualización Densa (Usar Gephi para análisis)")
plt.savefig("grafo_dataset_completo_denso_v3.png", dpi=300)
print("✅ Grafo generado y guardado (versión densa).")