import pandas as pd
import os
from collections import Counter
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from matplotlib.backends.backend_pdf import PdfPages


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


def generar_pdf_analisis():
    # Cargar los datos de ventas
    df = cargar_datos()
    if df.empty:
        return "No hay datos disponibles para análisis."

    # Crear el PDF
    pdf_path = "analisis_ventas.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Análisis de Ventas")

    # Resumen de ventas
    c.setFont("Helvetica", 12)
    y_position = height - 80  # Posición inicial para el texto

    resumen = resumen_general()
    if isinstance(resumen, str):  # Si es mensaje de error
        c.drawString(100, y_position, resumen)
        c.save()
        return pdf_path

    # Añadir resumen de ventas al PDF
    for key, value in resumen.items():
        c.drawString(100, y_position, f"{key}:")
        y_position -= 15  # Espacio entre líneas

        if isinstance(value, dict):  # Productos más vendidos o ingresos por día
            for sub_key, sub_value in value.items():
                c.drawString(120, y_position, f"  {sub_key}: {sub_value}")
                y_position -= 15
        else:
            c.drawString(120, y_position, f"  {value}")
            y_position -= 15  # Espacio entre líneas

        if y_position < 50:  # Si llegamos al final de la página, agregar nueva página
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 50  # Reiniciar la posición

    # Crear gráficas y añadir al PDF

    # Gráfico 1: Ingresos por producto
    fig, ax = plt.subplots(figsize=(6, 4))
    ingresos = df.groupby('nombre')['subtotal'].sum().sort_values(ascending=False)
    ax.bar(ingresos.index, ingresos.values)
    ax.set_title("Ingresos por Producto")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    graph_path = "temp_ingresos.png"
    plt.savefig(graph_path)
    plt.close()
    c.showPage()  # Nueva página para la gráfica
    c.drawImage(graph_path, 100, height - 400, width=400, height=300)

    # Gráfico 2: Cantidad por producto
    fig, ax = plt.subplots(figsize=(6, 4))
    cantidades = df.groupby('nombre')['cantidad'].sum().sort_values(ascending=False)
    ax.bar(cantidades.index, cantidades.values, color='orange')
    ax.set_title("Unidades Vendidas por Producto")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    graph_path = "temp_cantidades.png"
    plt.savefig(graph_path)
    plt.close()
    c.showPage()  # Nueva página para la gráfica
    c.drawImage(graph_path, 100, height - 400, width=400, height=300)

    # Gráfico 3: Ingresos por Día
    fig, ax = plt.subplots(figsize=(6, 4))
    ingresos_dia = ingresos_por_dia(df)
    ax.bar(ingresos_dia.index, ingresos_dia.values, color='green')
    ax.set_title("Ingresos por Día")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    graph_path = "temp_ingresos_dia.png"
    plt.savefig(graph_path)
    plt.close()
    c.showPage()  # Nueva página para la gráfica
    c.drawImage(graph_path, 100, height - 400, width=400, height=300)

    # Gráfico 4: Distribución del Promedio Diario
    fig, ax = plt.subplots(figsize=(6, 4))
    ingresos_diarios = ingresos_por_dia(df)
    ax.plot(ingresos_diarios.index, ingresos_diarios.values, marker='o', color='blue')
    ax.set_title("Distribución del Promedio Diario")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Ingresos")
    plt.tight_layout()
    graph_path = "temp_promedio_diario.png"
    plt.savefig(graph_path)
    plt.close()
    c.showPage()  # Nueva página para la gráfica
    c.drawImage(graph_path, 100, height - 400, width=400, height=300)

    # Gráfico 5: Productos Más Vendidos
    fig, ax = plt.subplots(figsize=(6, 4))
    productos = productos_mas_vendidos(df)
    ax.bar(productos.index, productos.values, color='purple')
    ax.set_title("Productos Más Vendidos")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    graph_path = "temp_productos_vendidos.png"
    plt.savefig(graph_path)
    plt.close()
    c.showPage()  # Nueva página para la gráfica
    c.drawImage(graph_path, 100, height - 400, width=400, height=300)

    # Guardar el PDF
    c.save()

    # Eliminar las imágenes temporales de las gráficas
    os.remove("temp_ingresos.png")
    os.remove("temp_cantidades.png")
    os.remove("temp_ingresos_dia.png")
    os.remove("temp_promedio_diario.png")
    os.remove("temp_productos_vendidos.png")

    return pdf_path
