import streamlit as st
import pandas as pd
import mysql.connector

def get_connection():
    # return mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="",
    #     database="db_lab_management"
    # )

    # Membaca kredensial dari Streamlit Secrets
    db_config = st.secrets["mysql"]

    return mysql.connector.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        ssl_disabled=False,  # Wajib untuk Aiven
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
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Gagal eksekusi query: {e}")
        return False