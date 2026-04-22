import streamlit as st

def show_input_guru(load_data, execute_query):
    st.title("Panel Kelola Data Guru")

    # --- BAGIAN 1: CONTROL PANEL (CRUD) ---
    # Kita bagi menjadi 3 kolom agar hemat tempat di bagian atas
    df_guru = load_data("SELECT teacher_id, full_name, subject FROM teachers ORDER BY teacher_id DESC")
    list_id = df_guru['teacher_id'].tolist() if not df_guru.empty else []

    tab1, tab2, tab3 = st.tabs(["Tambah", "Edit", "Hapus"])

    with tab1:
        with st.form("form_tambah", clear_on_submit=True):
            st.subheader("Tambah Guru")
            nama = st.text_input("Nama Lengkap", placeholder="Masukan Nama Guru")
            mapel = st.text_input("Mata Pelajaran", placeholder="Masukan Mata Pelajaran")
            
            submit_btn = st.form_submit_button("Tambah")
            
            if submit_btn:
                if nama and mapel:
                    # Pastikan nama kolom 'full_name' dan 'subject' 
                    # Sesuai dengan yang ada di HeidiSQL
                    query = "INSERT INTO teachers (full_name, subject) VALUES (%s, %s)"
                    data = (nama, mapel)
                    
                    # Kita panggil execute_query
                    if execute_query(query, data):
                        st.success(f"Berhasil menambah guru: {nama}")
                        st.rerun()
                    else:
                        st.error("Gagal menyimpan ke Database. Cek terminal untuk detailnya.")
                else:
                    st.warning("Nama dan Mapel wajib diisi!")

    with tab2:
        if list_id:
            id_upd = st.selectbox("Pilih ID Guru yang akan diubah", options=list_id, key="upd_sel")
            # Ambil data spesifik yang dipilih
            curr = df_guru[df_guru['teacher_id'] == id_upd].iloc[0]
            
            with st.form("form_update"):
                new_nama = st.text_input("Nama Baru", value=curr['full_name'])
                new_mapel = st.text_input("Mata Pelajaran Baru", value=curr['subject'])
                if st.form_submit_button("Simpan"):
                    st.write(f"Mencoba update ID: {id_upd} dengan nama {new_nama}")
                    execute_query("UPDATE teachers SET full_name=%s, subject=%s WHERE teacher_id=%s", (new_nama, new_mapel, id_upd))
                    st.success("Data berhasil diperbarui!")
                    st.rerun()
        else:
            st.info("Belum ada data untuk diperbarui.")

    with tab3:
        if not df_guru.empty:
            # 1. Buat mapping Nama ke ID agar user tidak perlu menghafal angka ID
            # Kita tampilkan "Nama (Mapel)" supaya kalau ada nama sama, bisa dibedakan
            opsi_guru = {f"{row['full_name']} ({row['subject']})": row['teacher_id'] for _, row in df_guru.iterrows()}
            
            # 2. Dropdown pilihan berdasarkan Nama
            pilihan_label = st.selectbox(
                "Pilih Guru yang akan dihapus", 
                options=list(opsi_guru.keys()), 
                key="del_guru_name_sel"
            )
            
            # 3. Ambil ID asli dari label yang dipilih
            id_del = opsi_guru[pilihan_label]
            
            st.error(f"**Konfirmasi:** Anda akan menghapus data guru: **{pilihan_label}**")
            
            # Tombol hapus dengan warna merah (primary)
            if st.button("Hapus", type="primary", key="btn_del_guru"):
                query = "DELETE FROM teachers WHERE teacher_id = %s"
                
                # Eksekusi dengan tuple (id_del,)
                success = execute_query(query, (id_del,))
                
                if success:
                    st.success(f"Data guru {pilihan_label} berhasil dihapus!")
                    st.rerun()
                else:
                    st.error("Gagal menghapus! Guru ini kemungkinan masih memiliki riwayat di tabel peminjaman.")
        else:
            st.info("Belum ada data guru untuk dihapus.")

    st.markdown("---")

    # --- BAGIAN 2: TAMPILAN DATA (DI BAWAH) ---
    st.subheader("Daftar Guru")
    if not df_guru.empty:
        
        display_df = df_guru.rename(columns={
            'teacher_id': 'ID', 
            'full_name': 'Nama Lengkap',
            'subject': 'Mata Pelajaran'
        })
        # Menampilkan tabel
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("Database kosong.")