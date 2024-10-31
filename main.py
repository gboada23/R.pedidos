import streamlit as st
from conexionsql import MYSQL
import pandas as pd
import io
from datetime import datetime
#INSTANCIA SQL 
Mysql = MYSQL()
# CREAMOS EL DF CON EL METODO DE LA CLASE MYSQL
df = Mysql.vista_pedidos()
# CONFIGURAMOS LA PAGINA
layout = "centered"
page_title = "Rentabilidad | Productos"
page_icon = "🚛"

st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout)
# CARGAMOS EL CSS
# AÑADIMOS EL ESTILO
css_file = "styles/main.css"
with open(css_file) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
col1,  col2, col3 = st.columns((1,3,1))
with col2:
    # Mostramos el logo
    logo = st.image('assets/logo.png', width=350)
# modifcamos el tipo de dato fecha to_datetime 
df['fecha'] = pd.to_datetime(df['fecha'], format='%d-%m-%Y').dt.date

# AGREGAMOS UNA COLUMNA CON LA SEMANA DEL AÑO
df['semana'] = df['semana'].astype(int)
# CREAMOS LA TABLA CON STREAMLIT
df.sort_values(by=['fecha'],inplace=True)
df['codigo'] = df['codigo'].str.strip()
df['codigo'] = df['codigo'].astype(int)
df['familia'] = df['familia'].str.strip()
df['comedor'] = df['comedor'].str.strip()
df['descripcion'] = df['descripcion'].str.strip()
df['presentacion'] = df['presentacion'].str.strip()
df['nro_pedido'] = df['nro_pedido'].str.strip()
frio = ['CHARCUTERIA','PROTEICO','PRODUCTOS CONGELADOS']
# Filtrar el DataFrame donde la columna 'familia' está en la lista 'frio'

st.markdown("<h1 style='text-align: center;'>Tablero de Pedidos</h1>", unsafe_allow_html=True)

st.subheader("¿Cómo te gustaría realizar el filtrado?")

selected_week = st.radio("Elija un filtro:", ['Semana', 'Semana y comedor', 'Mes', 'Mes y Comedor',
                                              'Familia', 'Familia y Comedor', 'Nro de pedido'])

# Función para convertir el dataframe en un archivo de Excel
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()  # Cierra y guarda el archivo correctamente
    processed_data = output.getvalue()
    return processed_data

# Lista de semanas para el selectbox (del 1 al 52)
weeks = list(range(1, 53))
# Obtener la semana actual
current_week = datetime.now().isocalendar()[1]

# Variable para almacenar el DataFrame filtrado
df_filtered = pd.DataFrame()  # Inicializa df_filtered

# Función para aplicar los filtros
def filter_data():
    # Declarar df_filtered dentro de la función
    df_filtered = pd.DataFrame()  # Reiniciar df_filtered

    if selected_week == 'Semana':
        week_filter = st.selectbox("Semana", weeks, index=weeks.index(current_week))
        df_filtered = df[df['semana'] == week_filter]


    elif selected_week == 'Semana y comedor':
        week_filter = st.selectbox("Semana", weeks, index=weeks.index(current_week))
        comer_filter = st.selectbox("Comedor", df['comedor'].unique().tolist())
        df_filtered = df[(df['semana'] == week_filter) & (df['comedor'] == comer_filter)]

    elif selected_week == 'Mes':
        month_filter = st.selectbox("Mes", df['fecha'].dt.month_name().unique().tolist())
        df_filtered = df[df['fecha'].dt.month_name() == month_filter]

    elif selected_week == 'Mes y Comedor':
        month_filter = st.selectbox("Mes", df['fecha'].dt.month_name().unique().tolist())
        comer_filter = st.selectbox("Comedor", df['comedor'].unique().tolist())
        df_filtered = df[(df['fecha'].dt.month_name() == month_filter) & (df['comedor'] == comer_filter)]

    elif selected_week == 'Familia':
        family_filter = st.selectbox("Familia", df['familia'].unique().tolist())
        df_filtered = df[df['familia'] == family_filter]

    elif selected_week == 'Familia y Comedor':
        family_filter = st.selectbox("Familia", df['familia'].unique().tolist())
        comer_filter = st.selectbox("Comedor", df['comedor'].unique().tolist())
        df_filtered = df[(df['familia'] == family_filter) & (df['comedor'] == comer_filter)]

    elif selected_week == 'Nro de pedido':
        pedido_filter = st.text_input("Introduce el Nro de pedido completo: ")
        df_filtered = df[df['nro_pedido'] == pedido_filter]

    return df_filtered  # Retornar el DataFrame filtrado


df_filtered = filter_data()

# Checkbox para filtrar por productos fríos
filtro_frios = st.checkbox("¿Desea ver solo los productos fríos?", value=False)

# Filtrar los productos fríos si se selecciona el checkbox
if filtro_frios:
    df_filtered = df_filtered[df_filtered['familia'].isin(frio)]

# Mostrar el DataFrame filtrado si no está vacío
if not df_filtered.empty:
    st.dataframe(df_filtered)

    # Botón para descargar el DataFrame filtrado como archivo Excel
    excel_data = to_excel(df_filtered)
    st.download_button(
        label="Descargar como Excel",
        data=excel_data,
        file_name='datos_pedidos.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
else:
    st.warning("No se encontraron resultados para los filtros seleccionados.")