import json
import pandas as pd
from pymongo import MongoClient

def extract_data():
    # Load raw JSON data
    with open('raw_data/raw_users.json', 'r') as f:
        raw_users = json.load(f)
        
    with open('raw_data/raw_events.json', 'r') as f:
        raw_events = json.load(f)
        
    return raw_users, raw_events

def transform_users(raw_users):
    # Process user profiles
    df_users = pd.DataFrame(raw_users)
    profile_df = pd.json_normalize(df_users['profile'])
    
    df_users = pd.concat([df_users.drop(['profile'], axis=1), profile_df], axis=1)
    df_users['signup_date'] = pd.to_datetime(df_users['signup_date'])
    
    return df_users

def transform_events(raw_events):
    # Process event data
    df_events = pd.DataFrame(raw_events)
    
    payload_df = pd.json_normalize(df_events['payload'])
    df_events = pd.concat([df_events.drop(['payload'], axis=1), payload_df], axis=1)
    
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'])
    
    # Fill missing values for optional fields
    df_events['refund_amount'] = df_events['refund_amount'].fillna(0)
    df_events['payment_method'] = df_events['payment_method'].fillna('N/A')
    df_events['reason'] = df_events['reason'].fillna('No Return')
    
    return df_events

def load_to_csv(df_users, df_events):
    df_users.to_csv('cleaned_users.csv', index=False)
    df_events.to_csv('cleaned_events.csv', index=False)
    print("Successfully saved cleaned data to CSV files.")

def load_to_mongodb(df_users, df_events):
    users_dict = df_users.to_dict("records")
    events_dict = df_events.to_dict("records")
    
    # Connection to MongoDB
    # Note: Replace 'your_connection_string' with your actual MongoDB Atlas URL
    connection_string = "mongodb://localhost:27017/"
    
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=2000)
        db = client['ecommerce_db']
        
        # Clear old data before inserting new data
        db.users.drop()
        db.events.drop()
        
        # Insert data into MongoDB collections
        db.users.insert_many(users_dict)
        db.events.insert_many(events_dict)
        print("Successfully loaded data into MongoDB!")
        
    except Exception as e:
        print("MongoDB is not running locally or connection failed.")
        print("Data is still saved in CSV format for analysis.")

import sqlite3

def load_to_sql(df_users, df_events):
    conn = sqlite3.connect('ecommerce_data_warehouse.db')
    df_users.to_sql('users', conn, if_exists='replace', index=False)
    df_events.to_sql('events', conn, if_exists='replace', index=False)
    conn.close()
    print("Successfully loaded clean data into Relational SQL Database (ecommerce_data_warehouse.db)")

if __name__ == "__main__":
    print("Starting ETL Pipeline...")
    
    users_raw, events_raw = extract_data()
    
    clean_users = transform_users(users_raw)
    clean_events = transform_events(events_raw)
    
    load_to_csv(clean_users, clean_events)
    load_to_sql(clean_users, clean_events)
    load_to_mongodb(clean_users, clean_events)
    
    print("ETL Pipeline completed successfully.")
