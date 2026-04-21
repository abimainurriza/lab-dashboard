import streamlit as st
import pandas as pd
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_lab_management"
    )

def load_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def execute_query(query, data=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        conn.commit() # Menyimpan perubahan ke database
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Gagal eksekusi query: {e}")
        return False