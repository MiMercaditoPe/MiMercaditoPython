import pandas as pd

# Dataset: tiendas
# Columns inferred from uploaded file's header (if available).
columns = ["id_tienda", "nombre_tienda", "tipo", "distrito"]

data = [
    (1, "Plaza Vea Miraflores", "Supermercado", "Miraflores"),
    (10, "Mercado San Borja", "Mercado", "San Borja"),
    (11, "Tottus Jesús María", "Supermercado", "Jesús María"),
    (12, "Metro San Borja", "Supermercado", "San Borja"),
    (13, "Vivanda La Molina", "Supermercado", "La Molina"),
    (14, "Tottus Lince", "Supermercado", "Lince"),
    (15, "Wong San Isidro", "Supermercado", "San Isidro"),
    (16, "Metro Santiago de Surco", "Supermercado", "Santiago de Surco"),
    (17, "Bodega San Miguel", "Bodega", "San Miguel"),
    (18, "Mercado Callao", "Mercado", "Callao"),
    (19, "Mercado VES", "Mercado", "Villa El Salvador"),
    (2, "Mercado Central SMP", "Mercado", "San Martín de Porres"),
    (20, "Bodega Chorrillos", "Bodega", "Chorrillos"),
    (21, "Mercado Surquillo", "Mercado", "Surquillo"),
    (22, "Wong La Molina", "Supermercado", "La Molina")
]

df = pd.DataFrame(data, columns=columns)
# Save to CSV in the same folder as this script
df.to_csv("generated_tiendas.csv", index=False)
print("Saved generated_tiendas.csv with", len(df), "rows")
