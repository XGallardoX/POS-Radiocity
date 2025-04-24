import sys
import os
import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Asegurar que se pueda importar desde la carpeta backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from factura import generar_factura
from inventario import agregar_producto, retirar_producto, actualizar_producto, leer_inventario
from usuarios import login as verificar_login
from compra import registrar_venta
from analisis import resumen_general
from analisis import generar_pdf_analisis
from ventas import cargar_datos_ventas
from ventas import resumen_ventas

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
    
        total = sum(item['subtotal'] for item in carrito)
    
        # Registrar venta
        id_venta = registrar_venta(carrito, total)

        # Aquí puedes luego llamar a generar_factura(carrito, total) si quieres generar PDF
        messagebox.showinfo("Venta registrada", f"Venta {id_venta} finalizada.")
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

def grafico_productos_mas_vendidos():
    import matplotlib.pyplot as plt
    from backend.ventas import resumen_ventas

    resumen = resumen_ventas()
    productos = resumen['Productos Más Vendidos']
    
    # Crear el gráfico
    productos = dict(sorted(productos.items(), key=lambda item: item[1], reverse=True))
    
    plt.figure(figsize=(10, 6))
    plt.bar(productos.keys(), productos.values(), color='lightblue')
    plt.title('Productos Más Vendidos')
    plt.xlabel('Producto')
    plt.ylabel('Cantidad Vendida')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def grafico_ingresos_por_dia():
    import matplotlib.pyplot as plt
    from backend.ventas import resumen_ventas

    resumen = resumen_ventas()
    ingresos = resumen['Ingresos por Día']
    
    # Crear el gráfico
    fechas = list(ingresos.keys())
    ingresos_dia = list(ingresos.values())
    
    plt.figure(figsize=(10, 6))
    plt.plot(fechas, ingresos_dia, marker='o', color='green')
    plt.title('Ingresos por Día')
    plt.xlabel('Fecha')
    plt.ylabel('Ingreso ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def grafico_promedio_diario():
    import matplotlib.pyplot as plt
    from backend.ventas import resumen_ventas

    resumen = resumen_ventas()
    promedio = resumen['Promedio Diario ($)']
    
    # Crear el gráfico
    plt.figure(figsize=(5, 5))
    plt.bar(['Promedio Diario'], [promedio], color='orange')
    plt.title('Promedio Diario de Ventas')
    plt.ylabel('Promedio ($)')
    plt.tight_layout()
    plt.show()


# Función para mostrar análisis de ventas
def mostrar_analisis():
    for widget in root.winfo_children():
        widget.destroy()

    df = cargar_datos_ventas()
    if df is None:
        return messagebox.showerror("Error", "No hay datos disponibles para análisis.")

    tk.Label(root, text="Análisis de Ventas", font=("Arial", 20), bg=color_fondo, fg=color_texto).pack(pady=10)

    resumen = resumen_ventas()

    text_widget = tk.Text(root, height=15, width=70, bg=color_fondo, fg=color_texto, font=("Courier", 11), borderwidth=0)
    text_widget.insert(tk.END, resumen)
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(pady=10)

    # Botón para generar el PDF de análisis
    ttk.Button(root, text="Generar PDF de Análisis", style="Custom.TButton", command=generar_pdf_analisis).pack(pady=5)

    ttk.Button(root, text="Ver Gráficas", style="Custom.TButton", command=mostrar_graficas).pack(pady=5)
    ttk.Button(root, text="Volver al Menú", style="Custom.TButton", command=show_menu).pack(pady=5)


# Variable global para manejar la gráfica actual
indice_grafica = 0

# Función de mostrar gráficas
def mostrar_graficas():
    global indice_grafica
    
    for widget in root.winfo_children():
        widget.destroy()

    df = cargar_datos_ventas()
    if df is None:
        return messagebox.showerror("Error", "No hay datos disponibles para análisis.")
    
    tk.Label(root, text="Gráficas de Ventas", font=("Arial", 20), bg=color_fondo, fg=color_texto).pack(pady=10)

    # Frame para las gráficas
    frame_graficas = tk.Frame(root, bg=color_fondo)
    frame_graficas.pack(fill='both', expand=True)

    # Crear la figura para las gráficas
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))

    if indice_grafica == 0:
        # Gráfico 1: Ingresos por producto
        ingresos = df.groupby('nombre')['subtotal'].sum().sort_values(ascending=False)
        axs.bar(ingresos.index, ingresos.values)
        axs.set_title("Ingresos por Producto")
        axs.tick_params(axis='x', rotation=45)

    elif indice_grafica == 1:
        # Gráfico 2: Unidades vendidas por producto
        cantidades = df.groupby('nombre')['cantidad'].sum().sort_values(ascending=False)
        axs.bar(cantidades.index, cantidades.values, color='orange')
        axs.set_title("Unidades Vendidas por Producto")
        axs.tick_params(axis='x', rotation=45)

    elif indice_grafica == 2:
        # Gráfico 3: Productos más vendidos
        productos_ventas = df.groupby('nombre')['cantidad'].sum().sort_values(ascending=False)
        axs.bar(productos_ventas.index, productos_ventas.values)
        axs.set_title("Productos Más Vendidos")
        axs.tick_params(axis='x', rotation=45)

    elif indice_grafica == 3:
        # Gráfico 4: Ingresos por día
        ingresos_dia = df.groupby(df['fecha'].dt.date)['subtotal'].sum()
        axs.plot(ingresos_dia.index, ingresos_dia.values, marker='o', color='green')
        axs.set_title("Ingresos por Día")
        axs.set_xlabel("Fecha")
        axs.set_ylabel("Ingreso ($)")

    elif indice_grafica == 4:
        # Gráfico 5: Promedio Diario
        total_ventas = df["subtotal"].sum()
        promedio_diario = df.groupby(df["fecha"].dt.date)["subtotal"].sum().mean()
        axs.pie([promedio_diario, total_ventas - promedio_diario], 
                labels=["Promedio Diario", "Otros"], autopct='%1.1f%%', colors=['yellow', 'lightgray'])
        axs.set_title("Distribución del Promedio Diario")

    fig.tight_layout()

    # Canvas para la gráfica
    canvas = FigureCanvasTkAgg(fig, master=frame_graficas)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # Botón "Anterior" para regresar a la gráfica anterior
    if indice_grafica > 0:
        ttk.Button(root, text="Anterior", style="Custom.TButton", command=mostrar_anterior_grafica).pack(pady=10)
    
    # Botón "Siguiente" para avanzar a la siguiente gráfica
    if indice_grafica < 4:
        ttk.Button(root, text="Siguiente", style="Custom.TButton", command=mostrar_siguiente_grafica).pack(pady=10)
    
    # Botón "Volver al Análisis"
    ttk.Button(root, text="Volver al Análisis", style="Custom.TButton", command=mostrar_analisis).pack(pady=10)

# Función para manejar el clic en "Siguiente"
def mostrar_siguiente_grafica():
    global indice_grafica
    indice_grafica += 1
    mostrar_graficas()  # Llamamos a la función de gráficas nuevamente para mostrar la siguiente gráfica

# Función para manejar el clic en "Anterior"
def mostrar_anterior_grafica():
    global indice_grafica
    indice_grafica -= 1
    mostrar_graficas()  # Llamamos a la función de gráficas nuevamente para mostrar la gráfica anterior





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

def cerrar_aplicacion():
    root.quit()  # Termina el bucle principal de Tkinter

# Agregar este código antes de entrar en el bucle principal
root.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

# Estilo personalizado
style = ttk.Style()
style.configure("Custom.TButton", font=("Arial", 14), padding=10, width=20)
style.map("Custom.TButton", background=[("active", color_boton_hover)])

# Iniciar con pantalla de login
show_login()

# Ejecutar app
root.mainloop()
