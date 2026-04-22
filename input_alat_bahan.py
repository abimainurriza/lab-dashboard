import streamlit as st

def show_input_alat_bahan(load_data, execute_query):
    st.title("Panel Kelola Data Alat & Bahan")

    # --- LOAD DATA ---
    # Pastikan query menyertakan kolom quantity
    df_alat = load_data("SELECT item_id, item_name, category, quantity FROM lab_items ORDER BY item_id DESC")
    list_id = df_alat['item_id'].tolist() if not df_alat.empty else []
    
    opsi_kategori = ["equipment", "material"]

    # --- BAGIAN 1: CONTROL PANEL (CRUD) ---
    tab1, tab2, tab3 = st.tabs(["Tambah", "Edit", "Hapus"])

    with tab1:
        with st.form("form_tambah_alat", clear_on_submit=True):
            st.subheader("Tambah Alat/Bahan Baru")
            nama_alat = st.text_input("Nama Alat/Bahan", placeholder="Masukan Nama Alat atau Bahan")
            
            col1, col2 = st.columns(2)
            with col1:
                kategori = st.selectbox(
                    "Pilih Kategori", 
                    options=opsi_kategori,
                    format_func=lambda x: x.capitalize()
                )
            with col2:
                stok = st.number_input("Jumlah Stok", min_value=0, step=1, value=0)
            
            submit_btn = st.form_submit_button("Tambah")
            
            if submit_btn:
                if nama_alat:
                    # Menambahkan quantity ke dalam query INSERT
                    query = "INSERT INTO lab_items (item_name, category, quantity) VALUES (%s, %s, %s)"
                    if execute_query(query, (nama_alat, kategori, stok)):
                        st.success(f"Berhasil menambah: {nama_alat}")
                        st.rerun()
                else:
                    st.warning("Nama alat tidak boleh kosong!")

    with tab2:
        if not df_alat.empty:
            # Mapping Nama untuk Update agar lebih mudah
            opsi_upd = {f"{row['item_name']} (ID: {row['item_id']})": row['item_id'] for _, row in df_alat.iterrows()}
            pilihan_upd = st.selectbox("Pilih Alat yang akan diubah", options=list(opsi_upd.keys()), key="upd_name_sel")
            
            id_upd = opsi_upd[pilihan_upd]
            curr = df_alat[df_alat['item_id'] == id_upd].iloc[0]
            
            with st.form("form_update_alat"):
                new_nama = st.text_input("Nama Alat/Bahan", value=curr['item_name'])
                
                col1, col2 = st.columns(2)
                with col1:
                    default_idx = opsi_kategori.index(curr['category']) if curr['category'] in opsi_kategori else 0
                    new_kategori = st.selectbox("Kategori", options=opsi_kategori, index=default_idx, format_func=lambda x: x.capitalize())
                with col2:
                    new_stok = st.number_input("Stok", min_value=0, step=1, value=int(curr['quantity']))
                
                if st.form_submit_button("Simpan"):
                    query = "UPDATE lab_items SET item_name=%s, category=%s, quantity=%s WHERE item_id=%s"
                    if execute_query(query, (new_nama, new_kategori, new_stok, id_upd)):
                        st.success("Data alat berhasil diperbarui!")
                        st.rerun()
        else:
            st.info("Belum ada data untuk diupdate.")

    with tab3:
        if not df_alat.empty:
            opsi_hapus = {f"{row['item_name']} (ID: {row['item_id']})": row['item_id'] for _, row in df_alat.iterrows()}
            pilihan_nama = st.selectbox("Pilih Nama Alat yang akan dihapus", options=list(opsi_hapus.keys()), key="del_alat_name_sel")
            
            id_del = opsi_hapus[pilihan_nama]
            curr_del = df_alat[df_alat['item_id'] == id_del].iloc[0]
            
            st.error(f"**Konfirmasi:** Anda akan menghapus **{pilihan_nama}**\n\nKategori: {curr_del['category']} | Jumlah Stok saat ini: {curr_del['quantity']}")
            
            if st.button("Hapus", type="primary", key="btn_del_alat"):
                query = "DELETE FROM lab_items WHERE item_id = %s"
                if execute_query(query, (id_del,)):
                    st.success(f"Berhasil menghapus {pilihan_nama}!")
                    st.rerun()
                else:
                    st.error("Gagal menghapus! Data ini mungkin masih digunakan di tabel transaksi peminjaman.")
        else:
            st.info("Belum ada data untuk dihapus.")

    st.markdown("---")

    # --- BAGIAN 2: TAMPILAN DATA ---
    st.subheader("Daftar Alat & Bahan")
    if not df_alat.empty:
        display_df = df_alat.rename(columns={
            'item_id': 'ID', 
            'item_name': 'Nama Alat/Bahan', 
            'category': 'Kategori',
            'quantity': 'Jumlah Stok'
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("Database alat masih kosong.")