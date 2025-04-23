from fpdf import FPDF
import pandas as pd
import pandas as pd
from datetime import datetime
import os


# Función para generar la factura en PDF
def generar_factura(cliente, productos, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    
    # Información de la empresa
    pdf.cell(200, 10, txt="Factura Electrónica - Nombre de la Empresa", ln=True)
    
    # Información del cliente
    pdf.cell(200, 10, txt=f"Cliente: {cliente['nombre']}", ln=True)
    pdf.cell(200, 10, txt=f"Dirección: {cliente['direccion']}", ln=True)

    # Detalles de los productos
    pdf.cell(200, 10, txt="Productos:", ln=True)
    for producto in productos:
        pdf.cell(200, 10, txt=f"{producto['nombre']} - Cantidad: {producto['cantidad']} - Precio: {producto['precio_unitario']}", ln=True)
    
    # Total
    pdf.cell(200, 10, txt=f"Total: {total}", ln=True)
    pdf.output(f"factura_{cliente['id']}.pdf")
    print(f"Factura generada para el cliente {cliente['nombre']}.")

def generar_factura(productos, total):
    if not productos:
        return

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f'factura_{now}.csv'
    ruta_archivo = os.path.join('data', nombre_archivo)

    df = pd.DataFrame(productos)
    df["total"] = total
    df.to_csv(ruta_archivo, index=False)
    print(f"Factura guardada en {ruta_archivo}")

# Ejemplo de uso
#cliente = {'id': 1, 'nombre': 'Cliente Ejemplo', 'direccion': 'Calle Ficticia 123'}
#productos = [{'nombre': 'Producto A', 'cantidad': 2, 'precio_unitario': 500},
#             {'nombre': 'Producto B', 'cantidad': 1, 'precio_unitario': 300}]
#total = 1300
#generar_factura(cliente, productos, total)
