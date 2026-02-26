import os

class Config:
    # Kunci rahasia untuk session (biarkan saja)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci_rahasia_anda_disini'
    
    # KONFIGURASI DATABASE
    # Format: mysql+pymysql://USERNAME:PASSWORD@HOST:PORT/NAMA_DATABASE
    
    # ✅ PERBAIKAN: TAMBAH ':5000' SETELAH localhost
    # KASUS 1: Jika MySQL di port 5000
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3307/spk_cabai_db'
    
    # KASUS 2: Jika tidak butuh password
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:5000/spk_cabai_db'
    
    # KASUS 3: Jika pakai password
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password_anda@localhost:5000/spk_cabai_db'
    
    # Mematikan notifikasi track modification (untuk performa)
    SQLALCHEMY_TRACK_MODIFICATIONS = False