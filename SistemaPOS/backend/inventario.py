import pandas as pd
import os

archivo_inventario = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventario.csv')

def leer_inventario():
    if os.path.exists(archivo_inventario):
        return pd.read_csv(archivo_inventario, dtype={'id_producto': str})
    else:
        df = pd.DataFrame(columns=['id_producto', 'nombre', 'descripcion', 'cantidad', 'precio_unitario', 'estado'])
        df.to_csv(archivo_inventario, index=False)
        return df

def guardar_inventario(df):
    df.to_csv(archivo_inventario, index=False)

def agregar_producto(id_producto, nombre, descripcion, cantidad, precio_unitario):
    df = leer_inventario()
    id_producto = str(id_producto).strip()
    if id_producto in df['id_producto'].astype(str).str.strip().values:
        raise ValueError("El producto ya existe.")
    nuevo = {
        'id_producto': id_producto,
        'nombre': nombre,
        'descripcion': descripcion,
        'cantidad': cantidad,
        'precio_unitario': precio_unitario,
        'estado': 'disponible'
    }
    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    guardar_inventario(df)

def retirar_producto(id_producto, cantidad):
    df = leer_inventario()
    id_producto = str(id_producto).strip()
    idx = df[df['id_producto'].astype(str).str.strip() == id_producto].index
    if len(idx) == 0:
        raise ValueError("Producto no encontrado.")
    i = idx[0]
    cantidad_actual = int(df.loc[i, 'cantidad'])
    if cantidad > cantidad_actual:
        raise ValueError("Cantidad insuficiente.")
    df.loc[i, 'cantidad'] = cantidad_actual - cantidad
    guardar_inventario(df)

def actualizar_producto(id_producto, nueva_cantidad=None, nuevo_precio=None):
    df = leer_inventario()
    id_producto = str(id_producto).strip()
    idx = df[df['id_producto'].astype(str).str.strip() == id_producto].index
    if len(idx) == 0:
        raise ValueError("Producto no encontrado.")
    i = idx[0]
    if nueva_cantidad is not None:
        df.loc[i, 'cantidad'] = nueva_cantidad
    if nuevo_precio is not None:
        df.loc[i, 'precio_unitario'] = nuevo_precio
    guardar_inventario(df)
