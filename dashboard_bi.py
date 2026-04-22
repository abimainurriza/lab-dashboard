# File untuk visualisasi data dan dashboard BI

import streamlit as st
import plotly.express as px

def show_dashboard(load_data):
    st.title("Dashboard Analisis Laboratorium IPA")
    st.write("""
    Halo Operator! Dashboard ini menyajikan ringkasan aktivitas laboratorium IPA. """)
    
    # --- METRICS UTAMA ---
    col1, col2, col3 = st.columns(3)

    # Load data
    total_alat = load_data("SELECT COUNT(*) as total FROM lab_items").iloc[0]['total']
    total_pinjam = load_data("SELECT COUNT(*) as total FROM lab_bookings").iloc[0]['total']

    # Bungkus tiap kolom dengan container (card)
    with col1:
        with st.container(border=True):
            st.metric("Total Alat", f"{total_alat} Unit")

    with col2:
        with st.container(border=True):
            st.metric("Total Peminjaman", f"{total_pinjam} Kali")

    with col3:
        with st.container(border=True):
            st.metric("Status Sistem", "Online")

    # Membuat dua kolom dengan rasio yang sama (50:50)
    col_grafik1, col_grafik2 = st.columns(2)

    # --- KOLOM KIRI: GRAFIK TAHUNAN ---
    with col_grafik1:
        st.subheader("📈 Tren Tahunan")
        df_tahun = load_data("SELECT YEAR(booking_date) as Tahun, COUNT(*) as Total FROM lab_bookings GROUP BY Tahun ORDER BY Tahun")

        if not df_tahun.empty:
            fig_tahun = px.area(df_tahun, x='Tahun', y='Total', markers=True, color_discrete_sequence=['#007BFF'])
            # Mengatur margin agar grafik tidak terlalu mepet
            fig_tahun.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
            st.plotly_chart(fig_tahun, use_container_width=True)
            
            # --- INSIGHT TAHUNAN ---
            if not df_tahun.empty:
                with st.expander("💡 Lihat Detail Penggunaan Per Tahun"):
                    # Kita urutkan dari tahun terbaru ke terlama agar lebih informatif
                    df_sorted = df_tahun.sort_values('Tahun', ascending=False)
                    
                    for index, row in df_sorted.iterrows():
                        tahun_v = int(row['Tahun'])
                        total_v = int(row['Total'])
                        
                        # Menampilkan teks per baris
                        st.write(f"📅 Tahun **{tahun_v}**: Terjadi **{total_v}** kali penggunaan lab.")

    # --- KOLOM KANAN: GURU TERAKTIF ---
    with col_grafik2:
        st.subheader("🏆 Guru Teraktif")
        df_guru = load_data("""
            SELECT t.full_name as Nama_Guru, COUNT(b.booking_id) as Total 
            FROM lab_bookings b JOIN teachers t ON b.teacher_id = t.teacher_id 
            GROUP BY Nama_Guru ORDER BY Total DESC LIMIT 5
        """)

        if not df_guru.empty:
            # Urutkan agar yang paling banyak ada di atas pada grafik horizontal
            df_guru = df_guru.sort_values('Total', ascending=True)
            fig_guru = px.bar(df_guru, x='Total', y='Nama_Guru', orientation='h', 
                            color='Total', color_continuous_scale='Blues')
            # Mengatur tinggi agar sejajar dengan grafik sebelah
            fig_guru.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350, showlegend=False)
            st.plotly_chart(fig_guru, use_container_width=True)
            
            # Insight Guru
            top_teacher = df_guru.iloc[-1] # Ambil yang terakhir karena tadi di-sort ascending
            with st.expander("💡 Analisis Guru"):
                st.write(f"**{top_teacher['Nama_Guru']}** adalah pengguna paling aktif sebanyak (**{top_teacher['Total']} kali**).")

    st.markdown("---")
    col_grafik3, col_grafik4 = st.columns(2)

    # --- KOLOM KIRI: TOPIK PEMBELAJARAN PALING SERING ---
    with col_grafik3:
        st.subheader("📚 Topik Praktikum Populer")
        df_topik = load_data("""
            SELECT lesson_topic as Topik, COUNT(*) as Total 
            FROM lab_bookings 
            GROUP BY Topik ORDER BY Total DESC LIMIT 5
        """)
        
        if not df_topik.empty:
            fig_topik = px.pie(df_topik, values='Total', names='Topik', 
                            hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            fig_topik.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
            st.plotly_chart(fig_topik, use_container_width=True)
            
            with st.expander("💡 Insight Kurikulum"):
                top_topic = df_topik.iloc[0]
                st.write(f"Materi **'{top_topic['Topik']}'** paling sering dipraktikkan.")
                st.write("Sekolah dapat memastikan ketersediaan bahan habis pakai khusus untuk materi ini agar tidak menghambat KBM.")

    # --- KOLOM KANAN: ALAT PALING SERING DIGUNAKAN ---
    with col_grafik4:
        st.subheader("🛠️ Alat Paling Sering Digunakan")
        df_alat = load_data("""
            SELECT i.item_name as Nama_Alat, SUM(d.quantity) as Total_Dipakai 
            FROM booking_details d 
            JOIN lab_items i ON d.item_id = i.item_id 
            GROUP BY Nama_Alat ORDER BY Total_Dipakai DESC LIMIT 5
        """)
        
        if not df_alat.empty:
            fig_alat = px.bar(df_alat, x='Total_Dipakai', y='Nama_Alat', orientation='h',
                            color='Total_Dipakai', color_continuous_scale='GnBu')
            fig_alat.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350, showlegend=False)
            st.plotly_chart(fig_alat, use_container_width=True)
            
            with st.expander("💡 Insight Inventaris"):
                most_used = df_alat.iloc[0]
                st.write(f"Alat **'{most_used['Nama_Alat']}'** memiliki tingkat utilisasi tertinggi.")
                st.write("Disarankan bagi sekolah untuk melakukan maintenance rutin atau menambah unit alat ini untuk menghindari kekurangan saat kelas paralel.")

    st.markdown("---")
    col_grafik5, col_grafik6 = st.columns(2)

    # --- KOLOM KIRI: DISTRIBUSI PENGGUNAAN BERDASARKAN KELAS ---
    with col_grafik5:
        st.subheader("🏫 Distribusi Beban Kelas")
        # Mengambil data jumlah praktikum per jenjang kelas
        df_kelas = load_data("""
            SELECT class_name as Kelas, COUNT(*) as Total 
            FROM lab_bookings 
            GROUP BY Kelas ORDER BY Total DESC
        """)
        
        if not df_kelas.empty:
            fig_kelas = px.bar(df_kelas, x='Kelas', y='Total', 
                            color='Kelas', color_discrete_sequence=px.colors.qualitative.Safe)
            fig_kelas.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350, showlegend=False)
            st.plotly_chart(fig_kelas, use_container_width=True)
            
            with st.expander("💡 Insight Manajemen Kelas"):
                top_class = df_kelas.iloc[0]
                st.write(f"Kelas **{top_class['Kelas']}** adalah pengguna laboratorium paling padat.")
                st.write("Sekolah dapat mempertimbangkan pembagian jadwal yang lebih merata jika terjadi bentrokan jadwal di jenjang ini.")

    # --- KOLOM KANAN: HARI PALING SIBUK (PEAK DAYS) ---
    with col_grafik6:
        st.subheader("📅 Hari Operasional Tersibuk")
        # Mengambil nama hari dari tanggal booking
        df_hari = load_data("""
            SELECT DAYNAME(booking_date) as Hari, COUNT(*) as Total 
            FROM lab_bookings 
            GROUP BY Hari 
            ORDER BY FIELD(Hari, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
        """)
        
        if not df_hari.empty:
            # Menerjemahkan hari ke Bahasa Indonesia untuk grafik
            hari_map = {
                'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu', 
                'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
            }
            df_hari['Hari'] = df_hari['Hari'].map(hari_map)
            
            fig_hari = px.line(df_hari, x='Hari', y='Total', markers=True,
                            line_shape='spline', render_mode='svg')
            fig_hari.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
            st.plotly_chart(fig_hari, use_container_width=True)
            
            with st.expander("💡 Insight Operasional"):
                # Mencari hari dengan total tertinggi
                busy_day = df_hari.sort_values('Total', ascending=False).iloc[0]
                st.write(f"Hari **{busy_day['Hari']}** adalah waktu tersibuk di laboratorium.")
                st.write("Petugas laboratorium (Laboran) disarankan melakukan persiapan alat ekstra di hari sebelumnya untuk menjaga kelancaran praktikum.")
        
        