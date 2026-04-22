import streamlit as st
from db_manager import load_data, execute_query
from dashboard_bi import show_dashboard
from input_alat_bahan import show_input_alat_bahan
from input_guru import show_input_guru
from input_peminjaman import show_input_peminjaman

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Lab Analytics Al-Azhar 17", 
    layout="wide"
)

# Custom CSS untuk padding atas
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigasi Sidebar
st.sidebar.image("logosmp.png", width=100) # Ganti logo sekolah jika ada
st.sidebar.write("Dashboard BI Peminjaman Lab IPA")
menu = st.sidebar.radio("Daftar Menu:", ["Dashboard", "Peminjaman", "Guru", "Alat & Bahan"])

# Logika Perpindahan Halaman
if menu == "Dashboard":
    show_dashboard(load_data)
    
elif menu == "Peminjaman":
    show_input_peminjaman(load_data, execute_query)

elif menu == "Guru":
    show_input_guru(load_data, execute_query)

elif menu == "Alat & Bahan":
    show_input_alat_bahan(load_data, execute_query)

# Di app.py dalam section sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Laporan")

# Query data lengkap untuk didownload
df_download = load_data("SELECT * FROM lab_bookings")

if not df_download.empty:
    csv = df_download.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Data CSV",
        data=csv,
        file_name='laporan_lab_ipa.csv',
        mime='text/csv',
    )

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Magang IT Al-Azhar")