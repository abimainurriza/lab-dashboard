import streamlit as st
import pandas as pd
from datetime import datetime

def show_input_peminjaman(load_data, execute_query):
    st.title("Panel Kelola Data Peminjaman Lab IPA")

    # 1. Inisialisasi Keranjang di Session State
    if 'keranjang_pinjam' not in st.session_state:
        st.session_state.keranjang_pinjam = []

    # 2. Load Data Master
    df_guru = load_data("SELECT teacher_id, full_name FROM teachers")
    df_alat = load_data("SELECT item_id, item_name, quantity FROM lab_items").fillna(0)
    
    # Load Data Riwayat
    query_riwayat = """
        SELECT b.booking_id, b.booking_date, t.full_name, b.class_name, b.lesson_topic, b.student_count
        FROM lab_bookings b
        JOIN teachers t ON b.teacher_id = t.teacher_id
        ORDER BY b.booking_id DESC
    """
    df_riwayat = load_data(query_riwayat).fillna(0)

    tab1, tab2, tab3 = st.tabs(["Tambah", "Edit", "Hapus"])

    # ================= TAB 1: INPUT BARU =================
    with tab1:
        with st.container(border=True):
            st.subheader("Tambah Penggunaan Lab")
            c_a, c_b = st.columns(2)
            with c_a:
                if not df_guru.empty:
                    opsi_guru = {row['full_name']: row['teacher_id'] for _, row in df_guru.iterrows()}
                    nama_peminjam = st.selectbox("Guru", options=list(opsi_guru.keys()), key="in_guru")
                tgl_pinjam = st.date_input("Tanggal", value=datetime.now(), key="in_date")
            with c_b:
                kelas = st.text_input("Kelas", placeholder="Masukan Kelas", key="in_class")
                topik = st.text_input("Topik", placeholder="Masukan Topik", key="in_topic")
                jml_siswa = st.number_input("Jumlah Siswa", min_value=1, value=1, key="in_siswa")

        with st.container(border=True):
            st.subheader("Tambah Penggunaan Alat")
            c1, c2 = st.columns([3, 1])
            opsi_alat = {f"{r['item_name']} (Stok: {int(r['quantity'])})": r for _, r in df_alat.iterrows()}
            
            with c1:
                pilihan_label = st.selectbox("Pilih Alat", options=list(opsi_alat.keys()), key="in_item")
                alat_data = opsi_alat[pilihan_label]
            with c2:
                stok_tersedia = int(alat_data['quantity'])
                qty = st.number_input("Jumlah", min_value=1, max_value=max(1, stok_tersedia), key="in_qty")
            
            # Tombol Tambah ke daftar sementara
            if st.button("Tambah ke Daftar", use_container_width=True, key="btn_add_list"):
                st.session_state.keranjang_pinjam.append({
                    "id_alat": int(alat_data['item_id']), 
                    "nama_alat": alat_data['item_name'], 
                    "jumlah": int(qty)
                })
                st.rerun()

        # --- (BAGIAN SIMPAN & KOSONGKAN YANG SUDAH DIPERBAIKI) ---
        if st.session_state.keranjang_pinjam:
            st.markdown("### Daftar Alat Sementara")
            st.table(
                pd.DataFrame(st.session_state.keranjang_pinjam)
                .rename(columns={'nama_alat': 'Nama Alat', 'jumlah': 'Jumlah'})
                [['Nama Alat', 'Jumlah']]
            )
            
            # Membuat dua kolom untuk tombol agar sejajar
            col_simpan, col_reset = st.columns(2)
            
            with col_simpan:
                if st.button("Simpan", use_container_width=True):
                    # 1. Simpan Header
                    q_h = "INSERT INTO lab_bookings (teacher_id, booking_date, class_name, lesson_topic, student_count) VALUES (%s,%s,%s,%s,%s)"
                    params_h = (opsi_guru[nama_peminjam], tgl_pinjam, kelas, topik, jml_siswa)
                    
                    if execute_query(q_h, params_h):
                        # 2. Ambil ID terakhir
                        df_id = load_data("SELECT MAX(booking_id) as last_id FROM lab_bookings")
                        
                        if not df_id.empty:
                            last_id = int(df_id.iloc[0]['last_id'])
                            
                            # 3. Simpan Detail dengan Looping
                            sukses_semua = True
                            for itm in st.session_state.keranjang_pinjam:
                                q_d = "INSERT INTO booking_details (booking_id, item_id, quantity) VALUES (%s, %s, %s)"
                                params_d = (last_id, int(itm['id_alat']), int(itm['jumlah']))
                                
                                if not execute_query(q_d, params_d):
                                    sukses_semua = False
                                    st.error(f"Gagal simpan alat: {itm['nama_alat']}")
                            
                            if sukses_semua:
                                st.success(f"✅ Transaksi {last_id} Berhasil Disimpan!")
                                st.session_state.keranjang_pinjam = []
                                st.rerun()
                        else:
                            st.error("Gagal mendapatkan ID terakhir.")

            # SEJAJAR DENGAN with col_simpan (Keluar dari blok IF simpan)
            with col_reset:
                if st.button("Kosongkan", type="primary", use_container_width=True, key="btn_reset_manual"):
                    st.session_state.keranjang_pinjam = []
                    st.toast("Keranjang dikosongkan")
                    st.rerun()

    # ================= TAB 2: EDIT TRANSAKSI =================
    with tab2:
        if not df_riwayat.empty:
            dict_edit = {f"ID: {r['booking_id']} | {r['full_name']}": r['booking_id'] for _, r in df_riwayat.iterrows()}
            id_edit_sel = st.selectbox("Pilih Transaksi untuk Diedit", options=list(dict_edit.keys()), key="edit_sel")
            curr_id = dict_edit[id_edit_sel]
            
            data_now = df_riwayat[df_riwayat['booking_id'] == curr_id].iloc[0]
            
            with st.form("form_edit_header"):
                st.subheader("Edit Penggunaan Lab")
                ce1, ce2 = st.columns(2)
                with ce1:
                    ed_kelas = st.text_input("Kelas", value=str(data_now['class_name']))
                    ed_topik = st.text_input("Topik", value=str(data_now['lesson_topic']))
                with ce2:
                    val_s = int(data_now['student_count']) if pd.notnull(data_now['student_count']) else 1
                    ed_siswa = st.number_input("Jumlah Siswa", min_value=1, value=max(1, val_s))
                
                if st.form_submit_button("Simpan"):
                    q_upd = "UPDATE lab_bookings SET class_name=%s, lesson_topic=%s, student_count=%s WHERE booking_id=%s"
                    execute_query(q_upd, (ed_kelas, ed_topik, ed_siswa, curr_id))
                    st.success("Data utama berhasil diperbarui!")
                    st.rerun()

            st.markdown("---")
            st.subheader("Edit Daftar Alat")
            df_items_saved = load_data(f"""
                SELECT d.detail_id, i.item_name, d.quantity, d.item_id 
                FROM booking_details d 
                JOIN lab_items i ON d.item_id = i.item_id 
                WHERE d.booking_id = {curr_id}
            """)

            if not df_items_saved.empty:
                for _, row in df_items_saved.iterrows():
                    col_n, col_q, col_b = st.columns([3, 1, 1])
                    col_n.write(f"**{row['item_name']}**")
                    col_q.write(f"{int(row['quantity'])} pcs")
                    if col_b.button("Hapus", type="primary", key=f"del_det_{row['detail_id']}"):
                        execute_query(f"DELETE FROM booking_details WHERE detail_id = {row['detail_id']}")
                        st.rerun()
            else:
                st.info("Belum ada alat yang ditambahkan untuk transaksi ini.")
            
            with st.expander("Tambah Alat Baru ke Transaksi Ini"):
                c_t1, c_t2 = st.columns([3, 1])
                with c_t1:
                    new_item_label = st.selectbox("Pilih Alat", options=list(opsi_alat.keys()), key="edit_add_item")
                    new_item_data = opsi_alat[new_item_label]
                with c_t2:
                    new_qty = st.number_input("Jumlah", min_value=1, key="edit_add_qty")
                
                if st.button("Tambah", use_container_width=True):
                    execute_query("INSERT INTO booking_details (booking_id, item_id, quantity) VALUES (%s,%s,%s)", 
                                (curr_id, int(new_item_data['item_id']), int(new_qty)))
                    st.success("Alat berhasil ditambahkan!")
                    st.rerun()
        else:
            st.info("Tidak ada data untuk diedit.")

    # ================= TAB 3: HAPUS =================
    with tab3:
        if not df_riwayat.empty:
            st.subheader("Hapus Peminjaman Lab")
            id_del_pilih = st.selectbox("Pilih ID untuk Dihapus Total", options=df_riwayat['booking_id'].tolist())
            st.warning(f"Tindakan ini akan menghapus ID {id_del_pilih} beserta seluruh daftar alatnya!")
            if st.button("Hapus", type="primary", use_container_width=True):
                execute_query("DELETE FROM lab_bookings WHERE booking_id = %s", (id_del_pilih,))
                st.success("Data berhasil dihapus!")
                st.rerun()
        else:
            st.info("Tidak ada data untuk dihapus.")

    # --- TABEL RIWAYAT DI BAWAH ---
    st.markdown("---")
    st.subheader("Riwayat Penggunaan Lab Terkini")
    if not df_riwayat.empty:
        st.dataframe(
            df_riwayat.rename(columns={
                'booking_id':'ID',
                'booking_date':'Tanggal',
                'full_name':'Guru',
                'class_name':'Kelas',
                'lesson_topic':'Topik',
                'student_count':'Siswa'
            }), 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Riwayat masih kosong.")