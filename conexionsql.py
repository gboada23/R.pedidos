import pandas as pd
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy import text
from mysql.connector import Error
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st

class MYSQL:
    def __init__(self):
        self.user = st.secrets["mysql"]["user"]
        self.password = st.secrets["mysql"]["password"]
        self.host = st.secrets["mysql"]["host"]
        self.database = st.secrets["mysql"]["database"]
        # Inicializa la conexión al crear la instancia
        self.engine = self.create_connection()

    def create_connection(self):
        # Método para crear y retornar la conexión usando PyMySQL
        password_encoded = urllib.parse.quote(self.password)
        connection_string = f'mysql+pymysql://{self.user}:{password_encoded}@{self.host}/{self.database}'
        try:
            engine = create_engine(connection_string)
            return engine
        except SQLAlchemyError as e:
            st.error(f"Error al conectar a la base de datos: {e}")
            return None


    def tabla_inventario(self):
        query = '''
            SELECT i1.FECHA, i1.unidad, i1.CODIGO, i1.alterno, i1.PRODUCTO, i1.FISICO
            FROM inventario_dat i1
            INNER JOIN (
                SELECT CODIGO, unidad, MAX(FECHA) AS MaxFecha
                FROM inventario_dat
                GROUP BY CODIGO
            ) i2
            ON i1.CODIGO = i2.CODIGO AND i1.FECHA = i2.MaxFecha;
        '''
        return self.fetch_data(query)

    def vista_pedidos(self):
        query = '''SELECT 
                        fechapedido as fecha, 
                        semana,
                        comedor,
                        pedido AS nro_pedido,
                        familia,
                        descripcion,
                        presentacion
                        cantidad,
                        costo_dolar,
                        precio AS precio_dolar,
                        cantidad * costo_dolar AS costo_total_dolar,
                        cantidad * precio AS precio_total_dolar
                    FROM v_pedidos
                    WHERE fechapedido >= '2024-04-01'
                    AND costo_dolar != 0
                    AND precio !=0 ;'''
        return self.fetch_data(query)

    def fetch_data(self, query):
        try:
            if self.engine:
                # Ejecuta la consulta y convierte el resultado en un DataFrame
                df = pd.read_sql(query, self.engine)
                return df
            else:
                st.error("No se pudo establecer la conexión con la base de datos.")
                return None
        except SQLAlchemyError as e:
            st.error(f"Error al ejecutar la consulta: {e}")
            return None

