import datetime
import pandas as pd
import streamlit as st
import altair as alt
from sqlalchemy import create_engine

# --- Database Connection Details ---
# Asegúrate de que estos datos son correctos para tu base de datos
user = "mi_usuario"
password = "userRoot11"
host = "localhost"
port = "3306"
db = "mi_basededatos"

# Crear motor de conexión
try:
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}")
except Exception as e:
    st.error(f"Error al crear el motor de conexión a la base de datos: {e}")
    st.stop() # Detiene la ejecución si hay un error

# Leer datos con SQL
query = """
SELECT
    f.fecha_emision,
    f.hora_emision, -- Added hora_emision to the select statement
    e.id AS empleado_id,
    CONCAT(e.nombre, ' ', e.apellido) AS empleado_nombre,
    p.id AS producto_id,
    p.nombre AS producto_nombre,
    SUM(df.cantidad) AS cantidad_vendida,
    SUM(df.cantidad * df.precio_unitario) AS total_venta
FROM
    gestion_factura f
JOIN
    gestion_empleado e ON f.empleado_id = e.id
JOIN
    gestion_detallefactura df ON f.id = df.factura_id
JOIN
    gestion_producto p ON df.producto_id = p.id
WHERE
    f.anulado = FALSE
GROUP BY
    f.fecha_emision, f.hora_emision, e.id, p.id
ORDER BY
    f.fecha_emision DESC, total_venta DESC;
"""

# Cargar datos
try:
    df = pd.read_sql(query, engine)
except Exception as e:
    st.error(f"Error al conectar a la base de datos o ejecutar la consulta: {e}")
    st.stop() # Detiene la ejecución si hay un error en la base de datos

# Convertir fecha_emision a datetime
df['fecha_emision'] = pd.to_datetime(df['fecha_emision']).dt.date # Keep only the date part

# Handle hora_emision column: convert to string 'HH:MM:SS' if it's timedelta
# This is a more robust way to handle different ways read_sql might return TIME data
if pd.api.types.is_timedelta64_dtype(df['hora_emision']):
    # Convert timedelta to total seconds, then format as HH:MM:SS
    df['hora_emision_str'] = df['hora_emision'].apply(
        lambda td: (datetime.timedelta(seconds=td.total_seconds())).total_seconds()
    ).apply(
        lambda s: f"{int(s // 3600):02d}:{(int(s % 3600 // 60)):02d}:{(int(s % 60)):02d}"
    )
elif pd.api.types.is_object_dtype(df['hora_emision']):
     # If it's object dtype, assume it might be time objects or strings already
     # Attempt to convert to string 'HH:MM:SS'
     df['hora_emision_str'] = df['hora_emision'].astype(str).apply(lambda t: str(t).split('.')[0]) # Handle potential microseconds
else:
    # If it's neither timedelta nor object, assume it's already a time-like series
    # Convert to string 'HH:MM:SS'
    df['hora_emision_str'] = df['hora_emision'].astype(str).apply(lambda t: str(t).split('.')[0]) # Handle potential microseconds


# Create a new datetime column combining date and time strings
# Combine date string and time string, then convert to datetime
df['fecha_hora_emision'] = pd.to_datetime(
    df['fecha_emision'].astype(str) + ' ' + df['hora_emision_str']
)


# Extract date and time components from the new combined column
df['año'] = df['fecha_hora_emision'].dt.year
df['mes_num'] = df['fecha_hora_emision'].dt.month # Número del mes para ordenar
df['mes'] = df['fecha_hora_emision'].dt.month_name() # Nombre del mes
df['dia'] = df['fecha_hora_emision'].dt.day # Número del día
df['dia_semana'] = df['fecha_hora_emision'].dt.day_name() # Nombre del día de la semana
df['hora_emision_time'] = df['fecha_hora_emision'].dt.time # Extract time object for filtering


# Orden para los días de la semana (en inglés, ya que .dt.day_name() devuelve nombres en inglés por defecto)
orden_dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# Orden para los meses (en inglés)
orden_meses = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


# --- Streamlit App Layout ---
st.title("Datos de ventas")

# --- Sidebar for Filtering ---
st.sidebar.header("Filtro de Fecha")

# Radio button para seleccionar tipo de filtro de fecha
filtro_tipo = st.sidebar.radio(
    "Selecciona el tipo de filtro de fecha:",
    ('Fecha actual', 'Fecha específica')
)

# Variables para almacenar los criterios de filtro de fecha
año_filtro = None
mes_filtro = None
dia_rango_filtro = None # Usaremos un rango para el día
fecha_seleccionada_display = None # Para mostrar la fecha o el rango seleccionado

if filtro_tipo == 'Fecha actual':
    # Si se selecciona "Fecha actual", usar la fecha de hoy
    fecha_actual = datetime.date.today()
    # Para el filtro global, usaremos la fecha exacta
    año_filtro = fecha_actual.year
    mes_filtro = fecha_actual.strftime('%B') # Nombre del mes actual
    dia_rango_filtro = (fecha_actual.day, fecha_actual.day) # Rango de un solo día
    fecha_seleccionada_display = fecha_actual.strftime('%Y-%m-%d')
    st.sidebar.write(f"Mostrando datos para: {fecha_seleccionada_display}")

elif filtro_tipo == 'Fecha específica':
    # Si se selecciona "Fecha específica", mostrar selectboxes y slider

    # Obtener años disponibles de los datos y añadir "Todos"
    años_disponibles = sorted(df['año'].unique())
    opciones_año = ['Todos'] + años_disponibles

    # Selectbox para el año
    año_seleccionado_sidebar = st.sidebar.selectbox(
        "Selecciona el Año:",
        opciones_año,
        key='sidebar_año'
    )

    if año_seleccionado_sidebar != 'Todos':
        año_filtro = año_seleccionado_sidebar
        # Filtrar datos por el año seleccionado para obtener meses disponibles
        df_filtrado_año_sidebar = df[df['año'] == año_filtro]
        meses_disponibles_sidebar = sorted(df_filtrado_año_sidebar['mes'].unique(), key=orden_meses.index)
        opciones_mes = ['Todos'] + meses_disponibles_sidebar

        # Selectbox para el mes
        mes_seleccionado_sidebar = st.sidebar.selectbox(
            "Selecciona el Mes:",
            opciones_mes,
            key='sidebar_mes'
        )

        if mes_seleccionado_sidebar != 'Todos':
            mes_filtro = mes_seleccionado_sidebar
            # Filtrar datos por año y mes para obtener días disponibles
            df_filtrado_mes_sidebar = df_filtrado_año_sidebar[df_filtrado_año_sidebar['mes'] == mes_filtro]
            dias_disponibles_sidebar = sorted(df_filtrado_mes_sidebar['dia'].unique())

            if dias_disponibles_sidebar:
                min_dia_disponible = min(dias_disponibles_sidebar)
                max_dia_disponible = max(dias_disponibles_sidebar)

                # --- Slider para el Rango de Días ---
                dia_rango_seleccionado_sidebar = st.sidebar.slider(
                    "Selecciona el Rango de Días:",
                    min_value=min_dia_disponible,
                    max_value=max_dia_disponible,
                    value=(min_dia_disponible, max_dia_disponible), # Default to the full range
                    step=1,
                    key='sidebar_dia_range'
                )

                # Almacenar el rango de días seleccionado
                dia_rango_filtro = dia_rango_seleccionado_sidebar

                # Actualizar mensaje de display
                if dia_rango_filtro[0] == min_dia_disponible and dia_rango_filtro[1] == max_dia_disponible:
                     fecha_seleccionada_display = f"{mes_filtro}, {año_filtro} (Todos los días)"
                else:
                     # Construir el rango de fecha seleccionado para mostrar
                     try:
                          mes_numero_seleccionado = orden_meses.index(mes_seleccionado_sidebar) + 1
                          fecha_inicio_display = f"{año_filtro}-{mes_numero_seleccionado:02d}-{dia_rango_filtro[0]:02d}"
                          fecha_fin_display = f"{año_filtro}-{mes_numero_seleccionado:02d}-{dia_rango_filtro[1]:02d}"
                          fecha_seleccionada_display = f"Rango: {fecha_inicio_display} a {fecha_fin_display}"
                     except ValueError:
                          fecha_seleccionada_display = "Fecha inválida"
                          st.sidebar.error("Fecha seleccionada inválida.")
                          dia_rango_filtro = None # Reset if date is invalid


            else:
                st.sidebar.warning("No hay días disponibles para el mes y año seleccionados.")
                fecha_seleccionada_display = f"{mes_filtro}, {año_filtro} (Sin días disponibles)"
                dia_rango_filtro = None # Reset if no days available
        else:
             fecha_seleccionada_display = f"Año {año_filtro}"
             mes_filtro = None # Reset mes filter if month is 'Todos'
             dia_rango_filtro = None # Reset dia filter if month is 'Todos'
    else:
         fecha_seleccionada_display = "Todos los años"
         año_filtro = None # Set año_filtro to None if 'Todos' is selected
         mes_filtro = None # Reset mes filter if year is 'Todos'
         dia_rango_filtro = None # Reset dia filter if year is 'Todos'

    st.sidebar.write(f"Mostrando datos para: {fecha_seleccionada_display}")


# --- Sidebar for Time Filtering ---
st.sidebar.header("Filtro de Hora")

# Checkbox para habilitar/deshabilitar el filtro de hora
aplicar_filtro_hora = st.sidebar.checkbox("Aplicar filtro de hora", value=False, key='sidebar_apply_hour_filter')

# Variables para almacenar el rango de horas seleccionado (valores por defecto)
hora_inicio = 0
hora_fin = 23
time_inicio = datetime.time(hora_inicio, 0, 0)
time_fin = datetime.time(hora_fin, 59, 59)

if aplicar_filtro_hora:
    # Slider para seleccionar el rango de horas (de 0 a 23)
    # REMOVED: format="%H:00" to avoid sprintf error
    hora_inicio, hora_fin = st.sidebar.slider(
        "Selecciona el rango de horas:",
        min_value=0,
        max_value=23,
        value=(0, 23), # Default to the full 24-hour range
        step=1,
        key='sidebar_hour_range'
    )

    # Convertir las horas seleccionadas a objetos time para comparar
    time_inicio = datetime.time(hora_inicio, 0, 0)
    time_fin = datetime.time(hora_fin, 59, 59) # Incluir hasta el final del minuto 59 de la hora fin

    st.sidebar.write(f"Filtrando entre {time_inicio.strftime('%H:%M')} y {time_fin.strftime('%H:%M')}")
else:
     st.sidebar.write("Filtro de hora desactivado (mostrando todas las horas).")

# --- Removed Sidebar option to display filtered data ---
# mostrar_dataframe_filtrado = st.sidebar.checkbox("Mostrar datos filtrados", value=False, key='sidebar_display_filtered_df')


# --- Filtrar el DataFrame principal basado en las selecciones de la sidebar ---
# Filter using the combined 'fecha_hora_emision' column for date and time
df_filtrado_global = df.copy() # Empezar con una copia del DataFrame completo

# Aplicar filtro de fecha primero using the date part of the combined column
if filtro_tipo == 'Fecha actual':
    fecha_actual = datetime.date.today()
    df_filtrado_global = df_filtrado_global[df_filtrado_global['fecha_hora_emision'].dt.date == fecha_actual]

elif filtro_tipo == 'Fecha específica':
    # Apply filters based on sidebar selections using components from the combined column
    if año_filtro is not None: # Filtra si se seleccionó un año específico
        df_filtrado_global = df_filtrado_global[df_filtrado_global['fecha_hora_emision'].dt.year == año_filtro]

    if mes_filtro is not None: # Filtra si se seleccionó un mes específico
        df_filtrado_global = df_filtrado_global[df_filtrado_global['fecha_hora_emision'].dt.month_name() == mes_filtro]

    if dia_rango_filtro is not None: # Filtra si se seleccionó un rango de días
         min_dia, max_dia = dia_rango_filtro
         df_filtrado_global = df_filtrado_global[(df_filtrado_global['fecha_hora_emision'].dt.day >= min_dia) & (df_filtrado_global['fecha_hora_emision'].dt.day <= max_dia)]

# Aplicar filtro de hora si está habilitado using the time part of the combined column
if aplicar_filtro_hora and not df_filtrado_global.empty:
     df_filtrado_global = df_filtrado_global[
         (df_filtrado_global['fecha_hora_emision'].dt.time >= time_inicio) &
         (df_filtrado_global['fecha_hora_emision'].dt.time <= time_fin)
     ]

# --- Removed Display filtered DataFrame if checkbox is checked ---
# if mostrar_dataframe_filtrado:
#     st.subheader("Datos Filtrados (para depuración)")
#     st.dataframe(df_filtrado_global)
#     st.write(f"Número de filas después del filtro: {len(df_filtrado_global)}")


# --- Gráfico de Línea de Ventas a lo largo del Tiempo (Mostrar solo con filtro de rango de días > 1) ---
# Mostrar este gráfico solo si se seleccionó un rango de días > 1 en la fecha específica
if filtro_tipo == 'Fecha específica' and año_filtro is not None and mes_filtro is not None and dia_rango_filtro is not None and dia_rango_filtro[0] != dia_rango_filtro[1]:
    st.subheader("Ventas a lo largo del tiempo (por fecha)")

    # Agrupar por fecha de emisión y sumar las ventas para el gráfico de línea
    # Use the date part of the combined column for grouping
    ventas_por_fecha = df_filtrado_global.groupby(df_filtrado_global['fecha_hora_emision'].dt.date)['total_venta'].sum().reset_index()
    # Rename the date column for Altair plotting
    ventas_por_fecha.rename(columns={'fecha_hora_emision': 'fecha'}, inplace=True)


    # Crear gráfico de línea
    if not ventas_por_fecha.empty:
        line_chart_ventas = alt.Chart(ventas_por_fecha).mark_line().encode(
            x=alt.X('fecha:T', title='Fecha'), # Usar tipo temporal para la fecha
            y=alt.Y('total_venta:Q', title='Total Vendido'),
            tooltip=[alt.Tooltip('fecha', title='Fecha', format='%Y-%m-%d'), alt.Tooltip('total_venta', format=',.2f')]
        ).properties(
            title=f'Ventas Diarias entre {time_inicio.strftime("%H:%M")} y {time_fin.strftime("%H:%M")}' if aplicar_filtro_hora else 'Ventas Diarias (Todas las horas)',
            width=700,
            height=400
        ).interactive()

        st.altair_chart(line_chart_ventas)
    else:
        st.info("No hay datos de ventas para el rango de fechas y horas seleccionado para mostrar el gráfico de línea.")


# --- Mostrar Ventas Totales para el período y hora seleccionados ---
st.subheader("Ventas Totales")
if not df_filtrado_global.empty:
    total_ventas_periodo = df_filtrado_global['total_venta'].sum()
    st.metric(label="Total Vendido", value=f"${total_ventas_periodo:,.2f}")
else:
    st.info("No hay datos de ventas para el período y hora seleccionados.")


# --- Apartado de Ventas por Empleado para el período y hora seleccionados ---
st.subheader("Ventas por Empleado")

# Agrupar por empleado usando el DataFrame filtrado global
if not df_filtrado_global.empty:
    ventas_por_empleado = df_filtrado_global.groupby('empleado_nombre')['total_venta'].sum().reset_index()

    # Crear gráfico de barras para empleados
    barras_empleados = alt.Chart(ventas_por_empleado).mark_bar().encode(
        x=alt.X('total_venta:Q', title='Total Vendido'),
        y=alt.Y('empleado_nombre:N', title='Empleado', sort='-x'),
        tooltip=['empleado_nombre', alt.Tooltip('total_venta', format=',.2f')] # Formato para moneda
    ).properties(
        title=f'Ventas por Empleado ({time_inicio.strftime("%H:%M")} - {time_fin.strftime("%H:%M")})' if aplicar_filtro_hora else 'Ventas por Empleado (Todas las horas)',
        width=700,
        height=400
    ).interactive() # Permite zoom y paneo

    st.altair_chart(barras_empleados)
else:
    st.info("No hay datos de ventas por empleado para el período y hora seleccionados.")


# --- Apartado de Ventas por Producto para el período y hora seleccionados ---
st.subheader("Ventas por Producto")
# Agrupar por producto usando el DataFrame filtrado global
if not df_filtrado_global.empty:
    ventas_por_producto = df_filtrado_global.groupby('producto_nombre')['total_venta'].sum().reset_index()
    barras_productos = alt.Chart(ventas_por_producto).mark_bar().encode(
        x=alt.X('total_venta:Q', title='Total Vendido'),
        y=alt.Y('producto_nombre:N', title='Producto', sort='-x'),
        tooltip=['producto_nombre', alt.Tooltip('total_venta', format=',.2f')] # Formato para moneda
    ).properties(
        title=f'Ventas por Producto ({time_inicio.strftime("%H:%M")} - {time_fin.strftime("%H:%M")})' if aplicar_filtro_hora else 'Ventas por Producto (Todas las horas)',
        width=700,
        height=400
    ).interactive() # Permite zoom y paneo

    st.altair_chart(barras_productos)
else:
    st.info("No hay datos de ventas por producto para el período y hora seleccionados.")
