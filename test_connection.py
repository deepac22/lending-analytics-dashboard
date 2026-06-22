import psycopg2
import os

# Replace these with YOUR actual values from terraform output
DB_ENDPOINT = "lending-analytics-db.cotq60e68s8c.us-east-1.rds.amazonaws.com"  # e.g., lending-analytics-db.xxxxxx.ca-central-1.rds.amazonaws.com
DB_NAME = "lendingdb"
DB_USER = "lending_admin"
DB_PASSWORD = "LendingSecurePass123!"

try:
    conn = psycopg2.connect(
        host=DB_ENDPOINT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=5432
    )
    print("✅ SUCCESS! Connected to AWS RDS PostgreSQL!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"📦 PostgreSQL Version: {version[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")