import pandas as pd
from sqlalchemy import create_engine

# 1. Por favor, restaure la base de datos usando el archivo .bak adjunto.
# 2. CAMBIE el valor de 'SERVER_NAME' por el nombre de SU servidor SQL local.

SERVER_NAME = 'PATRICKYIN' 
DATABASE_NAME = 'MiMercadito_Final'

# Crear puente conexión  usando mi sql >:D
connection_string = f"mssql+pyodbc://{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(connection_string)

try:
    
    print("🔌 Intentando conectar a SQL Server...")
    
    query = "SELECT * FROM PRODUCTOS"
    df_productos = pd.read_sql(query, engine)
    
    print("✅ ¡CONEXIÓN EXITOSA!")
    print(f"Se descargaron {len(df_productos)} productos desde la Base de Datos.")
    print(df_productos.head())

except Exception as e:
    print("❌ Error de conexión. Revisa el nombre del servidor.")
    print(e)