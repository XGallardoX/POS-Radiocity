import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENTAS_CSV = os.path.join(BASE_DIR, 'data', 'ventas.csv')


def cargar_datos_ventas():
    ruta = os.path.join(os.path.dirname(__file__), '..', 'data', 'ventas.csv')
    if not os.path.exists(ruta):
        return None
    df = pd.read_csv(ruta, parse_dates=["fecha"])
    return df if not df.empty else None

import pandas as pd
from collections import Counter

def resumen_ventas():
    try:
        df = pd.read_csv(VENTAS_CSV, parse_dates=["fecha"])
        if df.empty:
            return "No hay datos disponibles para análisis."

        total_ventas = df["subtotal"].sum()
        promedio_diario = df.groupby(df["fecha"].dt.date)["subtotal"].sum().mean()

        productos_vendidos = df.groupby("nombre")["cantidad"].sum().sort_values(ascending=False)
        ingresos_por_dia = df.groupby(df["fecha"].dt.date)["subtotal"].sum()

        resumen = f"""
========= Resumen de Ventas =========

Ventas Totales: ${total_ventas:,.2f}
Promedio Diario: ${promedio_diario:,.2f}

--- Productos Más Vendidos ---
"""
        for producto, cantidad in productos_vendidos.items():
            resumen += f"{producto}: {cantidad} unidades\n"

        resumen += "\n--- Ingresos por Día ---\n"
        for fecha, ingreso in ingresos_por_dia.items():
            resumen += f"{fecha}: ${ingreso:,.2f}\n"

        return resumen.strip()

    except FileNotFoundError:
        return "No se encontró el archivo de ventas."
    except Exception as e:
        return f"Error al generar resumen: {e}"

