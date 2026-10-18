# Builds the category-wise return summary.
#
# - return_summary.csv  -> imported into the "Return Analytics" Google Sheet,
#                          which automation.gs reads to send the daily email
# - images/return_rate_by_category.png -> bar chart used in the README
#
# Usage: python return_summary.py   (run etl_pipeline.py first)

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

QUERY = '''
SELECT
    product_category,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS total_purchases,
    SUM(CASE WHEN event_type = 'return' THEN 1 ELSE 0 END) AS total_returns,
    ROUND(SUM(refund_amount), 2) AS total_refund_inr
FROM transactions
GROUP BY product_category
'''


def build_summary():
    conn = sqlite3.connect('ecommerce_data_warehouse.db')
    df = pd.read_sql_query(QUERY, conn)
    conn.close()

    df['return_rate_pct'] = (df['total_returns'] / df['total_purchases'] * 100).round(2)
    df['share_of_returns_pct'] = (df['total_returns'] / df['total_returns'].sum() * 100).round(2)
    df['share_of_refunds_pct'] = (df['total_refund_inr'] / df['total_refund_inr'].sum() * 100).round(2)
    return df.sort_values('return_rate_pct', ascending=False)


def plot_return_rates(df):
    colors = ['#c0392b' if cat == 'Apparel' else '#2980b9' for cat in df['product_category']]

    plt.figure(figsize=(7, 4.5))
    bars = plt.bar(df['product_category'], df['return_rate_pct'], color=colors, width=0.5)
    plt.axhline(y=5.0, color='green', linestyle='--', linewidth=1.2, label='Normal baseline (~5%)')

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 0.7, f"{height:.1f}%", ha='center', fontsize=9)

    plt.title('Return Rate by Product Category')
    plt.ylabel('Return Rate (%)')
    plt.ylim(0, 38)
    plt.legend()
    plt.tight_layout()

    os.makedirs('images', exist_ok=True)
    plt.savefig('images/return_rate_by_category.png', dpi=120)
    plt.close()


if __name__ == '__main__':
    summary = build_summary()
    summary.to_csv('return_summary.csv', index=False)
    plot_return_rates(summary)
    print(summary.to_string(index=False))
