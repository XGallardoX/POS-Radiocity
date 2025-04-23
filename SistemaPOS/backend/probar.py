import pandas as pd
from inventario import agregar_producto, retirar_producto, actualizar_producto

# Prueba de agregar productos
agregar_producto(5, 'Producto C', 'Descripción C', 200, 400)
agregar_producto(6, 'Producto D', 'Descripción D', 30, 250)

# Retirar productos (supón que tienes un stock de 100 de Producto A)
retirar_producto(1, 90)  # Retira 10 productos del Producto A

# Actualizar Producto B a una nueva cantidad y precio
actualizar_producto(2, nueva_cantidad=9999, nuevo_precio=350)


from factura import generar_factura

# Definir los productos y el cliente
cliente = {'id': 1, 'nombre': 'Cliente Ejemplo', 'direccion': 'Calle Ficticia 123'}
productos = [
    {'nombre': 'Producto A', 'cantidad': 2, 'precio_unitario': 500},
    {'nombre': 'Producto B', 'cantidad': 1, 'precio_unitario': 300}
]
total = 1300

# Generar factura
generar_factura(cliente, productos, total)

from usuarios import login

# Prueba de login
rol = login('admin', 'admin123')  # Debería devolver 'ADMIN' si es correcto
print(f"Rol del usuario: {rol}")
