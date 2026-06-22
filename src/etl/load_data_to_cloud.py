import random
import pandas as pd
from faker import Faker
from datetime import datetime
from sqlalchemy import create_engine, text
import time

# ============ DATABASE CONNECTION ============
# !!! REPLACE THIS WITH YOUR ACTUAL ENDPOINT (without :5432) !!!
DB_ENDPOINT = "lending-analytics-db.cotq60e68s8c.us-east-1.rds.amazonaws.com"  # e.g., lending-analytics-db.xxxxxx.ca-central-1.rds.amazonaws.com
DB_NAME = "lendingdb"
DB_USER = "lending_admin"
DB_PASSWORD = "LendingSecurePass123!"

# Create SQLAlchemy connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ENDPOINT}:5432/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# ============ GENERATE DATA ============
fake = Faker(['en_CA'])
Faker.seed(42)
random.seed(42)

def generate_clients(n=1000):
    data = []
    provinces = ['ON', 'BC', 'AB', 'QC', 'MB', 'SK', 'NS', 'NB']
    segments = ['Retail', 'Premium', 'Commercial']
    for i in range(1, n + 1):
        data.append({
            'client_id': i,
            'full_name': fake.name(),
            'province': random.choice(provinces),
            'client_segment': random.choice(segments)
        })
    return pd.DataFrame(data)

def generate_loan_portfolio(clients_df, products_df, n=9000):
    data = []
    statuses = ['Current', '30 Days Past Due', '60 Days Past Due', '90+ Days Past Due', 'Default']
    status_weights = [0.80, 0.08, 0.05, 0.04, 0.03]
    
    for _ in range(n):
        client = clients_df.sample(1).iloc[0]
        product = products_df.sample(1).iloc[0]
        orig_date = fake.date_between(start_date='-5y', end_date='-1d')
        amount = round(random.uniform(10000, 850000), 2)
        rate = round(random.uniform(3.5, 12.5), 2)
        age_in_days = (datetime.now().date() - orig_date).days
        paydown_factor = min(1, age_in_days / 730)
        remaining = round(amount * (1 - (paydown_factor * 0.9)), 2)
        if remaining < 0: remaining = 0
        
        data.append({
            'client_id': client['client_id'],
            'product_id': product['product_id'],
            'origination_date': orig_date,
            'loan_amount': amount,
            'interest_rate': rate,
            'remaining_balance': remaining,
            'payment_status': random.choices(statuses, weights=status_weights, k=1)[0],
            'last_payment_date': fake.date_between(start_date=orig_date, end_date='today') if random.random() > 0.1 else None
        })
    return pd.DataFrame(data)

# ============ PUSH TO CLOUD ============
def create_tables(conn):
    with conn.connect() as connection:
        # Drop tables if they exist (clean slate)
        connection.execute(text("DROP TABLE IF EXISTS loan_portfolio CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS clients CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS loan_products CASCADE;"))
        
        # Create clients table
        connection.execute(text("""
            CREATE TABLE clients (
                client_id INTEGER PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                province VARCHAR(2) NOT NULL,
                client_segment VARCHAR(20) CHECK (client_segment IN ('Retail', 'Premium', 'Commercial'))
            );
        """))
        
        # Create products table
        connection.execute(text("""
            CREATE TABLE loan_products (
                product_id INTEGER PRIMARY KEY,
                product_name VARCHAR(50) NOT NULL,
                product_type VARCHAR(20) CHECK (product_type IN ('Mortgage', 'Personal Loan', 'Wealth Margin', 'Business Term'))
            );
        """))
        
        # Create portfolio table
        connection.execute(text("""
            CREATE TABLE loan_portfolio (
                loan_id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(client_id),
                product_id INTEGER REFERENCES loan_products(product_id),
                origination_date DATE NOT NULL,
                loan_amount DECIMAL(12,2) NOT NULL,
                interest_rate DECIMAL(5,2) NOT NULL,
                remaining_balance DECIMAL(12,2) NOT NULL,
                payment_status VARCHAR(20) CHECK (payment_status IN ('Current', '30 Days Past Due', '60 Days Past Due', '90+ Days Past Due', 'Default')),
                last_payment_date DATE
            );
        """))
        
        connection.commit()
    print("✅ Tables created successfully!")

def push_data_to_cloud():
    print("🔄 Connecting to AWS RDS...")
    
    try:
        # Create tables
        create_tables(engine)
        
        # Generate data
        print("📊 Generating data...")
        products = pd.DataFrame([
            {'product_id': 1, 'product_name': '5-Year Fixed Mortgage', 'product_type': 'Mortgage'},
            {'product_id': 2, 'product_name': 'Variable Open Mortgage', 'product_type': 'Mortgage'},
            {'product_id': 3, 'product_name': 'Unsecured Personal Loan', 'product_type': 'Personal Loan'},
            {'product_id': 4, 'product_name': 'Secured Wealth Margin', 'product_type': 'Wealth Margin'},
            {'product_id': 5, 'product_name': 'Business Term Loan', 'product_type': 'Business Term'}
        ])
        
        clients = generate_clients(1000)
        portfolio = generate_loan_portfolio(clients, products, 9000)
        
        # Push to database using SQLAlchemy
        print("☁️ Uploading clients...")
        clients.to_sql('clients', engine, if_exists='append', index=False)
        
        print("☁️ Uploading products...")
        products.to_sql('loan_products', engine, if_exists='append', index=False)
        
        print("☁️ Uploading portfolio... (this takes ~30 seconds)")
        portfolio.to_sql('loan_portfolio', engine, if_exists='append', index=False)
        
        print("🎉 SUCCESS! All data uploaded to AWS RDS!")
        print(f"   - {len(clients)} clients")
        print(f"   - {len(products)} products")
        print(f"   - {len(portfolio)} loan records")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    push_data_to_cloud()