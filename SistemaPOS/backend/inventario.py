import pandas as pd

# Función para agregar un producto al inventario
def agregar_producto(id_producto, nombre, descripcion, cantidad, precio_unitario):
    # Verifica si el archivo CSV existe, si no lo crea
    try:
        df = pd.read_csv('data/inventario.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['id_producto', 'nombre', 'descripcion', 'cantidad', 'precio_unitario', 'estado'])

    nuevo_producto = {
        'id_producto': id_producto, 
        'nombre': nombre, 
        'descripcion': descripcion, 
        'cantidad': cantidad, 
        'precio_unitario': precio_unitario, 
        'estado': 'activo'
    }

    # Usamos pd.concat para agregar el nuevo producto
    df = pd.concat([df, pd.DataFrame([nuevo_producto])], ignore_index=True)
    
    df.to_csv('data/inventario.csv', index=False)
    print(f"Producto {nombre} agregado al inventario.")

# Función para retirar un producto del inventario
def retirar_producto(id_producto, cantidad):
    try:
        df = pd.read_csv('data/inventario.csv')
    except FileNotFoundError:
        print("No se encontró el archivo de inventario.")
        return
    
    producto = df[df['id_producto'] == id_producto]
    
    if producto.empty:
        print("Producto no encontrado.")
        return

    cantidad_actual = producto['cantidad'].values[0]
    if cantidad_actual >= cantidad:
        # Actualizamos la cantidad del producto en lugar de agregarlo de nuevo
        df.loc[df['id_producto'] == id_producto, 'cantidad'] -= cantidad
        df.to_csv('data/inventario.csv', index=False)
        print(f"Producto {id_producto} retirado. Nueva cantidad: {cantidad_actual - cantidad}")
    else:
        print("No hay suficiente stock para retirar.")

# Función para actualizar un producto
def actualizar_producto(id_producto, nueva_cantidad=None, nuevo_precio=None):
    try:
        df = pd.read_csv('data/inventario.csv')
    except FileNotFoundError:
        print("No se encontró el archivo de inventario.")
        return
    
    # Verificar si el producto existe
    if id_producto not in df['id_producto'].values:
        print("Producto no encontrado.")
        return

    if nueva_cantidad is not None:
        # Actualizamos la cantidad
        df.loc[df['id_producto'] == id_producto, 'cantidad'] = nueva_cantidad

    if nuevo_precio is not None:
        # Actualizamos el precio
        df.loc[df['id_producto'] == id_producto, 'precio_unitario'] = nuevo_precio
    
    # Guardamos los cambios en el CSV
    df.to_csv('data/inventario.csv', index=False)
    print(f"Producto {id_producto} actualizado.")