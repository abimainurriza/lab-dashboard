import streamlit as st

st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. KONFIGURASI HALAMAN (Tab Browser)
st.set_page_config(
    page_title="Lab Analytics Al-Azhar 17", 
    # page_icon="🧪",
    layout="wide"
)

# 2. SIDEBAR (Identitas & Navigasi)
with st.sidebar:
    st.image("logosmp.png", width=70)
    st.header("SMP Islam Al Azhar 17")
    st.markdown("---")
    
    st.title("Filter Panel")
    # Pilihan Guru (Dummy dulu karena kita fokus tampilan)
    st.selectbox("Pilih Guru:", ["Semua Guru", "Guru A", "Guru B"])
    st.date_input("Rentang Waktu:")
    
    st.markdown("---")
    st.caption("Dashboard v1.0 - Operator Lab")

# 3. AREA UTAMA (Header Section)
st.title("Dashboard Analisis Laboratorium")
st.write("Selamat datang Operator! Berikut adalah ringkasan aktivitas laboratorium.")
st.write("Tahun 2022-2026.")
st.markdown("---")

# 4. BAGIAN METRICS (Tiap Metrik Dibungkus Kotak)
m1, m2, m3, m4 = st.columns(4)

with m1:
    with st.container(border=True):
        st.metric(value="120", label="Total Peminjaman")

with m2:
    with st.container(border=True):
        st.metric(value="15", label="Total Alat")

with m3:
    with st.container(border=True):
        st.metric(value="3", label="Guru Aktif")

st.markdown("---")

# 5. BAGIAN LAYOUT VISUALISASI (Placeholder)
# Kita bagi menjadi dua area besar: Kiri untuk Tabel/Daftar, Kanan untuk Grafik
left_col, right_col = st.columns([1.2, 2]) # Angka 2 berarti kolom kanan lebih lebar

with left_col:
    st.subheader("Daftar Aktivitas Terakhir")
    # Tempat sementara untuk tabel data
    st.info("Area ini nanti akan berisi tabel 5 peminjaman terbaru.")
    # Kotak kosong untuk visualisasi tabel
    st.empty() 

with right_col:
    st.subheader("Tren Penggunaan Lab")
    # Tempat sementara untuk grafik
    st.warning("Area ini nanti akan berisi grafik frekuensi peminjaman.")
    # Kotak kosong untuk visualisasi grafik
    st.empty()

# 6. BAGIAN FOOTER (Informasi Tambahan)
st.markdown("---")
st.write("*Tips: Gunakan filter di sebelah kiri untuk menyaring data berdasarkan guru atau tanggal.*")