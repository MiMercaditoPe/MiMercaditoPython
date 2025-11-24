from neo4j import GraphDatabase
# =============================================================================
# TÉCNICA: INTEGRACIÓN CON BASE DE DATOS DE GRAFOS (NEO4J) - S13
# =============================================================================
# OBJETIVO: 
#   Establecer el "puente" entre la lógica de Python (Backend) y la Base de Datos 
#   de Grafos (Neo4j) para realizar consultas sobre relaciones complejas.
#
# CÓMO FUNCIONA:
#   1. Utiliza el driver oficial 'neo4j' para comunicarse con el servidor.
#   2. Se conecta mediante el protocolo BOLT (bolt://localhost:7687).
#   3. Permite enviar sentencias CYPHER (el lenguaje de los grafos) desde Python
#      para obtener datos como: "¿Qué productos se venden en esta tienda?" o 
#      "¿Qué familias compran productos similares?".
#
# IMPORTANCIA:
#   Permite pasar de un análisis visual estático (Gephi) a un sistema de 
#   consultas dinámico y en tiempo real para la aplicación.
# =============================================================================
# --- CONFIGURACIÓN ---
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678") 

def probar_conexion():
    print("🔌 Intentando conectar a Neo4J...")
    try:
        # Conectamos
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        print("✅ ¡CONEXIÓN EXITOSA CON NEO4J!")
        
        # Hacemos una consulta de prueba (Traer 5 productos)
        query = "MATCH (p:Producto) RETURN p.nombre AS nombre LIMIT 5"
        records, summary, keys = driver.execute_query(query)
        
        print("\n📦 Productos encontrados en el Grafo:")
        for record in records:
            print(f" - {record['nombre']}")
            
        driver.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    probar_conexion()