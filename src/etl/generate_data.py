import random
import pandas as pd
from faker import Faker
from datetime import datetime

fake = Faker(['en_CA'])
Faker.seed(42)
random.seed(42)

def generate_clients(n=1000):
    data = []
    provinces = ['ON', 'BC', 'AB', 'QC', 'MB', 'SK', 'NS', 'NB']
    segments = ['Retail', 'Premium', 'Commercial']
    for _ in range(n):
        data.append({
            'full_name': fake.name(),
            'province': random.choice(provinces),
            'client_segment': random.choice(segments)
        })
    df = pd.DataFrame(data)
    df.insert(0, 'client_id', range(1, len(df) + 1))
    return df

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

if __name__ == "__main__":
    print("Generating fake banking data...")
    
    products = pd.DataFrame([
        {'product_name': '5-Year Fixed Mortgage', 'product_type': 'Mortgage'},
        {'product_name': 'Variable Open Mortgage', 'product_type': 'Mortgage'},
        {'product_name': 'Unsecured Personal Loan', 'product_type': 'Personal Loan'},
        {'product_name': 'Secured Wealth Margin', 'product_type': 'Wealth Margin'},
        {'product_name': 'Business Term Loan', 'product_type': 'Business Term'}
    ])
    products.insert(0, 'product_id', range(1, len(products) + 1))
    
    clients = generate_clients(1000)
    portfolio = generate_loan_portfolio(clients, products, 9000)
    
    clients.to_csv('data/clients_raw.csv', index=False)
    products.to_csv('data/products_raw.csv', index=False)
    portfolio.to_csv('data/portfolio_raw.csv', index=False)
    
    print(f"Generated {len(clients)} clients and {len(portfolio)} loan records.")
    print("Files saved in /data folder.")