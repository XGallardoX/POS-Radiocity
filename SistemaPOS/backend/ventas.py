import pandas as pd
from datetime import datetime

def resumen_ventas():
    try:
        df = pd.read_csv("data/ventas.csv", parse_dates=["fecha"])
    except FileNotFoundError:
        return "No hay registros de ventas todavía."

    resumen = ""

    total_ventas = df["cantidad"].sum()
    total_ingresos = (df["cantidad"] * df["precio_unitario"]).sum()
    promedio_por_factura = (df["cantidad"] * df["precio_unitario"]).groupby(df["id_factura"]).sum().mean()

    producto_mas_vendido = df.groupby("id_producto")["cantidad"].sum().idxmax()
    cantidad_mas_vendida = df.groupby("id_producto")["cantidad"].sum().max()

    resumen += f"📅 Ventas registradas: {len(df)}\n"
    resumen += f"🛒 Total productos vendidos: {total_ventas}\n"
    resumen += f"💰 Ingresos totales: ${total_ingresos:,.2f}\n"
    resumen += f"📈 Promedio por factura: ${promedio_por_factura:,.2f}\n"
    resumen += f"🔥 Producto más vendido (ID): {producto_mas_vendido} ({cantidad_mas_vendida} unidades)\n"

    return resumen
