import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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

    btn_logout = ttk.Button(root, text="Cerrar Sesión", style="Custom.TButton", command=logout)
    btn_logout.pack(pady=10, ipadx=10, ipady=10, fill="x", padx=50)

# Funciones de acción para los botones
def open_inventario():
    # Llamar a la interfaz de inventario
    messagebox.showinfo("Inventario", "Abrir control de inventario...")

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

# Estilo de botones personalizados
style = ttk.Style()
style.configure("Custom.TButton", font=("Arial", 14), padding=10, width=20, background=color_boton)
style.map("Custom.TButton", background=[("active", color_boton_hover)])

# Mostrar la pantalla de login al iniciar
show_login()

# Ejecutar la aplicación
root.mainloop()
