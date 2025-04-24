import os
import pandas as pd
import uuid
from datetime import datetime
from inventario import actualizar_producto

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENTAS_CSV = os.path.join(BASE_DIR, 'data', 'ventas.csv')


def registrar_venta(carrito, total):
    # Comprobar si ya existe el archivo, si no, crear un DataFrame vacío
    try:
        df = pd.read_csv(VENTAS_CSV)
    except FileNotFoundError:
        # Si no existe el archivo, crear un DataFrame vacío con las columnas adecuadas
        df = pd.DataFrame(columns=['id_venta', 'fecha', 'id_producto', 'nombre', 'cantidad', 'precio_unitario', 'subtotal'])
    
    # Crear un nuevo ID de venta y fecha
    id_venta = str(uuid.uuid4())[:8]
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Registrar productos en la venta
    for item in carrito:
        nueva_venta = {
            'id_venta': id_venta,
            'fecha': fecha,
            'id_producto': item['id_producto'],
            'nombre': item['nombre'],
            'cantidad': item['cantidad'],
            'precio_unitario': item['precio_unitario'],
            'subtotal': item['subtotal']
        }
        # Asegurarse de que el producto se ha añadido correctamente al DataFrame
        print(f"Añadiendo al DataFrame: {nueva_venta}")
        df = pd.concat([df, pd.DataFrame([nueva_venta])], ignore_index=True)

        # Actualizar inventario restando la cantidad vendida
        nueva_cantidad = item['cantidad']  # Calcular la cantidad restante
        actualizar_producto(item['id_producto'], nueva_cantidad=nueva_cantidad)

    # Depuración: Verificar el contenido de df antes de guardar
    print(f"Contenido de df antes de guardar:\n{df}")

    # Verificar que el archivo CSV tiene la ruta correcta
    print(f"Guardando en el archivo: {VENTAS_CSV}")
    
    # Verificar si el directorio existe y crearlo si no es así
    directory = os.path.dirname(VENTAS_CSV)
    if not os.path.exists(directory):
        print(f"El directorio {directory} no existe. Creándolo.")
        os.makedirs(directory)
    
    # Intentar guardar el DataFrame en el archivo CSV
    try:
        df.to_csv(VENTAS_CSV, index=False)
        print(f"Archivo guardado exitosamente en {VENTAS_CSV}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

    return id_venta, fecha
