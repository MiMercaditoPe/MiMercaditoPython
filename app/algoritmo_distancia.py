import networkx as nx

# =============================================================================
# MAPA DE LIMA (Distancias en Kilómetros)
# Se define como un diccionario, que networkx usa para construir el grafo.
# =============================================================================
# Fuente: Grafos y pesos de la imagen proporcionada (ej: Comas a SMP son 8km)
MAPA_LIMA = {
    'Comas': {'San Martin de Porres': 8, 'San Juan de Lurigancho': 12},
    'San Martin de Porres': {'Comas': 8, 'Callao': 9, 'Jesus Maria': 9},
    'Callao': {'San Martin de Porres': 9, 'San Miguel': 3},
    'San Miguel': {'Callao': 3, 'Pueblo Libre': 3},
    'Pueblo Libre': {'San Miguel': 3, 'Jesus Maria': 4, 'Surquillo': 18},
    'Jesus Maria': {'San Martin de Porres': 9, 'Pueblo Libre': 4, 'Lince': 3},
    'Lince': {'Jesus Maria': 3, 'San Isidro': 4},
    'San Isidro': {'Lince': 4, 'San Borja': 3, 'Surquillo': 2},
    'Surquillo': {'San Isidro': 2, 'Miraflores': 7, 'Santiago de Surco': 4, 'Villa El Salvador': 10},
    'Miraflores': {'Surquillo': 7, 'Barranco': 2},
    'Barranco': {'Miraflores': 2, 'Chorrillos': 2},
    'Chorrillos': {'Barranco': 2, 'Santiago de Surco': 7, 'Villa El Salvador': 11},
    'Santiago de Surco': {'Surquillo': 4, 'Chorrillos': 7, 'San Borja': 4},
    'San Borja': {'San Isidro': 3, 'Santiago de Surco': 4, 'La Molina': 5},
    'La Molina': {'San Borja': 5, 'San Juan de Lurigancho': 13, 'Villa El Salvador': 9},
    'San Juan de Lurigancho': {'Comas': 12, 'La Molina': 13, 'Surquillo': 10} # Añadí un 10 para Surquillo por consistencia, asumiendo una conexión del mapa
}

# Crear el objeto Grafo Ponderado (se crea una sola vez al inicio)
GRAFO_DISTANCIA = nx.Graph(MAPA_LIMA)

def obtener_costo_traslado(distrito_origen: str, distrito_destino: str) -> float:
    """
    Calcula el costo mínimo de traslado (distancia en km) entre dos distritos
    utilizando el algoritmo de Dijkstra (que networkx usa por defecto).
    """
    try:
        # En networkx, shortest_path_length utiliza Dijkstra para grafos ponderados.
        costo = nx.shortest_path_length(
            GRAFO_DISTANCIA, 
            source=distrito_origen, 
            target=distrito_destino, 
            weight='weight' # Usamos el peso (km) de las aristas
        )
        return costo
    except nx.NetworkXNoPath:
        # Esto ocurre si los distritos no están conectados (no debería pasar con este mapa)
        return float('inf')
    except nx.NodeNotFound:
        # Esto ocurre si el nombre del distrito no está en el mapa
        return float('inf')


# --- PRUEBA DE EJEMPLO ---
if __name__ == "__main__":
    # Prueba: Calcular costo de Kevin (Miraflores) a Plaza Vea (San Borja)
    costo_ejemplo = obtener_costo_traslado('Miraflores', 'San Borja')
    print(f"Costo Miraflores -> San Borja: {costo_ejemplo} km")

    # Prueba: Calcular costo de Comas a Chorrillos (Una ruta larga)
    costo_largo = obtener_costo_traslado('Comas', 'Chorrillos')
    print(f"Costo Comas -> Chorrillos: {costo_largo} km")