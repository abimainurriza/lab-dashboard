import pandas as pd
import pickle
import os
import sys

# Menambahkan folder utama ke path agar bisa import db_manager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_manager import get_connection

def train_association_logic():
    print("🚀 Memulai proses Data Mining (Association Rules)...")
    try:
        conn = get_connection()
        
        # Query Tiga Tingkat untuk menghubungkan Topik dengan Nama Alat
        query = """
        SELECT 
            b.lesson_topic, 
            i.item_name
        FROM lab_bookings b
        JOIN booking_details bd ON b.booking_id = bd.booking_id
        JOIN lab_items i ON bd.item_id = i.item_id
        """ 

        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        
        cursor.close()
        conn.close()

        if not df.empty:
            # Standarisasi teks huruf kecil dan hapus spasi tambahan
            df['lesson_topic'] = df['lesson_topic'].str.lower().str.strip()
            df['item_name'] = df['item_name'].str.lower().str.strip()

            # LOGIKA DATA MINING: 
            # Mencari alat (item_name) yang paling sering muncul untuk setiap topik (lesson_topic)
            model_logika = df.groupby('lesson_topic')['item_name'].agg(lambda x: x.mode()[0]).to_dict()

            # Pastikan folder model ada
            if not os.path.exists('model'):
                os.makedirs('model')

            # Simpan AI ke file .pkl
            with open('model/model_rekomendasi.pkl', 'wb') as f:
                pickle.dump(model_logika, f)
            
            print(f"✅ Berhasil! Ditemukan {len(model_logika)} pola hubungan.")
            print("📂 File 'model_rekomendasi.pkl' telah diperbarui.")
            
            print("\nPreview Rekomendasi:")
            for topic, item in list(model_logika.items())[:3]:
                print(f"   - Jika Topik: {topic.title()} -> Siapkan: {item.title()}")
        else:
            print("⚠️ Data belum ada. Pastikan sudah ada data di booking_details.")

    except Exception as e:
        print(f"❌ Error saat training: {e}")

if __name__ == "__main__":
    train_association_logic()