import sys
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd

# Asegurar que se pueda importar desde la carpeta backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from ventas import resumen_ventas
from factura import generar_factura
from inventario import agregar_producto, retirar_producto, actualizar_producto, leer_inventario
from usuarios import login as verificar_login

# Crear la ventana principal
root = tk.Tk()
root.title("POS")
root.geometry("800x600")
root.config(bg="#f1f1f1")

# Paleta de colores
color_fondo = "#f1f1f1"
color_boton = "#4CAF50"
color_boton_hover = "#45a049"
color_texto = "#333333"

# Mostrar menú principal
def show_menu():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Menú Principal", font=("Arial", 24), bg=color_fondo, fg=color_texto).pack(pady=20)

    ttk.Button(root, text="Control de Inventario", style="Custom.TButton", command=open_inventario).pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)
    ttk.Button(root, text="Generar Factura Electrónica", style="Custom.TButton", command=generate_invoice).pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)
    ttk.Button(root, text="Análisis de Ventas", style="Custom.TButton", command=mostrar_analisis).pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)
    btn_ventas = ttk.Button(root, text="Ventas", style="Custom.TButton", command=open_ventas)
    btn_ventas.pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)
    ttk.Button(root, text="Cerrar Sesión", style="Custom.TButton", command=logout).pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)

# Inventario
def open_inventario():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Control de Inventario", font=("Arial", 20), bg=color_fondo, fg=color_texto).pack(pady=10)

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill='both', padx=20, pady=10)

    # Tab: Agregar Producto
    tab_agregar = ttk.Frame(tab_control)
    tab_control.add(tab_agregar, text='Agregar Producto')

    def agregar():
        try:
            agregar_producto(id_entry.get(), nombre_entry.get(), descripcion_entry.get(),
                             int(cantidad_entry.get()), float(precio_entry.get()))
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            mostrar_tabla_inventario()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Label(tab_agregar, text="ID:").pack()
    id_entry = tk.Entry(tab_agregar)
    id_entry.pack()

    tk.Label(tab_agregar, text="Nombre:").pack()
    nombre_entry = tk.Entry(tab_agregar)
    nombre_entry.pack()

    tk.Label(tab_agregar, text="Descripción:").pack()
    descripcion_entry = tk.Entry(tab_agregar)
    descripcion_entry.pack()

    tk.Label(tab_agregar, text="Cantidad:").pack()
    cantidad_entry = tk.Entry(tab_agregar)
    cantidad_entry.pack()

    tk.Label(tab_agregar, text="Precio Unitario:").pack()
    precio_entry = tk.Entry(tab_agregar)
    precio_entry.pack()

    ttk.Button(tab_agregar, text="Agregar", command=agregar).pack(pady=10)

    # Tab: Retirar Producto
    tab_retirar = ttk.Frame(tab_control)
    tab_control.add(tab_retirar, text='Retirar Producto')

    def retirar():
        try:
            retirar_producto(retirar_id_entry.get(), int(retirar_cantidad_entry.get()))
            messagebox.showinfo("Éxito", "Producto retirado correctamente.")
            mostrar_tabla_inventario()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Label(tab_retirar, text="ID Producto:").pack()
    retirar_id_entry = tk.Entry(tab_retirar)
    retirar_id_entry.pack()

    tk.Label(tab_retirar, text="Cantidad a Retirar:").pack()
    retirar_cantidad_entry = tk.Entry(tab_retirar)
    retirar_cantidad_entry.pack()

    ttk.Button(tab_retirar, text="Retirar", command=retirar).pack(pady=10)

    # Tab: Actualizar Producto
    tab_actualizar = ttk.Frame(tab_control)
    tab_control.add(tab_actualizar, text='Actualizar Producto')

    def actualizar():
        try:
            cantidad = nueva_cantidad_entry.get()
            precio = nuevo_precio_entry.get()
            actualizar_producto(actualizar_id_entry.get(),
                                int(cantidad) if cantidad else None,
                                float(precio) if precio else None)
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
            mostrar_tabla_inventario()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Label(tab_actualizar, text="ID Producto:").pack()
    actualizar_id_entry = tk.Entry(tab_actualizar)
    actualizar_id_entry.pack()

    tk.Label(tab_actualizar, text="Nueva Cantidad:").pack()
    nueva_cantidad_entry = tk.Entry(tab_actualizar)
    nueva_cantidad_entry.pack()

    tk.Label(tab_actualizar, text="Nuevo Precio:").pack()
    nuevo_precio_entry = tk.Entry(tab_actualizar)
    nuevo_precio_entry.pack()

    ttk.Button(tab_actualizar, text="Actualizar", command=actualizar).pack(pady=10)

    # Tab: Ver Inventario
    tab_ver = ttk.Frame(tab_control)
    tab_control.add(tab_ver, text='Ver Inventario')

    inventario_tree = ttk.Treeview(tab_ver, columns=('ID', 'Nombre', 'Descripción', 'Cantidad', 'Precio', 'Estado'), show='headings')
    for col in inventario_tree["columns"]:
        inventario_tree.heading(col, text=col)
        inventario_tree.column(col, minwidth=0, width=100)
    inventario_tree.pack(expand=True, fill='both', pady=10)

    def mostrar_tabla_inventario():
        for row in inventario_tree.get_children():
            inventario_tree.delete(row)
        df = leer_inventario()
        for _, row in df.iterrows():
            inventario_tree.insert('', 'end', values=tuple(row))

    mostrar_tabla_inventario()

    ttk.Button(root, text="Volver al Menú", style="Custom.TButton", command=show_menu).pack(pady=20)

#Ventas
def open_ventas():
    from inventario import leer_inventario
    from factura import generar_factura

    carrito = []

    def actualizar_carrito():
        carrito_listbox.delete(0, tk.END)
        total = 0
        for item in carrito:
            texto = f"{item['nombre']} x {item['cantidad']} = ${item['subtotal']:.2f}"
            carrito_listbox.insert(tk.END, texto)
            total += item['subtotal']
        total_label.config(text=f"Total: ${total:.2f}")

    def agregar_al_carrito():
        seleccionado = producto_combo.get()
        cantidad = int(cantidad_spinbox.get())
        if not seleccionado or cantidad <= 0:
            return messagebox.showerror("Error", "Producto o cantidad inválidos.")
        nombre, precio, id_producto = seleccionado.split(" | ")
        subtotal = float(precio) * cantidad
        carrito.append({
            'id_producto': id_producto,
            'nombre': nombre,
            'precio_unitario': float(precio),
            'cantidad': cantidad,
            'subtotal': subtotal
        })
        actualizar_carrito()

    def quitar_del_carrito():
        seleccion = carrito_listbox.curselection()
        if seleccion:
            del carrito[seleccion[0]]
            actualizar_carrito()

    def finalizar_venta():
        if not carrito:
            return messagebox.showwarning("Vacío", "No hay productos en el carrito.")
        generar_factura(carrito)
        messagebox.showinfo("Éxito", "Factura generada correctamente.")
        carrito.clear()
        actualizar_carrito()

    # UI
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Ventas", font=("Arial", 20), bg=color_fondo, fg=color_texto).pack(pady=10)

    frame = tk.Frame(root, bg=color_fondo)
    frame.pack(padx=10, pady=10, fill="x")

    # Productos disponibles
    df = leer_inventario()
    opciones = [f"{row['nombre']} | {row['precio_unitario']} | {row['id_producto']}" for _, row in df.iterrows()]
    producto_combo = ttk.Combobox(frame, values=opciones, width=40)
    producto_combo.pack(pady=5)

    cantidad_spinbox = tk.Spinbox(frame, from_=1, to=100, width=5)
    cantidad_spinbox.pack(pady=5)

    ttk.Button(frame, text="Agregar al Carrito", command=agregar_al_carrito).pack(pady=5)

    carrito_listbox = tk.Listbox(root, height=8, width=50)
    carrito_listbox.pack(pady=5)

    ttk.Button(root, text="Quitar Seleccionado", command=quitar_del_carrito).pack(pady=5)

    total_label = tk.Label(root, text="Total: $0.00", font=("Arial", 14), bg=color_fondo, fg=color_texto)
    total_label.pack(pady=5)

    ttk.Button(root, text="Finalizar Venta", command=finalizar_venta).pack(pady=10)

    ttk.Button(root, text="Volver al Menú", style="Custom.TButton", command=show_menu).pack(pady=20)


# Generar factura (aún por implementar)
def generate_invoice():
    messagebox.showinfo("Factura", "Generar factura electrónica...")

# Mostrar análisis de ventas
def mostrar_analisis():
    try:
        resumen = resumen_ventas()
        messagebox.showinfo("Análisis de Ventas", resumen)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Logout
def logout():
    show_login()

# Login
def show_login():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Iniciar Sesión", font=("Arial", 24), bg=color_fondo, fg=color_texto).pack(pady=20)

    tk.Label(root, text="Usuario", font=("Arial", 14), bg=color_fondo, fg=color_texto).pack(pady=5)
    username_entry = ttk.Entry(root, font=("Arial", 14))
    username_entry.pack(pady=10, ipadx=5, ipady=5, fill="x", padx=50)

    tk.Label(root, text="Contraseña", font=("Arial", 14), bg=color_fondo, fg=color_texto).pack(pady=5)
    password_entry = ttk.Entry(root, font=("Arial", 14), show="*")
    password_entry.pack(pady=10, ipadx=5, ipady=5, fill="x", padx=50)

    def handle_login():
        if username_entry.get() == "admin" and password_entry.get() == "admin123":
            show_menu()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    ttk.Button(root, text="Iniciar Sesión", style="Custom.TButton", command=handle_login).pack(pady=20, ipadx=10, ipady=10, fill="x", padx=50)

# Estilo personalizado
style = ttk.Style()
style.configure("Custom.TButton", font=("Arial", 14), padding=10, width=20)
style.map("Custom.TButton", background=[("active", color_boton_hover)])

# Iniciar con pantalla de login
show_login()

# Ejecutar app
root.mainloop()
