import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USUARIOS_CSV = os.path.join(BASE_DIR, 'data', 'usuarios.csv')

# Función para realizar login
def login(usuario, contrasena):
    try:
        df_usuarios = pd.read_csv(USUARIOS_CSV)  # Archivo CSV con usuarios y contraseñas
    except FileNotFoundError:
        print("No se encontró el archivo de usuarios.")
        return False
    
    usuario_data = df_usuarios[df_usuarios['usuario'] == usuario]
    if usuario_data.empty:
        print("Usuario no encontrado.")
        return False
    
    if usuario_data['contrasena'].values[0] == contrasena:
        return usuario_data['rol'].values[0]
    else:
        print("Contraseña incorrecta.")
        return False
