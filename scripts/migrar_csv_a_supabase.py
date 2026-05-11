import os
import sys
import csv
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Configuración
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "api", "data")
ENV_PATH = os.path.join(PROJECT_ROOT, "server", ".env")

load_dotenv(ENV_PATH)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def nullify(val):
    return None if not val or val.strip() == "" else val.strip()

def nullify_float(val):
    val = nullify(val)
    return float(val) if val is not None else None

def nullify_int(val):
    val = nullify(val)
    return int(float(val)) if val is not None else None

def importar_ordenes(conn):
    print("Migrando olist_orders...")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS olist_orders (
            order_id VARCHAR PRIMARY KEY,
            customer_id VARCHAR,
            order_status VARCHAR,
            order_purchase_timestamp TIMESTAMP,
            order_approved_at TIMESTAMP,
            order_delivered_carrier_date TIMESTAMP,
            order_delivered_customer_date TIMESTAMP,
            order_estimated_delivery_date TIMESTAMP
        );
        TRUNCATE TABLE olist_orders;
    """)
    
    filepath = os.path.join(DATA_DIR, "olist_orders_dataset.csv")
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader) # skip header
        data = []
        for row in reader:
            data.append((
                nullify(row[0]), nullify(row[1]), nullify(row[2]),
                nullify(row[3]), nullify(row[4]), nullify(row[5]),
                nullify(row[6]), nullify(row[7])
            ))
            
    execute_values(cur, "INSERT INTO olist_orders VALUES %s", data, page_size=5000)
    conn.commit()
    print(f"[OK] olist_orders importado ({len(data)} filas)")

def importar_productos(conn):
    print("Migrando olist_products...")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS olist_products (
            product_id VARCHAR PRIMARY KEY,
            product_category_name VARCHAR,
            product_name_lenght INT,
            product_description_lenght INT,
            product_photos_qty INT,
            product_weight_g INT,
            product_length_cm INT,
            product_height_cm INT,
            product_width_cm INT
        );
        TRUNCATE TABLE olist_products;
    """)
    
    filepath = os.path.join(DATA_DIR, "olist_products_dataset.csv")
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        data = []
        for row in reader:
            data.append((
                nullify(row[0]), nullify(row[1]),
                nullify_int(row[2]), nullify_int(row[3]), nullify_int(row[4]),
                nullify_int(row[5]), nullify_int(row[6]), nullify_int(row[7]), nullify_int(row[8])
            ))
            
    execute_values(cur, "INSERT INTO olist_products VALUES %s", data, page_size=5000)
    conn.commit()
    print(f"[OK] olist_products importado ({len(data)} filas)")

def importar_items(conn):
    print("Migrando olist_order_items...")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS olist_order_items (
            order_id VARCHAR,
            order_item_id INT,
            product_id VARCHAR,
            seller_id VARCHAR,
            shipping_limit_date TIMESTAMP,
            price FLOAT,
            freight_value FLOAT
        );
        TRUNCATE TABLE olist_order_items;
    """)
    
    filepath = os.path.join(DATA_DIR, "olist_order_items_dataset.csv")
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        data = []
        for row in reader:
            data.append((
                nullify(row[0]), nullify_int(row[1]), nullify(row[2]),
                nullify(row[3]), nullify(row[4]),
                nullify_float(row[5]), nullify_float(row[6])
            ))
            
    execute_values(cur, "INSERT INTO olist_order_items VALUES %s", data, page_size=5000)
    conn.commit()
    print(f"[OK] olist_order_items importado ({len(data)} filas)")

def importar_geo(conn):
    print("Migrando olist_geolocation (esto puede tardar un minuto)...")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS olist_geolocation (
            geolocation_zip_code_prefix VARCHAR,
            geolocation_lat FLOAT,
            geolocation_lng FLOAT,
            geolocation_city VARCHAR,
            geolocation_state VARCHAR
        );
        TRUNCATE TABLE olist_geolocation;
    """)
    
    filepath = os.path.join(DATA_DIR, "olist_geolocation_dataset.csv")
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        data = []
        for row in reader:
            data.append((
                nullify(row[0]), nullify_float(row[1]), nullify_float(row[2]),
                nullify(row[3]), nullify(row[4])
            ))
            
    execute_values(cur, "INSERT INTO olist_geolocation VALUES %s", data, page_size=10000)
    conn.commit()
    print(f"[OK] olist_geolocation importado ({len(data)} filas)")

def importar_traducciones(conn):
    print("Migrando product_category_name_translation...")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_category_translation (
            product_category_name VARCHAR PRIMARY KEY,
            product_category_name_english VARCHAR
        );
        TRUNCATE TABLE product_category_translation;
    """)
    
    filepath = os.path.join(DATA_DIR, "product_category_name_translation.csv")
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)
        data = []
        for row in reader:
            data.append((nullify(row[0]), nullify(row[1])))
            
    execute_values(cur, "INSERT INTO product_category_translation VALUES %s", data)
    conn.commit()
    print(f"[OK] product_category_translation importado ({len(data)} filas)")

def main():
    print("=" * 60)
    print(" Migrador de CSV a PostgreSQL (Supabase)")
    print("=" * 60)
    try:
        conn = get_connection()
        importar_ordenes(conn)
        importar_productos(conn)
        importar_items(conn)
        importar_geo(conn)
        importar_traducciones(conn)
        conn.close()
        print("\n[INFO] Todos los datos han sido migrados exitosamente a Supabase!")
        print("Ya puedes desplegar a Vercel tranquilamente. La API ahora consultara la base de datos.")
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {e}")

if __name__ == "__main__":
    main()
