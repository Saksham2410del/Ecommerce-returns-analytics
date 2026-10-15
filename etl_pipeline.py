import json
import sqlite3
import pandas as pd

def extract_data():
    with open('raw_data/raw_users.json', 'r') as f:
        raw_users = json.load(f)
        
    with open('raw_data/raw_events.json', 'r') as f:
        raw_events = json.load(f)
        
    return raw_users, raw_events

def transform_customers(raw_users):
    df = pd.DataFrame(raw_users)
    profile = pd.json_normalize(df['profile'])
    
    df = pd.concat([df.drop(columns=['profile']), profile], axis=1)
    df = df.rename(columns={'_id': 'customer_id'})
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    
    df = df[['customer_id', 'location', 'signup_date', 'status']]
    return df

def transform_transactions(raw_events):
    df = pd.DataFrame(raw_events)
    payload = pd.json_normalize(df['payload'])
    
    df = pd.concat([df.drop(columns=['payload']), payload], axis=1)
    df = df.rename(columns={'event_id': 'transaction_id', 'user_id': 'customer_id'})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    df['amount'] = df['amount'].fillna(0.0)
    df['refund_amount'] = df['refund_amount'].fillna(0.0)
    df['payment_method'] = df['payment_method'].fillna('N/A')
    df['reason'] = df['reason'].fillna('No Return')
    
    df = df[['transaction_id', 'event_type', 'timestamp', 'customer_id', 
             'product_category', 'amount', 'payment_method', 'refund_amount', 'reason']]
    return df

def load_to_csv(df_customers, df_transactions):
    df_customers.to_csv('cleaned_customers.csv', index=False)
    df_transactions.to_csv('cleaned_transactions.csv', index=False)

def load_to_sqlite(df_customers, df_transactions):
    conn = sqlite3.connect('ecommerce_data_warehouse.db')
    cursor = conn.cursor()
    
    df_customers.to_sql('customers', conn, if_exists='replace', index=False)
    df_transactions.to_sql('transactions', conn, if_exists='replace', index=False)
    
    cursor.execute("DROP VIEW IF EXISTS users;")
    cursor.execute("DROP VIEW IF EXISTS events;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("DROP TABLE IF EXISTS events;")
    
    cursor.execute("""
        CREATE VIEW users AS 
        SELECT customer_id AS _id, status, location, signup_date 
        FROM customers;
    """)
    cursor.execute("""
        CREATE VIEW events AS 
        SELECT transaction_id AS event_id, event_type, timestamp, customer_id AS user_id, 
               product_category, amount, payment_method, refund_amount, reason 
            FROM transactions;
    """)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    raw_users, raw_events = extract_data()
    clean_customers = transform_customers(raw_users)
    clean_transactions = transform_transactions(raw_events)
    load_to_csv(clean_customers, clean_transactions)
    load_to_sqlite(clean_customers, clean_transactions)
