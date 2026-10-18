# ETL pipeline: raw JSON logs -> cleaned tables -> SQLite database
#
# raw_users.json   -> customers table
# raw_events.json  -> transactions table (purchases and returns)
#
# Usage: python etl_pipeline.py

import json
import sqlite3
import pandas as pd


def extract_data():
    with open('raw_data/raw_users.json') as f:
        raw_users = json.load(f)

    with open('raw_data/raw_events.json') as f:
        raw_events = json.load(f)

    print("Users loaded: ", len(raw_users))
    print("Events loaded:", len(raw_events))
    print("Total records:", len(raw_users) + len(raw_events))
    return raw_users, raw_events


def transform_customers(raw_users):
    df = pd.DataFrame(raw_users)

    # location and signup_date are nested inside "profile", so pull them out
    profile = pd.json_normalize(df['profile'])
    df = pd.concat([df.drop(columns=['profile']), profile], axis=1)

    df = df.rename(columns={'_id': 'customer_id'})
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df = df.drop_duplicates(subset='customer_id')

    return df[['customer_id', 'location', 'signup_date', 'status']]


def transform_transactions(raw_events):
    df = pd.DataFrame(raw_events)

    # product details are nested inside "payload"
    payload = pd.json_normalize(df['payload'])
    df = pd.concat([df.drop(columns=['payload']), payload], axis=1)

    df = df.rename(columns={'event_id': 'transaction_id', 'user_id': 'customer_id'})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.drop_duplicates(subset='transaction_id')

    # purchases have no refund and returns have no purchase amount, so fill the blanks
    df['amount'] = df['amount'].fillna(0)
    df['refund_amount'] = df['refund_amount'].fillna(0)
    df['payment_method'] = df['payment_method'].fillna('N/A')
    df['reason'] = df['reason'].fillna('No Return')

    return df[['transaction_id', 'event_type', 'timestamp', 'customer_id',
               'product_category', 'amount', 'payment_method', 'refund_amount', 'reason']]


def check_data(customers, transactions):
    # keep only transactions from known customers with no negative amounts
    before = len(transactions)
    transactions = transactions[transactions['customer_id'].isin(customers['customer_id'])]
    transactions = transactions[transactions['amount'] >= 0]
    transactions = transactions[transactions['refund_amount'] >= 0]

    print("Bad rows removed:", before - len(transactions))
    return transactions


def load_data(customers, transactions):
    # CSV copies are handy for opening in Excel
    customers.to_csv('cleaned_customers.csv', index=False)
    transactions.to_csv('cleaned_transactions.csv', index=False)

    conn = sqlite3.connect('ecommerce_data_warehouse.db')
    customers.to_sql('customers', conn, if_exists='replace', index=False)
    transactions.to_sql('transactions', conn, if_exists='replace', index=False)
    conn.close()

    print("Saved", len(customers), "customers and", len(transactions), "transactions to SQLite")


if __name__ == '__main__':
    raw_users, raw_events = extract_data()
    customers = transform_customers(raw_users)
    transactions = transform_transactions(raw_events)
    transactions = check_data(customers, transactions)
    load_data(customers, transactions)
