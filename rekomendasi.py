import streamlit as st 
import pickle
import os

def show_rekomendasi():
    st.write("---")
    st.subheader("Rekomendasi Asisten Lab (AI)")

    model_path = 'model/model_rekomendasi.pkl'

    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                rekomendasi_dict = pickle.load(f)

            daftar_topik = list(rekomendasi_dict.keys())
            
            if not daftar_topik:
                st.warning("Model ditemukan, tapi belum ada pola data yang dipelajari.")
                return

            selected_topic = st.selectbox(
                "Pilih Topik Praktikum untuk melihat kebutuhan alat:",
                options=daftar_topik,
                index=0,
                format_func=lambda x: x.title(),
                key="mining_selectbox"
            )

            # 4. Logika Rekomendasi
            if selected_topic:
                item_rekomendasi = rekomendasi_dict[selected_topic]
                
                st.info(f"💡 **Insight Data Mining:**")
                st.markdown(f"""
                Berdasarkan data historis, jika topik praktikum adalah **{selected_topic.title()}**, 
                maka alat yang paling sering digunakan dan harus disiapkan adalah: 
                ### ✨ **{item_rekomendasi.title()}**
                """)
        except Exception as e:
            st.error(f"Gagal memuat model: {e}")
            
    else:
        st.warning("⚠️ Sistem rekomendasi belum siap. Harap jalankan 'scripts/train_model.py' terlebih dahulu di terminal.")