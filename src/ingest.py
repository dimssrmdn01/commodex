import os
import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

#konfigurasi
DB_USER = "admin"
DB_PASSWORD = "adminpassword"
DB_HOST = "127.0.0.1"
DB_PORT = "5433"
DB_NAME = "komoditas_db"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def fetch_api_data():
    """Mengambil data real-time komoditas/kripto dari API publik"""
    print("Fetching data dari API...")
    #menggunakan API CoinGecko
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,tether,solana,binancecoin",
        "vs_currencies": "idr,usd",
        "include_24hr_change": "true",
        "include_last_updated_at": "true"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    #JSON mentah ke bentuk DataFrame
    records = []
    for asset, val in data.items():
        records.append({
            "asset_id": asset,
            "price_idr": val.get("idr"),
            "price_usd": val.get("usd"),
            "change_24h_idr": val.get("idr_24h_change"),
            "last_updated_timestamp": val.get("last_updated_at"),
            "ingested_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return pd.DataFrame(records)

def load_to_bronze(df):
    """Menyimpan data mentah ke PostgreSQL (Bronze Layer)"""
    print("Connecting ke PostgreSQL...")
    engine = create_engine(DATABASE_URL)
    
    df.to_sql("bronze_harga_pasar", con=engine, if_exists="append", index=False)
    print(f"Berhasil mengunggah {len(df)} baris data ke tabel 'bronze_harga_pasar'.")

if __name__ == "__main__":
    try:
        df_data = fetch_api_data()
        load_to_bronze(df_data)
        print("Pipeline Ingestion Hari 2 BERHASIL!")
    except Exception as e:
        print(f"Terjadi error: {e}")
        raise