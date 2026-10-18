# ETL pipeline: raw JSON logs -> cleaned tables -> SQLite database
#
# raw_users.json   -> customers table
# raw_events.json  -> transactions table (purchases and returns)
#
# Usage: python etl_pipeline.py

import json
import sqlite3
import pandas as pd

DB_PATH = 'ecommerce_data_warehouse.db'


def extract_data():
    with open('raw_data/raw_users.json', 'r') as f:
        raw_users = json.load(f)

    with open('raw_data/raw_events.json', 'r') as f:
        raw_events = json.load(f)

    print(f"Loaded {len(raw_users):,} users and {len(raw_events):,} events "
          f"({len(raw_users) + len(raw_events):,} raw records)")
    return raw_users, raw_events


def transform_customers(raw_users):
    df = pd.DataFrame(raw_users)

    # location and signup_date are nested inside a "profile" object
    profile = pd.json_normalize(df['profile'])
    df = pd.concat([df.drop(columns=['profile']), profile], axis=1)

    df = df.rename(columns={'_id': 'customer_id'})
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df = df.drop_duplicates(subset='customer_id')

    return df[['customer_id', 'location', 'signup_date', 'status']]


def transform_transactions(raw_events):
    df = pd.DataFrame(raw_events)

    # Product details sit inside "payload", and the keys are different for
    # purchases (amount, payment_method) and returns (refund_amount, reason)
    payload = pd.json_normalize(df['payload'])
    df = pd.concat([df.drop(columns=['payload']), payload], axis=1)

    df = df.rename(columns={'event_id': 'transaction_id', 'user_id': 'customer_id'})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.drop_duplicates(subset='transaction_id')

    # A purchase has no refund and a return has no purchase amount,
    # so fill those gaps instead of leaving NaN in the database
    df['amount'] = df['amount'].fillna(0.0)
    df['refund_amount'] = df['refund_amount'].fillna(0.0)
    df['payment_method'] = df['payment_method'].fillna('N/A')
    df['reason'] = df['reason'].fillna('No Return')

    return df[['transaction_id', 'event_type', 'timestamp', 'customer_id',
               'product_category', 'amount', 'payment_method', 'refund_amount', 'reason']]


def check_data(customers, transactions):
    # Basic sanity checks before loading, so bad data doesn't reach the analysis
    unknown = ~transactions['customer_id'].isin(customers['customer_id'])
    negative = (transactions['amount'] < 0) | (transactions['refund_amount'] < 0)

    print(f"Transactions with unknown customer: {unknown.sum()}")
    print(f"Negative amounts or refunds:        {negative.sum()}")

    if unknown.sum() or negative.sum():
        print("Dropping the bad rows")
        transactions = transactions[~unknown & ~negative]

    return transactions


def load_to_csv(df_customers, df_transactions):
    df_customers.to_csv('cleaned_customers.csv', index=False)
    df_transactions.to_csv('cleaned_transactions.csv', index=False)


def load_to_sqlite(df_customers, df_transactions):
    conn = sqlite3.connect(DB_PATH)
    df_customers.to_sql('customers', conn, if_exists='replace', index=False)
    df_transactions.to_sql('transactions', conn, if_exists='replace', index=False)
    conn.close()

    print(f"Saved {len(df_customers):,} customers and {len(df_transactions):,} "
          f"transactions to {DB_PATH}")


if __name__ == '__main__':
    raw_users, raw_events = extract_data()
    clean_customers = transform_customers(raw_users)
    clean_transactions = transform_transactions(raw_events)
    clean_transactions = check_data(clean_customers, clean_transactions)
    load_to_csv(clean_customers, clean_transactions)
    load_to_sqlite(clean_customers, clean_transactions)
