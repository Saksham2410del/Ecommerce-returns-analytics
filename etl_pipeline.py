# ETL pipeline: raw JSON logs -> cleaned tables -> SQLite database
#
# raw_users.json   -> customers table
# raw_events.json  -> transactions table (purchases and returns)
#
# The raw logs have the usual problems: duplicate records, test accounts,
# inconsistent spelling, three different date formats, amounts saved as text,
# negative refunds and blank values. Each step below fixes one of them and
# prints how many rows it touched.
#
# Usage: python etl_pipeline.py

import json
import sqlite3
import pandas as pd


def parse_dates(column):
    # Dates come as "2024-05-13", "2024-05-13T00:00:00" or "13/05/2024"
    iso_dates = pd.to_datetime(column, format='ISO8601', errors='coerce')
    dmy_dates = pd.to_datetime(column, format='%d/%m/%Y', errors='coerce')
    return iso_dates.fillna(dmy_dates)


def clean_customers(raw_users):
    df = pd.json_normalize(raw_users)
    df = df.rename(columns={
        '_id': 'customer_id',
        'profile.location': 'location',
        'profile.signup_date': 'signup_date',
    })
    print("Raw customer records:", len(df))

    # 1. Same customer saved more than once
    before = len(df)
    df = df.drop_duplicates(subset='customer_id')
    print("  Duplicate customers removed:", before - len(df))

    # 2. Internal test accounts are not real customers
    df['status'] = df['status'].str.strip().str.lower()
    is_test = df['status'] == 'test'
    print("  Test accounts removed:", is_test.sum())
    df = df[~is_test]

    # 3. City names: " mumbai", "PUNE", "Bengaluru" -> "Mumbai", "Pune", "Bangalore"
    df['location'] = df['location'].str.strip().str.title()
    df['location'] = df['location'].replace('Bengaluru', 'Bangalore')

    missing = df['location'].isna() | (df['location'] == '')
    print("  Missing city filled as 'Unknown':", missing.sum())
    df.loc[missing, 'location'] = 'Unknown'

    # 4. Dates in different formats
    df['signup_date'] = parse_dates(df['signup_date'])

    df = df.sort_values('customer_id')
    print("Clean customers:", len(df))
    return df[['customer_id', 'location', 'signup_date', 'status']]


def clean_transactions(raw_events, customers):
    df = pd.json_normalize(raw_events)
    df = df.rename(columns={
        'event_id': 'transaction_id',
        'user_id': 'customer_id',
        'payload.product_category': 'product_category',
        'payload.amount': 'amount',
        'payload.payment_method': 'payment_method',
        'payload.refund_amount': 'refund_amount',
        'payload.reason': 'reason',
    })
    print("\nRaw transaction records:", len(df))

    # 1. Same event logged twice
    before = len(df)
    df = df.drop_duplicates(subset='transaction_id')
    print("  Duplicate transactions removed:", before - len(df))

    # 2. Events from test accounts or customers we don't know
    known = df['customer_id'].isin(customers['customer_id'])
    print("  Test / unknown customer events removed:", (~known).sum())
    df = df[known]

    # 3. Rows with no product category can't be analysed
    missing_category = df['product_category'].isna()
    print("  Rows with no product category removed:", missing_category.sum())
    df = df[~missing_category].copy()

    # 4. Text cleanup: "apparel ", "APPAREL" -> "Apparel", "SIZE_ISSUE" -> "Size Issue"
    df['event_type'] = df['event_type'].str.strip().str.lower()
    df['product_category'] = df['product_category'].str.strip().str.title()
    df['reason'] = df['reason'].str.strip().str.replace('_', ' ').str.title()

    # 5. Some amounts were saved as text like "Rs. 4,284.59"
    is_text = df['amount'].apply(type) == str
    print("  Amounts stored as text converted:", is_text.sum())
    df['amount'] = df['amount'].astype(str).str.replace('Rs.', '').str.replace(',', '').str.strip()
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

    # 6. A refund can't be negative, the sign was flipped in some records
    negative = df['refund_amount'] < 0
    print("  Negative refunds fixed:", negative.sum())
    df['refund_amount'] = df['refund_amount'].abs().fillna(0)

    # 7. Dates in different formats
    df['timestamp'] = parse_dates(df['timestamp'])

    # 8. Blank payment method on a purchase -> "Unknown".
    #    Returns don't have a payment method at all -> "N/A"
    df.loc[df['payment_method'] == '', 'payment_method'] = None
    is_purchase = df['event_type'] == 'purchase'
    blank_payment = is_purchase & df['payment_method'].isna()
    print("  Blank payment methods filled as 'Unknown':", blank_payment.sum())
    df.loc[blank_payment, 'payment_method'] = 'Unknown'
    df['payment_method'] = df['payment_method'].fillna('N/A')
    df['reason'] = df['reason'].fillna('No Return')

    df = df.sort_values('transaction_id')
    print("Clean transactions:", len(df))
    return df[['transaction_id', 'event_type', 'timestamp', 'customer_id',
               'product_category', 'amount', 'payment_method', 'refund_amount', 'reason']]


def load_data(customers, transactions):
    # CSV copies are used by Power BI and are handy for opening in Excel
    customers.to_csv('cleaned_customers.csv', index=False)
    transactions.to_csv('cleaned_transactions.csv', index=False)

    conn = sqlite3.connect('ecommerce_data_warehouse.db')
    customers.to_sql('customers', conn, if_exists='replace', index=False)
    transactions.to_sql('transactions', conn, if_exists='replace', index=False)
    conn.close()

    print("\nSaved to ecommerce_data_warehouse.db and cleaned_*.csv")


def main():
    with open('raw_data/raw_users.json') as f:
        raw_users = json.load(f)
    with open('raw_data/raw_events.json') as f:
        raw_events = json.load(f)

    customers = clean_customers(raw_users)
    transactions = clean_transactions(raw_events, customers)
    load_data(customers, transactions)


if __name__ == '__main__':
    main()
