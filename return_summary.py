# Makes the category summary used for reporting:
#
# - return_summary.csv  -> imported into the "Return Analytics" Google Sheet,
#                          which automation.gs reads to send the daily email
# - images/return_rate_by_category.png -> bar chart shown in the README
#
# Usage: python return_summary.py   (run etl_pipeline.py first)

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def build_summary():
    conn = sqlite3.connect('ecommerce_data_warehouse.db')
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()

    purchases = df[df['event_type'] == 'purchase']
    returns = df[df['event_type'] == 'return']

    summary = pd.DataFrame({
        'total_purchases': purchases.groupby('product_category').size(),
        'total_returns': returns.groupby('product_category').size(),
        'total_refund_inr': returns.groupby('product_category')['refund_amount'].sum().round(2),
    })

    summary['return_rate_pct'] = (summary['total_returns'] / summary['total_purchases'] * 100).round(2)
    summary['share_of_returns_pct'] = (summary['total_returns'] / len(returns) * 100).round(2)
    summary['share_of_refunds_pct'] = (summary['total_refund_inr'] / returns['refund_amount'].sum() * 100).round(2)

    summary = summary.sort_values('return_rate_pct', ascending=False)
    return summary.reset_index()


def plot_return_rates(summary):
    # Apparel in red, everything else in blue
    colors = []
    for category in summary['product_category']:
        if category == 'Apparel':
            colors.append('#c0392b')
        else:
            colors.append('#2980b9')

    plt.figure(figsize=(7, 4.5))
    plt.bar(summary['product_category'], summary['return_rate_pct'], color=colors, width=0.5)
    plt.axhline(y=5, color='green', linestyle='--', label='Normal baseline (~5%)')

    for i, rate in enumerate(summary['return_rate_pct']):
        plt.text(i, rate + 0.7, f"{rate:.1f}%", ha='center', fontsize=9)

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
