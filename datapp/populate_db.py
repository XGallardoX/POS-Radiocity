import datetime
import random
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, BigInteger, Boolean, DECIMAL, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from decimal import Decimal # ¡Esta línea fue añadida!

# --- Database Connection Details ---
# Use the details from your Django settings
DATABASE_NAME = 'mi_basededatos'
DATABASE_USER = 'mi_usuario'
DATABASE_PASSWORD = 'userRoot11'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '3306'

# SQLAlchemy database URL
# Adjust the driver if needed (e.g., mysqlconnector, etc.)
DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# --- SQLAlchemy Setup ---
engine = create_engine(DATABASE_URL)
Base = declarative_base() # Base class for declarative models

# --- Define SQLAlchemy Models (Mirroring Django Models) ---
# Define models that match your database schema created by Django's ORM.
# Note: SQLAlchemy model names don't have to match Django model names,
# but __tablename__ MUST match the actual table names in your database.
# Django table names are often lowercase with underscores (e.g., appname_modelname).
# You might need to confirm the exact table names if they differ from the model names.
# Based on your query, it seems they are `gestion_factura`, `gestion_empleado`, etc.

class DetalleImpuesto(Base):
    __tablename__ = 'gestion_detalleimpuesto' # Confirm table name

    id = Column(Integer, primary_key=True) # Assuming auto-incrementing primary key
    nombre = Column(String(45), nullable=False)
    impuesto = Column(DECIMAL(5, 3), nullable=False)

class Producto(Base):
    __tablename__ = 'gestion_producto' # Confirm table name

    id = Column(Integer, primary_key=True) # Assuming auto-incrementing primary key
    nombre = Column(String(100), nullable=False)
    precio = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, default=0)
    cantidad_medida = Column(Integer, nullable=False)
    unidad_medida = Column(String(45), nullable=False)

class Proveedor(Base):
    __tablename__ = 'gestion_proveedor' # Confirm table name

    id = Column(Integer, primary_key=True) # Assuming auto-incrementing primary key
    nombre = Column(String(150), nullable=False)
    celular = Column(BigInteger, unique=True, nullable=True) # BigIntegerField in Django maps to BigInteger
    direccion = Column(String(255), nullable=True) # Using String for TextField, adjust length if needed

class Cliente(Base):
    __tablename__ = 'gestion_cliente' # Confirm table name

    id = Column(Integer, primary_key=True) # Assuming auto-incrementing primary key
    nombre = Column(String(100), nullable=True)
    celular = Column(BigInteger, nullable=True)
    email = Column(String(100), nullable=False)

class Empleado(Base):
    __tablename__ = 'gestion_empleado' # Confirm table name

    # Django model has CharField primary_key=True, max_length=20
    id = Column(String(20), primary_key=True) # This will store IDs like "0001", "0002"
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    celular = Column(BigInteger, unique=True, nullable=False)
    estado = Column(Boolean, default=True)

class ConfiguracionFactura(Base):
    __tablename__ = 'gestion_configuracionfactura' # Confirm table name

    id = Column(Integer, primary_key=True) # Assuming auto-incrementing primary key
    prefijo = Column(String(10), nullable=True)

class TipoPago(Base):
    __tablename__ = 'gestion_tipopago' # Confirm table name

    id = Column(Integer, primary_key=True) # Assuming auto-incrementing primary key
    nombre = Column(String(20), nullable=False)

class Factura(Base):
    __tablename__ = 'gestion_factura' # Confirm table name

    # Django model has CharField primary_key=True, max_length=20, custom save logic
    id = Column(String(20), primary_key=True)
    configuracion_id = Column(Integer, ForeignKey('gestion_configuracionfactura.id'), nullable=False)
    fecha_emision = Column(Date, nullable=False)
    hora_emision = Column(Time, nullable=False)
    empleado_id = Column(String(20), ForeignKey('gestion_empleado.id'), nullable=False) # Foreign Key now points to a String ID
    cliente_id = Column(Integer, ForeignKey('gestion_cliente.id'), nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    total = Column(DECIMAL(10, 2), nullable=False)
    tipo_impuesto_id = Column(Integer, ForeignKey('gestion_detalleimpuesto.id'), nullable=False)
    base_gravable = Column(DECIMAL(10, 2), nullable=False)
    tipo_pago_id = Column(Integer, ForeignKey('gestion_tipopago.id'), nullable=False)
    recibido = Column(DECIMAL(10, 2), nullable=False)
    propina = Column(DECIMAL(10, 2), default=0)
    anulado = Column(Boolean, default=False)

    # Relationships (optional, but helpful for ORM)
    configuracion = relationship("ConfiguracionFactura")
    empleado = relationship("Empleado")
    cliente = relationship("Cliente")
    tipo_impuesto = relationship("DetalleImpuesto")
    tipo_pago = relationship("TipoPago")
    detalles = relationship("DetalleFactura", back_populates="factura") # Relation to DetalleFactura

class DetalleFactura(Base):
    __tablename__ = 'gestion_detallefactura' # Confirm table name

    id = Column(Integer, primary_key=True) # Assuming auto-incrementing primary key
    factura_id = Column(String(20), ForeignKey('gestion_factura.id'), nullable=False) # Match Factura ID type
    producto_id = Column(Integer, ForeignKey('gestion_producto.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(DECIMAL(10, 2), nullable=False)

    # Relationships (optional)
    factura = relationship("Factura", back_populates="detalles") # Back reference to Factura
    producto = relationship("Producto")


# --- Faker Setup ---
fake = Faker('es_ES') # Use Spanish locale for more relevant names/addresses

# --- Data Generation Parameters ---
NUM_EMPLEADOS = 10
NUM_CLIENTES = 50
NUM_PRODUCTOS = 30
NUM_PROVEEDORES = 10
NUM_FACTURAS = 200 # Number of invoices to generate
MAX_ITEMS_PER_FACTURA = 5 # Maximum number of detail lines per invoice
DAYS_OF_DATA = 365 * 2 # Generate data for the last 2 years

# --- Helper function to generate custom Factura ID ---
def generate_factura_id(date, counter):
    """Generates a custom invoice ID similar to Django's save method."""
    date_str = date.strftime("%y%m%d")
    return f"{date_str}{counter:04d}"

# --- Main Data Population Logic ---
def populate_database():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("Populating database...")

        # --- Populate Lookup Tables First ---
        print("Populating lookup tables...")
        # DetalleImpuesto
        if session.query(DetalleImpuesto).count() == 0:
            impuestos = [
                DetalleImpuesto(nombre='IVA 0%', impuesto=Decimal('0.000')), # Usando Decimal
                DetalleImpuesto(nombre='IVA 5%', impuesto=Decimal('0.050')), # Usando Decimal
                DetalleImpuesto(nombre='IVA 12%', impuesto=Decimal('0.120')), # Usando Decimal
            ]
            session.add_all(impuestos)
            session.commit()
            print(f"Inserted {len(impuestos)} DetalleImpuesto records.")
        else:
            print("DetalleImpuesto table already has data, skipping.")
        impuesto_ids = [imp.id for imp in session.query(DetalleImpuesto).all()]

        # TipoPago
        if session.query(TipoPago).count() == 0:
            tipos_pago = [
                TipoPago(nombre='Efectivo'),
                TipoPago(nombre='Tarjeta Crédito'),
                TipoPago(nombre='Tarjeta Débito'),
                TipoPago(nombre='Transferencia'),
            ]
            session.add_all(tipos_pago)
            session.commit()
            print(f"Inserted {len(tipos_pago)} TipoPago records.")
        else:
            print("TipoPago table already has data, skipping.")
        tipo_pago_ids = [tp.id for tp in session.query(TipoPago).all()]

        # ConfiguracionFactura
        if session.query(ConfiguracionFactura).count() == 0:
            config = ConfiguracionFactura(prefijo='FAC')
            session.add(config)
            session.commit()
            print("Inserted 1 ConfiguracionFactura record.")
        else:
            print("ConfiguracionFactura table already has data, skipping.")
        configuracion_ids = [cfg.id for cfg in session.query(ConfiguracionFactura).all()]


        # --- Populate Core Entities ---
        print("Populating core entities...")
        # Empleado
        if session.query(Empleado).count() < NUM_EMPLEADOS:
            existing_empleado_count = session.query(Empleado).count()
            empleados_to_add = NUM_EMPLEADOS - existing_empleado_count
            new_empleados = []
            for i in range(empleados_to_add):
                # Generate purely numeric string ID, e.g., "0001", "0002", etc.
                empleado_id_num = (existing_empleado_count + i + 1)
                empleado_id_str = f"{empleado_id_num:04d}" # Formato de 4 dígitos con ceros a la izquierda
                new_empleados.append(Empleado(
                    id=empleado_id_str, # Usar el ID de cadena numérico
                    nombre=fake.first_name(),
                    apellido=fake.last_name(),
                    celular=fake.unique.random_int(min=1000000000, max=9999999999), # 10 digits
                    estado=True
                ))
            session.add_all(new_empleados)
            session.commit()
            print(f"Inserted {len(new_empleados)} Empleado records.")
        else:
            print("Empleado table has enough data, skipping.")
        empleado_ids = [emp.id for emp in session.query(Empleado).all()]
        if not empleado_ids:
            print("ERROR: No empleados found or inserted. Cannot generate invoices.")
            return # Exit if no employees

        # Cliente
        if session.query(Cliente).count() < NUM_CLIENTES:
            clientes_to_add = NUM_CLIENTES - session.query(Cliente).count()
            new_clientes = []
            # Add a default client if needed by your Django model (default=1)
            if session.query(Cliente).filter_by(id=1).count() == 0:
                new_clientes.append(Cliente(id=1, nombre='Cliente General', celular=None, email=''))

            for _ in range(clientes_to_add):
                new_clientes.append(Cliente(
                    nombre=fake.name(),
                    celular=fake.unique.random_int(min=1000000000, max=9999999999),
                    email=fake.unique.email()
                ))
            session.add_all(new_clientes)
            session.commit()
            print(f"Inserted {len(new_clientes)} Cliente records.")
        else:
            print("Cliente table has enough data, skipping.")
        cliente_ids = [cli.id for cli in session.query(Cliente).all()]
        if not cliente_ids:
            print("ERROR: No clientes found or inserted. Cannot generate invoices.")
            return # Exit if no clients

        # Producto
        if session.query(Producto).count() < NUM_PRODUCTOS:
            productos_to_add = NUM_PRODUCTOS - session.query(Producto).count()
            new_productos = []
            for _ in range(productos_to_add):
                new_productos.append(Producto(
                    nombre=fake.word().capitalize() + " " + fake.word(), # Simple product name
                    precio=fake.pydecimal(left_digits=2, right_digits=2, positive=True),
                    stock=fake.random_int(min=10, max=100),
                    cantidad_medida=random.choice([1, 5, 10]),
                    unidad_medida=random.choice(['unidad', 'kg', 'litro', 'paquete'])
                ))
            session.add_all(new_productos)
            session.commit()
            print(f"Inserted {len(new_productos)} Producto records.")
        else:
            print("Producto table has enough data, skipping.")
        producto_ids = [prod.id for prod in session.query(Producto).all()]
        if not producto_ids:
            print("ERROR: No productos found or inserted. Cannot generate invoice details.")
            return # Exit if no products


        # Proveedor (Optional, as not used in the main query)
        if session.query(Proveedor).count() < NUM_PROVEEDORES:
            proveedores_to_add = NUM_PROVEEDORES - session.query(Proveedor).count()
            new_proveedores = []
            for _ in range(proveedores_to_add):
                new_proveedores.append(Proveedor(
                    nombre=fake.company(),
                    celular=fake.unique.random_int(min=1000000000, max=9999999999),
                    direccion=fake.address()
                ))
            session.add_all(new_proveedores)
            session.commit()
            print(f"Inserted {len(new_proveedores)} Proveedor records.")
        else:
            print("Proveedor table has enough data, skipping.")


        # --- Populate Facturas and Detalles ---
        print("Populating Facturas and DetalleFacturas...")
        existing_factura_count = session.query(Factura).count()
        facturas_to_add = NUM_FACTURAS - existing_factura_count
        if facturas_to_add > 0:
            # Get a list of dates within the last X days
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=DAYS_OF_DATA)
            date_range = [start_date + datetime.timedelta(n) for n in range(DAYS_OF_DATA)]

            factura_counter_by_date = {} # To help generate unique IDs per day

            for i in range(facturas_to_add):
                # Randomly pick a date within the range
                factura_date = random.choice(date_range)

                # Initialize counter for this date if not exists
                if factura_date not in factura_counter_by_date:
                    # Find existing invoices for this date to continue the counter
                    existing_on_date = session.query(Factura).filter(Factura.fecha_emision == factura_date).count()
                    factura_counter_by_date[factura_date] = existing_on_date

                factura_counter_by_date[factura_date] += 1
                factura_id = generate_factura_id(factura_date, factura_counter_by_date[factura_date])

                # Generate random data for the invoice
                fake_hora = datetime.time(random.randint(8, 20), random.randint(0, 59), random.randint(0, 59))
                fake_empleado_id = random.choice(empleado_ids)
                fake_cliente_id = random.choice(cliente_ids)
                fake_configuracion_id = random.choice(configuracion_ids)
                fake_tipo_impuesto_id = random.choice(impuesto_ids)
                fake_tipo_pago_id = random.choice(tipo_pago_ids)
                fake_anulado = fake.boolean(chance_of_getting_true=5) # 5% chance of being cancelled

                # Create the Factura object
                nueva_factura = Factura(
                    id=factura_id,
                    configuracion_id=fake_configuracion_id,
                    fecha_emision=factura_date,
                    hora_emision=fake_hora,
                    empleado_id=fake_empleado_id,
                    cliente_id=fake_cliente_id,
                    tipo_impuesto_id=fake_tipo_impuesto_id,
                    tipo_pago_id=fake_tipo_pago_id,
                    anulado=fake_anulado,
                    propina=fake.pydecimal(left_digits=1, right_digits=2, positive=True) if fake.boolean(chance_of_getting_true=20) else Decimal('0.00') # Usando Decimal
                )

                # --- Explicitly disable autoflush before operations that might trigger it ---
                session.autoflush = False

                try:
                    # Add the Factura object to the session
                    session.add(nueva_factura)

                    # Generate DetalleFactura records for this invoice
                    num_detalles = random.randint(1, MAX_ITEMS_PER_FACTURA)
                    subtotal_factura = Decimal('0.00')
                    base_gravable_factura = Decimal('0.00')

                    for _ in range(num_detalles):
                        fake_producto_id = random.choice(producto_ids)
                        # Fetch the product price to use as base for unit price
                        producto = session.query(Producto).filter_by(id=fake_producto_id).first()
                        if producto:
                            fake_precio_unitario = producto.precio
                            fake_cantidad = random.randint(1, 10)
                            line_total = fake_cantidad * fake_precio_unitario

                            base_gravable_factura += line_total
                            subtotal_factura += line_total

                            nuevo_detalle = DetalleFactura(
                                factura=nueva_factura, # Link to the parent Factura object
                                producto_id=fake_producto_id,
                                cantidad=fake_cantidad,
                                precio_unitario=fake_precio_unitario
                            )
                            session.add(nuevo_detalle)

                    # Calculate total (simple calculation: subtotal + tax + tip)
                    impuesto_rate = session.query(DetalleImpuesto.impuesto).filter_by(id=fake_tipo_impuesto_id).scalar()
                    tax_amount = base_gravable_factura * (impuesto_rate or Decimal('0.00')) # Usando Decimal
                    total_factura = subtotal_factura + tax_amount + nueva_factura.propina

                    # Update Factura totals AFTER generating details and calculating
                    nueva_factura.subtotal = subtotal_factura.quantize(Decimal('0.01'))
                    nueva_factura.base_gravable = base_gravable_factura.quantize(Decimal('0.01'))
                    nueva_factura.total = total_factura.quantize(Decimal('0.01'))
                    nueva_factura.recibido = total_factura.quantize(Decimal('0.01')) # Assume received equals total for simplicity

                finally:
                    # --- Re-enable autoflush ---
                    session.autoflush = True

                # Commit in batches to avoid large transactions
                if (i + 1) % 50 == 0: # Commit every 50 invoices
                    session.commit()
                    print(f"Inserted {i + 1} invoices so far...")

            # Commit any remaining records
            session.commit()
            print(f"Finished inserting {facturas_to_add} new Factura and DetalleFactura records.")
        else:
            print("Factura table has enough data, skipping.")


    except Exception as e:
        session.rollback() # Roll back the transaction on error
        print(f"An error occurred: {e}")

    finally:
        session.close()
        print("Database population script finished.")

# --- Function to Delete All Data (using TRUNCATE TABLE) ---
def delete_all_data_truncate():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        print("Truncating all existing data...")
        # Temporarily disable foreign key checks for TRUNCATE in MySQL
        session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

        # Truncate tables in reverse order of dependency for safety,
        # though order matters less with FK checks off for TRUNCATE.
        # The order here ensures that if FK checks fail to disable,
        # it still attempts to delete children first.
        session.execute(text(f"TRUNCATE TABLE {DetalleFactura.__tablename__};"))
        session.execute(text(f"TRUNCATE TABLE {Factura.__tablename__};"))

        session.execute(text(f"TRUNCATE TABLE {Cliente.__tablename__};"))
        session.execute(text(f"TRUNCATE TABLE {Empleado.__tablename__};"))
        session.execute(text(f"TRUNCATE TABLE {Producto.__tablename__};"))
        session.execute(text(f"TRUNCATE TABLE {Proveedor.__tablename__};"))

        session.execute(text(f"TRUNCATE TABLE {DetalleImpuesto.__tablename__};"))
        session.execute(text(f"TRUNCATE TABLE {TipoPago.__tablename__};"))
        session.execute(text(f"TRUNCATE TABLE {ConfiguracionFactura.__tablename__};"))

        # Re-enable foreign key checks
        session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        session.commit()
        print("All data truncated successfully and auto-increments reset.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred during data truncation: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Opcional: Puedes descomentar la siguiente línea para eliminar todos los datos
    # antes de poblar la base de datos cada vez que ejecutes el script.
    delete_all_data_truncate()

    populate_database()