# "Ask your data" assistant: type a question in plain English, get the answer
# from the SQLite database.
#
#   question -> Gemini writes a SQL query -> safety check -> run on SQLite -> answer
#
# Only the table structure and the question are sent to Gemini.
# The query itself runs locally, so the customer data never leaves the machine.
#
# Needs a free Gemini API key from https://aistudio.google.com in a .env file:
#   GEMINI_API_KEY=your_key_here
#
# Usage: python ask_data.py   (run etl_pipeline.py first)

import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.6-flash"
DB_PATH = 'ecommerce_data_warehouse.db'

# The model needs to know the tables, the columns and what the values look like
SCHEMA = """
Table customers:
  customer_id TEXT      e.g. 'U00001'
  location TEXT         'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Pune' or 'Unknown'
  signup_date TEXT      'YYYY-MM-DD HH:MM:SS'
  status TEXT           'active'

Table transactions:
  transaction_id TEXT   e.g. 'EV000001'
  event_type TEXT       'purchase' or 'return'
  timestamp TEXT        'YYYY-MM-DD HH:MM:SS'
  customer_id TEXT      links to customers.customer_id
  product_category TEXT 'Apparel', 'Electronics', 'Home' or 'Beauty'
  amount REAL           purchase amount in rupees, 0 for returns
  payment_method TEXT   'UPI', 'Credit Card', 'Debit Card' or 'Unknown' for purchases, 'N/A' for returns
  refund_amount REAL    refund in rupees, 0 for purchases
  reason TEXT           'Size Issue', 'Defective' or 'Changed Mind' for returns, 'No Return' for purchases

Return rate of a category = number of returns / number of purchases * 100
"""


def write_sql(question):
    prompt = f"""You write SQLite queries for an e-commerce returns database.

{SCHEMA}
Write one SQLite SELECT query that answers the question below.
- Return only the columns and rows needed to answer it.
- Round money and percentages to 2 decimal places.
- Reply with the SQL only, no explanation.

Question: {question}"""

    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    response = client.models.generate_content(model=MODEL, contents=prompt)

    # the model sometimes wraps the query in ```sql ... ```
    sql = response.text.strip()
    sql = sql.replace('```sql', '').replace('```', '').strip()
    return sql


def is_safe(sql):
    # Only allow a single SELECT query, nothing that changes the data
    sql = sql.strip().rstrip(';').lower()
    if not (sql.startswith('select') or sql.startswith('with')):
        return False
    if ';' in sql:
        return False
    for word in ['insert', 'update', 'delete', 'drop', 'alter', 'create', 'attach', 'pragma']:
        if word in sql.split():
            return False
    return True


def run_sql(sql):
    # mode=ro opens the database read-only, a second layer of safety
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    result = pd.read_sql_query(sql, conn)
    conn.close()
    return result


def ask(question):
    sql = write_sql(question)
    if not is_safe(sql):
        raise ValueError(f"Blocked a query that is not a plain SELECT:\n{sql}")
    return sql, run_sql(sql)


if __name__ == '__main__':
    print("Ask a question about the returns data (or press Enter to quit)")
    while True:
        question = input("\n> ")
        if question == '':
            break
        try:
            sql, result = ask(question)
            print("\nSQL used:\n" + sql + "\n")
            print(result.to_string(index=False))
        except Exception as e:
            print("Error:", e)
