import pandas as pd
from sqlalchemy import create_engine
# =============================================================================
# TÉCNICA: FUERZA BRUTA CON BACKTRACKING (Recursividad)
# =============================================================================
# OBJETIVO: 
#   Encontrar la mejor combinación de productos que una familia puede comprar
#   sin exceder su presupuesto límite.
#
# CÓMO FUNCIONA:
#   1. El algoritmo explora el "Árbol de Decisiones": comprar o no comprar un producto.
#   2. Es RECURSIVO: Se llama a sí mismo probando cada opción.
#   3. Usa BACKTRACKING: Si se pasa del presupuesto, "retrocede" (return) y prueba 
#      otra rama del árbol.
#   4. Garantiza el Óptimo Global: Revisa las combinaciones para dar la mejor.
# =============================================================================

# --- 1. CONEXIÓN A SQL  ---
SERVER_NAME = 'PATRICKYIN'  
DATABASE_NAME = 'MiMercadito_Final'
connection_string = f"mssql+pyodbc://{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(connection_string)

def obtener_catalogo_precios():
    """Trae los productos y sus precios más baratos desde SQL"""
    query = """
    SELECT P.producto, MIN(O.precio_soles) as precio
    FROM OFERTAS O
    INNER JOIN PRODUCTOS P ON O.id_producto = P.id_producto
    GROUP BY P.producto
    """
    return pd.read_sql(query, engine)

# --- 2. EL ALGORITMO DE BACKTRACKING (El Núcleo) ---
def backtracking_compras(productos_disponibles, presupuesto, indice=0, canasta_actual=[]):
    #  productos o se acabó el dinero
    if indice >= len(productos_disponibles):
        return canasta_actual

    producto_actual = productos_disponibles.iloc[indice]
    nombre = producto_actual['producto']
    precio = float(producto_actual['precio'])

    # OPCIÓN A: INTENTAR AGREGAR EL PRODUCTO (Si alcanza el dinero)
    camino_con_producto = []
    if precio <= presupuesto:
        # Añadimos a la canasta y "avanzamos" restando el dinero
        nueva_canasta = canasta_actual + [{'producto': nombre, 'precio': precio}]
        camino_con_producto = backtracking_compras(
            productos_disponibles, 
            presupuesto - precio, 
            indice + 1, 
            nueva_canasta
        )

    # OPCIÓN B: SALTAR EL PRODUCTO 
    camino_sin_producto = backtracking_compras(
        productos_disponibles, 
        presupuesto, 
        indice + 1, 
        canasta_actual
    )

    # DECISIÓN: ¿Qué camino me dio más productos? (Maximizamos cantidad)
    if len(camino_con_producto) > len(camino_sin_producto):
        return camino_con_producto
    else:
        return camino_sin_producto

# --- 3. EJECUCIÓN ---
print("🔌 Descargando catálogo de precios de SQL Server...")
df_catalogo = obtener_catalogo_precios()
print(f"✅ Catálogo cargado: {len(df_catalogo)} productos disponibles.\n")

# DEFINIR EL ESCENARIO
PRESUPUESTO_FAMILIA = 30.00  # Ejemplo: La familia solo tiene 30 soles
print(f"🛒 PLANIFICADOR DE COMPRAS (Backtracking)")
print(f"💰 Presupuesto Límite: S/ {PRESUPUESTO_FAMILIA}")
print("🧠 Calculando la mejor combinación...")

# Ejecutar algoritmo
mejor_combinacion = backtracking_compras(df_catalogo, PRESUPUESTO_FAMILIA)

# MOSTRAR RESULTADOS
print("\n🏆 --- MEJOR COMBINACIÓN ENCONTRADA ---")
total_gastado = 0
for item in mejor_combinacion:
    print(f" - {item['producto']}: S/ {item['precio']}")
    total_gastado += item['precio']

print("--------------------------------------")
print(f"Total Artículos: {len(mejor_combinacion)}")
print(f"Total Gastado:   S/ {total_gastado:.2f}")
print(f"Vuelto (Sobra):  S/ {PRESUPUESTO_FAMILIA - total_gastado:.2f}")