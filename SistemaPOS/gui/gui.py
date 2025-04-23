import sys
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))) ##llamar la carpeta backend bb

from ventas import resumen_ventas
from factura import generar_factura  # por ejemplo
from inventario import agregar_producto, retirar_producto, actualizar_producto
from usuarios import login



# Crear la ventana principal
root = tk.Tk()
root.title("POS")
root.geometry("600x400")
root.config(bg="#f1f1f1")

# Definir la paleta de colores
color_fondo = "#f1f1f1"
color_boton = "#4CAF50"
color_boton_hover = "#45a049"
color_texto = "#333333"

# Función para mostrar el menú de opciones
def show_menu():
    # Limpiar la ventana principal
    for widget in root.winfo_children():
        widget.destroy()
    
    # Crear un título
    title_label = tk.Label(root, text="Menú Principal", font=("Arial", 24), bg=color_fondo, fg=color_texto)
    title_label.pack(pady=20)

    # Botones de acción
    btn_inventario = ttk.Button(root, text="Control de Inventario", style="Custom.TButton", command=open_inventario)
    btn_inventario.pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)

    btn_factura = ttk.Button(root, text="Generar Factura Electrónica", style="Custom.TButton", command=generate_invoice)
    btn_factura.pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)

    btn_analisis = ttk.Button(root, text="Análisis de Ventas", style="Custom.TButton", command=mostrar_analisis)
    btn_analisis.pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)

    btn_logout = ttk.Button(root, text="Cerrar Sesión", style="Custom.TButton", command=logout)
    btn_logout.pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)

    
# Funciones de acción para los botones
def open_inventario():
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Control de Inventario", font=("Arial", 20), bg=color_fondo, fg=color_texto).pack(pady=20)

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill='both', padx=20, pady=10)

    # Pestaña para agregar producto
    tab_agregar = ttk.Frame(tab_control)
    tab_control.add(tab_agregar, text='Agregar Producto')

    def agregar():
        try:
            agregar_producto(
                id_entry.get(),
                nombre_entry.get(),
                descripcion_entry.get(),
                int(cantidad_entry.get()),
                float(precio_entry.get())
            )
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
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

    # Pestaña para retirar producto
    tab_retirar = ttk.Frame(tab_control)
    tab_control.add(tab_retirar, text='Retirar Producto')

    def retirar():
        try:
            retirar_producto(retirar_id_entry.get(), int(retirar_cantidad_entry.get()))
            messagebox.showinfo("Éxito", "Producto retirado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Label(tab_retirar, text="ID Producto:").pack()
    retirar_id_entry = tk.Entry(tab_retirar)
    retirar_id_entry.pack()

    tk.Label(tab_retirar, text="Cantidad a Retirar:").pack()
    retirar_cantidad_entry = tk.Entry(tab_retirar)
    retirar_cantidad_entry.pack()

    ttk.Button(tab_retirar, text="Retirar", command=retirar).pack(pady=10)

    # Pestaña para actualizar producto
    tab_actualizar = ttk.Frame(tab_control)
    tab_control.add(tab_actualizar, text='Actualizar Producto')

    def actualizar():
        try:
            cantidad = nueva_cantidad_entry.get()
            precio = nuevo_precio_entry.get()
            actualizar_producto(
                actualizar_id_entry.get(),
                int(cantidad) if cantidad else None,
                float(precio) if precio else None
            )
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
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

    # Botón para volver al menú
    ttk.Button(root, text="Volver al Menú", style="Custom.TButton", command=show_menu).pack(pady=20)

    #messagebox.showinfo("Inventario", "Abrir control de inventario...")

def generate_invoice():
    # Llamar a la interfaz de generación de factura
    messagebox.showinfo("Factura", "Generar factura electrónica...")

def logout():
    # Función para cerrar sesión y volver al login
    show_login()

# Función para mostrar la pantalla de login
def show_login():
    # Limpiar la ventana principal
    for widget in root.winfo_children():
        widget.destroy()

    # Título del Login
    title_label = tk.Label(root, text="Iniciar Sesión", font=("Arial", 24), bg=color_fondo, fg=color_texto)
    title_label.pack(pady=20)

    # Campos de texto para usuario y contraseña
    username_label = tk.Label(root, text="Usuario", font=("Arial", 14), bg=color_fondo, fg=color_texto)
    username_label.pack(pady=5)
    
    username_entry = ttk.Entry(root, font=("Arial", 14))
    username_entry.pack(pady=10, ipadx=5, ipady=5, fill="x", padx=50)

    password_label = tk.Label(root, text="Contraseña", font=("Arial", 14), bg=color_fondo, fg=color_texto)
    password_label.pack(pady=5)
    
    password_entry = ttk.Entry(root, font=("Arial", 14), show="*")
    password_entry.pack(pady=10, ipadx=5, ipady=5, fill="x", padx=50)

    # Botón de inicio de sesión
    login_button = ttk.Button(root, text="Iniciar Sesión", style="Custom.TButton", command=lambda: login(username_entry.get(), password_entry.get()))
    login_button.pack(pady=20, ipadx=10, ipady=10, fill="x", padx=50)


# Función de autenticación (usuario y contraseña)
def login(username, password):
    # Aquí deberíamos verificar las credenciales con el archivo CSV de usuarios
    if username == "admin" and password == "admin123":
        show_menu()  # Mostrar menú si las credenciales son correctas
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

def mostrar_analisis():
    resumen = resumen_ventas()
    messagebox.showinfo("Análisis de Ventas", resumen)

# Estilo de botones personalizados
style = ttk.Style()
style.configure("Custom.TButton", font=("Arial", 14), padding=10, width=20, background=color_boton)
style.map("Custom.TButton", background=[("active", color_boton_hover)])

# Mostrar la pantalla de login al iniciar
show_login()

# Ejecutar la aplicación
root.mainloop()
