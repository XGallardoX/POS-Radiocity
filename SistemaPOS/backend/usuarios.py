import pandas as pd

# Función para realizar login
def login(usuario, contrasena):
    try:
        df_usuarios = pd.read_csv('data/usuarios.csv')  # Archivo CSV con usuarios y contraseñas
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

# Ejemplo de uso:
# Suponiendo que el archivo 'usuarios.csv' contiene las columnas 'usuario', 'contrasena' y 'rol'
#print(login('admin', 'admin123'))  # Debería devolver 'ADMIN' si es correcto
