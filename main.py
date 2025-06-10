import streamlit as st
from conexionsql import MYSQL
import pandas as pd
import io
from datetime import datetime

# Instancia de la conexión SQL
Mysql = MYSQL()
df = Mysql.vista_pedidos()

# Configuración de la página
st.set_page_config(
    page_title="Rentabilidad | Productos",
    page_icon="🚛",
    layout="centered"
)

# Cargar CSS personalizado
css_file = "styles/main.css"
with open(css_file) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Centrar el logo y título
# Cargar el logo correctamente
col1, col2, col3 = st.columns((2, 3, 2))

with col2:
    st.image("assets/logo.png", width=350)

# Encabezado centrado
st.markdown("<h1 style='text-align: center; color: black;'>Tablero de Pedidos</h1>", unsafe_allow_html=True)


# Modificar formato de fecha
df['fecha'] = pd.to_datetime(df['fecha'], format='%d-%m-%Y').dt.date
df['codigo'] = df['codigo'].str.strip().astype(int)
df['familia'] = df['familia'].str.strip()
df['comedor'] = df['comedor'].str.strip()
df['descripcion'] = df['descripcion'].str.strip()
df['presentacion'] = df['presentacion'].str.strip()
df['nro_pedido'] = df['nro_pedido'].str.strip()

# Definir familias frías
frio = ['CHARCUTERIA', 'PROTEICO', 'PRODUCTOS CONGELADOS']

# Sección de filtros
st.subheader("Filtrar datos por:")

selected_filter = st.radio("Seleccione una opción:", 
    ['Semana', 'Semana y comedor', 'Mes', 'Mes y Comedor', 'Familia', 
     'Familia y Comedor', 'Nro de pedido'])

weeks = list(range(1, 53))
current_week = datetime.now().isocalendar()[1]
df_filtered = pd.DataFrame()  # Inicialización

# Aplicar filtros
def filter_data():
    if selected_filter == 'Semana':
        week_filter = st.selectbox("Semana", weeks, index=weeks.index(current_week))
        return df[df['semana'] == week_filter]

    elif selected_filter == 'Semana y comedor':
        week_filter = st.selectbox("Semana", weeks, index=weeks.index(current_week))
        comer_filter = st.selectbox("Comedor", df['comedor'].unique().tolist())
        return df[(df['semana'] == week_filter) & (df['comedor'] == comer_filter)]

    elif selected_filter == 'Mes':
        month_filter = st.selectbox("Mes", df['fecha'].dt.month_name().unique().tolist())
        return df[df['fecha'].dt.month_name() == month_filter]

    elif selected_filter == 'Mes y Comedor':
        month_filter = st.selectbox("Mes", df['fecha'].dt.month_name().unique().tolist())
        comer_filter = st.selectbox("Comedor", df['comedor'].unique().tolist())
        return df[(df['fecha'].dt.month_name() == month_filter) & (df['comedor'] == comer_filter)]

    elif selected_filter == 'Familia':
        family_filter = st.selectbox("Familia", df['familia'].unique().tolist())
        return df[df['familia'] == family_filter]

    elif selected_filter == 'Familia y Comedor':
        family_filter = st.selectbox("Familia", df['familia'].unique().tolist())
        comer_filter = st.selectbox("Comedor", df['comedor'].unique().tolist())
        return df[(df['familia'] == family_filter) & (df['comedor'] == comer_filter)]

    elif selected_filter == 'Nro de pedido':
        pedido_filter = st.text_input("Introduce el Nro de pedido:")
        return df[df['nro_pedido'] == pedido_filter]

df_filtered = filter_data()

# Aplicar filtros de checkboxes
if st.checkbox("Mostrar solo productos fríos"):
    df_filtered = df_filtered[df_filtered['familia'].isin(frio)]
if st.checkbox("Mostrar solo productos NO finiquitados"):
    df_filtered = df_filtered[df_filtered['finiquito'] == 0]
if st.checkbox("Mostrar solo productos finiquitados"):
    df_filtered = df_filtered[df_filtered['finiquito'] == 1]

# Mostrar la tabla si hay datos
if not df_filtered.empty:
    st.dataframe(df_filtered, height=500)
    st.markdown(f"#### {len(df_filtered)} productos encontrados")
    
    # Botón para descargar el Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
    st.download_button("Descargar Excel", output.getvalue(), "datos_pedidos.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.warning("No hay datos con los filtros seleccionados.")
