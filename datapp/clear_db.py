import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- Database Connection Details ---
# Asegúrate de que estos detalles coincidan exactamente con los de tu script de población
# y con la configuración de tu Django.
DATABASE_NAME = 'mi_basededatos'
DATABASE_USER = 'mi_usuario'
DATABASE_PASSWORD = 'userRoot11'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '3306'

# SQLAlchemy database URL
# Ajusta el driver si es necesario (e.g., mysql+mysqlconnector, mysql+pymysql)
DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Lista de nombres de tablas de tu aplicación Django que quieres limpiar.
# EL ORDEN DE LAS TABLAS NO IMPORTA TANTO CON FOREIGN_KEY_CHECKS = 0,
# pero se recomienda empezar por las tablas "hijas" (con FKs) para una buena práctica.
# Asegúrate de incluir TODAS las tablas de tu aplicación que contienen datos de prueba.
APP_TABLES = [
    'gestion_detallefactura',
    'gestion_factura',
    'gestion_detallecompra', # Incluir si gestion_compra existe y tiene detalles
    'gestion_compra',        # Incluir si gestion_compra existe
    'gestion_cliente',
    'gestion_empleado',
    'gestion_producto',
    'gestion_proveedor',
    'gestion_detalleimpuesto',
    'gestion_tipopago',
    'gestion_configuracionfactura',
    # Si deseas borrar también los datos de autenticación de Django u otros modelos:
    # 'auth_user_user_permissions',
    # 'auth_user_groups',
    # 'auth_user',
    # 'auth_group_permissions',
    # 'auth_group',
    # 'django_admin_log',
    # 'django_session',
    # NOTA: Evita truncar 'django_migrations' o 'django_content_type' a menos que sepas exactamente lo que haces,
    # ya que esto puede romper tu historial de migraciones de Django.
]

def clear_all_app_data():
    """
    Borra todos los datos de las tablas de la aplicación listadas en APP_TABLES
    utilizando TRUNCATE TABLE, deshabilitando temporalmente las comprobaciones
    de claves foráneas.
    """
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print(f"Conectando a la base de datos: {DATABASE_NAME} en {DATABASE_HOST}:{DATABASE_PORT}")
        print("Iniciando proceso de limpieza de datos...")

        # Deshabilitar temporalmente las comprobaciones de claves foráneas en MySQL
        print("Deshabilitando comprobaciones de claves foráneas...")
        session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        session.commit() # Commit para asegurar que el SET se aplica

        for table_name in APP_TABLES:
            try:
                print(f"Truncando tabla: {table_name}...")
                session.execute(text(f"TRUNCATE TABLE {table_name};"))
            except Exception as e:
                print(f"Error al truncar la tabla {table_name}: {e}")
                print("Continuando con la siguiente tabla, pero revisa este error.")
        
        session.commit() # Confirmar todas las operaciones TRUNCATE

        # Volver a habilitar las comprobaciones de claves foráneas
        print("Habilitando comprobaciones de claves foráneas...")
        session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        session.commit() # Commit para asegurar que el SET se aplica

        print("¡Todos los datos de la aplicación han sido truncados exitosamente y los auto-incrementos reseteados!")

    except Exception as e:
        session.rollback() # Hacer rollback en caso de cualquier error antes de habilitar FKs
        print(f"\n¡Ocurrió un error crítico durante la limpieza de la base de datos: {e}")
        print("Asegúrate de que los detalles de conexión a la base de datos son correctos.")
        print("Si el error persiste, es posible que necesites revisar los permisos del usuario o el estado de la base de datos.")
        
        # Intentar re-habilitar FK checks incluso si hubo un error durante TRUNCATE
        try:
            print("Intentando re-habilitar comprobaciones de claves foráneas (SET FOREIGN_KEY_CHECKS = 1)...")
            session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            session.commit()
            print("Comprobaciones de claves foráneas habilitadas.")
        except Exception as re_e:
            print(f"Error al re-habilitar las comprobaciones de claves foráneas: {re_e}")
            print("¡ADVERTENCIA: Las comprobaciones de claves foráneas podrían estar deshabilitadas en tu DB!")
            print("Por favor, conéctate manualmente y ejecuta 'SET FOREIGN_KEY_CHECKS = 1;'")

        sys.exit(1) # Salir con código de error

    finally:
        session.close()
        print("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    clear_all_app_data()