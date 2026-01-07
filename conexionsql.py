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
                        v.fechapedido as fecha, 
                        v.semana,
                        v.comedor,
                        v.pedido AS nro_pedido,
                        v.familia,
                        p.alterno as codigo,
                        p.nombre as descripcion,
                        v.presentacion,
                        v.cantidad,
                        v.costo_dolar,
                        v.precio AS precio_dolar,
                        v.cantidad * v.costo_dolar AS costo_total_dolar,
                        v.cantidad * v.precio AS precio_total_dolar,
                        v.observacion,
                        v.finiquito
                    FROM v_pedidos v
                    inner join productos p 
                    on p.alterno = v.codigo
                    WHERE fechapedido >= '2026-01-02'
                    AND cerrado = 0 ;'''
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



