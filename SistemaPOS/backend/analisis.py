import pandas as pd
import sys
import os
from collections import Counter


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENTAS_CSV = os.path.join(BASE_DIR, 'data', 'ventas.csv')


def cargar_datos():
    try:
        df = pd.read_csv(VENTAS_CSV)
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    except FileNotFoundError:
        print("Archivo de ventas no encontrado.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        print("Archivo de ventas vacío.")
        return pd.DataFrame()

def ventas_totales(df):
    return df['subtotal'].sum()

def productos_mas_vendidos(df, top_n=5):
    conteo = df.groupby('nombre')['cantidad'].sum()
    return conteo.sort_values(ascending=False).head(top_n)

def ingresos_por_dia(df):
    return df.groupby(df['fecha'].dt.date)['subtotal'].sum()

def promedio_ventas_diario(df):
    ingresos = ingresos_por_dia(df)
    return ingresos.mean()

def resumen_general():
    df = cargar_datos()
    if df.empty:
        return "No hay datos disponibles para análisis."
    
    resumen = {
        "Ventas Totales ($)": ventas_totales(df),
        "Productos Más Vendidos": productos_mas_vendidos(df).to_dict(),
        "Ingresos por Día": ingresos_por_dia(df).to_dict(),
        "Promedio Diario ($)": promedio_ventas_diario(df)
    }
    return resumen
