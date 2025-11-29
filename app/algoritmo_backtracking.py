import pandas as pd
from sqlalchemy import create_engine
import sys
import networkx as nx
import math
from itertools import combinations
from typing import List, Dict, Tuple

# =============================================================================
# MOTOR DE OPTIMIZACIÓN FINAL (Backtracking + Dijkstra)
# OBJETIVO: Máxima cantidad de ítems dentro del presupuesto, ponderando el costo
#          de traslado. [IMPLEMENTACIÓN DE LOS CÍRCULOS ROJOS] :D
# =============================================================================

# --- VARIABLES GLOBALES PARA TRACKING ---
mejor_combinacion = []
mejor_cantidad = 0

# --- 1. CONEXIÓN A SQL ---
SERVER_NAME = 'PATRICKYIN'  
DATABASE_NAME = 'MiMercadito_Final'
connection_string = f"mssql+pyodbc://{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&autocommit=true"
engine = create_engine(connection_string)


def obtener_ofertas_y_distrito(productos_deseados: List[str], distrito_hogar: str) -> pd.DataFrame:
    """ Trae las ofertas más baratas por producto (ponderadas por costo de viaje). """
    if not productos_deseados:
        return pd.DataFrame()
    
    # 1. PREPARAR CONSULTA SQL (Manejo robusto de 1 vs N productos)
    if len(productos_deseados) == 1:
        where_clause = f"P.producto = ?"
        params = [productos_deseados[0]] 
    else:
        placeholders = ','.join(['?'] * len(productos_deseados))
        where_clause = f"P.producto IN ({placeholders})"
        params = tuple(productos_deseados)

    query = f"""
    SELECT 
        P.producto,
        O.precio_soles AS precio_producto,
        T.nombre_tienda,
        T.id_tienda,
        T.distrito AS distrito_tienda
    FROM OFERTAS O
    INNER JOIN PRODUCTOS P ON O.id_producto = P.id_producto
    INNER JOIN TIENDAS T ON O.id_tienda = T.id_tienda
    WHERE {where_clause}
    """
    
    df_ofertas_raw = pd.read_sql(query, engine, params=params)
    
    if df_ofertas_raw.empty:
        return pd.DataFrame()

    # 2. Ponderar costo con distancia (Algoritmo Dijkstra)
    df_ofertas_raw['costo_traslado'] = df_ofertas_raw['distrito_tienda'].apply(
        lambda dest_distrito: obtener_costo_traslado(distrito_hogar, dest_distrito)
    )
    
    # 3. Métrica Final: Precio Ponderado = Producto + Viaje
    df_ofertas_raw['precio_total_ponderado'] = df_ofertas_raw['precio_producto'] + df_ofertas_raw['costo_traslado']
    
    # 4. Regla de Unicidad: Seleccionar SOLO la mejor oferta ponderada por producto
    idx = df_ofertas_raw.groupby(['producto'])['precio_total_ponderado'].idxmin()
    df_ofertas_filtradas = df_ofertas_raw.loc[idx].reset_index(drop=True)
    
    return df_ofertas_filtradas


# --- 2. BASE DE DATOS GEOGRÁFICA (MAPA DE LIMA) ---
MAPA_LIMA = {
    'Comas': {'San Martin de Porres': 8, 'San Juan de Lurigancho': 12},
    'San Martin de Porres': {'Comas': 8, 'Callao': 9, 'Jesus Maria': 9},
    'Callao': {'San Martin de Porres': 9, 'San Miguel': 3},
    'San Miguel': {'Callao': 3, 'Pueblo Libre': 3},
    'Pueblo Libre': {'San Miguel': 3, 'Jesus Maria': 4, 'Surquillo': 18},
    'Jesus Maria': {'San Martin de Porres': 9, 'Pueblo Libre': 4, 'Lince': 3},
    'Lince': {'Jesus Maria': 3, 'San Isidro': 4},
    'San Isidro': {'Lince': 4, 'San Borja': 3, 'Surquillo': 2},
    'Surquillo': {'San Isidro': 2, 'Miraflores': 7, 'Santiago de Surco': 4},
    'Miraflores': {'Surquillo': 7, 'Barranco': 2, 'San Borja': 9},
    'Barranco': {'Miraflores': 2, 'Chorrillos': 2},
    'Chorrillos': {'Barranco': 2, 'Santiago de Surco': 7, 'Villa El Salvador': 11},
    'Santiago de Surco': {'Surquillo': 4, 'Chorrillos': 7, 'San Borja': 4},
    'San Borja': {'San Isidro': 3, 'Santiago de Surco': 4, 'La Molina': 5},
    'La Molina': {'San Borja': 5, 'San Juan de Lurigancho': 13, 'Villa El Salvador': 9},
    'San Juan de Lurigancho': {'Comas': 12, 'La Molina': 13, 'Surquillo': 10}
}
GRAFO_DISTANCIA = nx.Graph(MAPA_LIMA)

def obtener_costo_traslado(distrito_origen: str, distrito_destino: str) -> float:
    """ Calcula el costo mínimo de traslado (km) entre dos distritos usando Dijkstra. """
    try:
        costo = nx.shortest_path_length(
            GRAFO_DISTANCIA, 
            source=distrito_origen, 
            target=distrito_destino, 
            weight='weight' 
        )
        return float(costo)
    except nx.NetworkXNoPath:
        return 1000.0
    except nx.NodeNotFound:
        return 500.0 


# --- 3. ALGORITMO BACKTRACKING (Núcleo) ---
mejor_combinacion = []
mejor_cantidad = 0

def backtracking_compras(productos_disponibles_df, presupuesto_restante, indice=0, canasta_actual=None):
    """ Función recursiva para la optimización de la canasta (Fuerza Bruta). """
    global mejor_combinacion, mejor_cantidad
    
    if canasta_actual is None:
        canasta_actual = []
    
    # Caso base: llegamos al final de la lista
    if indice >= len(productos_disponibles_df):
        # ÚNICA REGLA DE DECISIÓN: Maximizamos la cantidad de ítems
        if len(canasta_actual) > mejor_cantidad:
            mejor_cantidad = len(canasta_actual)
            mejor_combinacion = canasta_actual.copy()
        return

    producto_actual_df = productos_disponibles_df.iloc[indice]
    
    # --- Datos esenciales ---
    nombre = producto_actual_df['producto']
    tienda = producto_actual_df['nombre_tienda']
    precio_ponderado = float(producto_actual_df['precio_total_ponderado'])
    precio_producto = float(producto_actual_df['precio_producto'])
    costo_traslado = float(producto_actual_df['costo_traslado'])

    # Opción 1: Incluir el producto/tienda (si cabe en el presupuesto ponderado)
    if precio_ponderado <= presupuesto_restante:
        item = {
            'producto': nombre, 
            'precio_producto': precio_producto, 
            'tienda': tienda,
            'costo_traslado': costo_traslado,
        }
        backtracking_compras(
            productos_disponibles_df,
            presupuesto_restante - precio_ponderado,
            indice + 1,
            canasta_actual + [item]
        )
    
    # Opción 2: Excluir el producto/tienda (seguir explorando)
    backtracking_compras(
        productos_disponibles_df,
        presupuesto_restante,
        indice + 1,
        canasta_actual
    )


# --- 4. FUNCIÓN PRINCIPAL DE EJECUCIÓN ---
def ejecutar_optimizacion(presupuesto, productos_deseados, distrito_familia):
    """ Función que ejecuta el flujo completo de optimización. """
    global mejor_combinacion, mejor_cantidad
    
    df_ofertas_filtradas = obtener_ofertas_y_distrito(productos_deseados, distrito_familia)
    
    if df_ofertas_filtradas.empty:
        return [], [], 0.0, 0.0, 0.0, "ERROR_PRODUCTO_NO_ENCONTRADO_EN_OFERTAS"

    # 4.1 Reiniciar y ejecutar Backtracking
    mejor_combinacion = []
    mejor_cantidad = 0
    
    # Ejecutamos el algoritmo de Backtracking
    backtracking_compras(df_ofertas_filtradas, presupuesto) 

    # 4.2 Calcular totales
    total_gastado = sum(item['precio_producto'] for item in mejor_combinacion)
    
    return mejor_combinacion, [], total_gastado, presupuesto - total_gastado, 0.0, "OK"


# --- 5. LÓGICA DE RECOMENDACIÓN DE VUELTO (BASADA EN EXCEDENTE) ---
def recomendar_productos_extra(presupuesto_extra, productos_ya_comprados):
    """
    Busca productos que el usuario NO compró, cuyo precio sea <= presupuesto_extra.
    Prioriza los más caros para maximizar el uso del excedente.
    [SOLUCIONA EL ARGUMENTERROR AL TRATAR LA EXCLUSIÓN]
    """
    if presupuesto_extra <= 0:
        return pd.DataFrame()
        
    # 1. Lista de nombres de productos ya comprados para exclusión
    nombres_comprados = [item['producto'] for item in productos_ya_comprados]
    
    # 2. CONSTRUIR LA CLÁUSULA WHERE para exclusión (Lógica de exclusión de strings)
    if not nombres_comprados:
        where_clause = "1=1" 
        params_final = [presupuesto_extra]
    elif len(nombres_comprados) == 1:
        # Caso de un solo producto (Usa != ? y el producto va como segundo parámetro)
        where_clause = "P.producto != ?"
        params_final = [presupuesto_extra, nombres_comprados[0]]
    else:
        # Caso de múltiples productos (Usa NOT IN (...) y el presupuesto es el primer parámetro)
        placeholders = ','.join(['?'] * len(nombres_comprados))
        where_clause = f"P.producto NOT IN ({placeholders})"
        params_final = [presupuesto_extra] + nombres_comprados
    
    # 3. Consulta SQL: Busca productos bajo el presupuesto extra
    query = f"""
    SELECT TOP 5 P.producto, MIN(O.precio_soles) AS precio
    FROM OFERTAS O
    INNER JOIN PRODUCTOS P ON O.id_producto = P.id_producto
    GROUP BY P.producto
    HAVING MIN(O.precio_soles) <= ? AND {where_clause}
    ORDER BY MIN(O.precio_soles) DESC;
    """
    
    try:
        # Ejecutamos, pasando [presupuesto, P1, P2...] como parámetros
        return pd.read_sql(query, engine, params=params_final)
    except Exception:
        return pd.DataFrame()


# --- 6. FUNCIONES DE INTERFAZ Y UTULIDADES ---

def obtener_lista_productos_disponibles():
    query = "SELECT DISTINCT producto FROM PRODUCTOS ORDER BY producto ASC"
    df = pd.read_sql(query, engine)['producto'].tolist()
    return df

def obtener_lista_distritos():
    return list(GRAFO_DISTANCIA.nodes)

def seleccionar_productos_deseados(lista_productos_total):
    print("\n--- 📝 LISTA DE DESEOS ---")
    for i, prod in enumerate(lista_productos_total):
        print(f"[{i+1:3}] {prod}")
    print("-" * 50)

    while True: # Loop para manejar la entrada inválida
        entrada = input("👉 Elige los números de los productos (ej: 1, 3, 7, 12): ").strip()
        
        if not entrada:
            print("No seleccionaste nada.")
            return []
        
        try:
            indices = [int(x.strip()) - 1 for x in entrada.split(',')]
            
            # Validar que NO haya números fuera de rango (el error que querías evitar)
            if any(i < 0 or i >= len(lista_productos_total) for i in indices):
                print(f"❌ Advertencia: ¡Número de producto fuera de rango! Vuelve a intentar.")
                continue # Vuelve a pedir la entrada
                
            productos_elegidos = [lista_productos_total[i] for i in indices]
            return productos_elegidos
        
        except ValueError:
            print("❌ Error: Ingresa solo números separados por comas.")
            continue # Vuelve a pedir la entrada

def seleccionar_distrito_usuario(lista_distritos):
    print("\n--- 📍 DISTRITO DE ORIGEN ---")
    for i, distrito in enumerate(lista_distritos):
        print(f"[{i+1:2}] {distrito}")
    print("-" * 25)
    
    while True:
        try:
            entrada = input("👉 Elige el número de tu distrito: ").strip()
            indice = int(entrada) - 1
            if 0 <= indice < len(lista_distritos):
                return lista_distritos[indice]
            print("Número fuera de rango.")
        except:
            print("Entrada inválida.")
            
# --- 7. ZONA DE PRUEBA MANUAL (FINAL) ---
if __name__ == "__main__":
    
    # 1. Carga inicial de datos
    lista_productos_total = obtener_lista_productos_disponibles()
    lista_distritos_total = obtener_lista_distritos()
    
    if not lista_productos_total or not lista_distritos_total:
        sys.exit("❌ Error: No se encontraron datos para iniciar la optimización.")

    # 2. Obtener la selección del usuario
    productos_elegidos = seleccionar_productos_deseados(lista_productos_total)
    
    if not productos_elegidos:
        sys.exit(0)
        
    distrito_origen = seleccionar_distrito_usuario(lista_distritos_total)
        
    # 3. Obtener Presupuesto
    while True:
        try:
            entrada = input(f"\n💸 Ingresa presupuesto (Tu distrito: {distrito_origen}): S/ ").strip()
            PRESUPUESTO = float(entrada)
            if PRESUPUESTO <= 0:
                print("El presupuesto debe ser mayor a 0.")
                continue
            break
        except:
            print("Por favor ingresa un número válido.")
            
    # 4. Ejecutar Optimización
    print(f"\nCalculando mejor canasta y ruta para S/ {PRESUPUESTO:.2f}...")
    
    canasta, tiendas_ruta, gasto, vuelto, costo_ruta_mst, estado = ejecutar_optimizacion(PRESUPUESTO, productos_elegidos, distrito_origen)
    
    # --- 5. Resultados y Exhibición ---
    print("\n" + "="*60)
    print(f"           INFORME FINAL DE OPTIMIZACIÓN")
    print("="*60)
    
    if estado != "OK":
        print(f"❌ La optimización no pudo completar el proceso. Estado: {estado}")
    elif not canasta:
        # LÓGICA DE SUGERENCIA DE BAJO PRESUPUESTO
        print("No es posible comprar nada con ese presupuesto o selección.")
        
        # Obtenemos la información de las ofertas para sugerir (Solo si el presupuesto es > 0)
        if PRESUPUESTO > 0:
            df_ofertas_ponderadas = obtener_ofertas_y_distrito(productos_elegidos, distrito_origen)
            
            if not df_ofertas_ponderadas.empty:
                costo_minimo_requerido = df_ofertas_ponderadas['precio_total_ponderado'].min()
                
                if costo_minimo_requerido > PRESUPUESTO:
                    falta = costo_minimo_requerido - PRESUPUESTO
                    print(f"\n❌ AVISO: El costo mínimo de un artículo excede tu presupuesto.")
                    print(f"💡 Necesitas al menos S/ {falta:.2f} más para empezar a comprar.")
                else:
                    print("🤔 SUGERENCIA: El presupuesto es bajo. Intenta con menos artículos.")
        
    else:
        # --- CASO DE ÉXITO ---
        print(f"🏡 Distrito Origen: {distrito_origen}")
        print(f"💰 Presupuesto Inicial: S/ {PRESUPUESTO:.2f}")
        print("\n🏆 Canasta Óptima Encontrada (Máxima cantidad de ítems):")
        
        total_traslado_acumulado = 0
        
        # Lógica para encontrar ítems omitidos
        productos_comprados_nombres = {item['producto'] for item in canasta}
        productos_no_comprados = set(productos_elegidos) - productos_comprados_nombres

        for item in canasta:
            print(f"   • {item['producto']:<25} @ {item['tienda']:<15} (+{item['costo_traslado']:.1f} km) S/ {item['precio_producto']:6.2f}")
            total_traslado_acumulado += item['costo_traslado']
        
        print("-" * 60)
        
        if productos_no_comprados:
            print(f"⚠️ ATENCIÓN: {len(productos_no_comprados)} ítems NO incluidos para maximizar la canasta.")
            print(f"   Omitidos: {', '.join(productos_no_comprados)}")
            print("-" * 60)

        # LÓGICA DE RECOMENDACIÓN DINÁMICA (Si sobra dinero)
        if vuelto >= 10.0: # Regla de negocio: Si sobra S/ 10.00 o más
            print("\n🎉 ¡TIENES UN PRESUPUESTO EXTRA!")
            
            df_recomendaciones = recomendar_productos_extra(vuelto, canasta)
            
            if not df_recomendaciones.empty:
                print("🎁 PRODUCTOS RECOMENDADOS para aprovechar el excedente:")
                
                for index, item in df_recomendaciones.iterrows():
                     print(f"   • {item['producto']:<35}   S/ {item['precio']:.2f}")
                print("-" * 60)
        
        
        print(f"Total Gastado (Producto): S/ {gasto:.2f}")
        print(f"Total KM Recorridos (Dijkstra): {total_traslado_acumulado:.1f} km")
        print(f"Dinero Sobrante:          S/ {vuelto:.2f}")
        print("="*60)