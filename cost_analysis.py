# How much money would we save if fewer Apparel items were returned?
#
# Cost of a return = refund + Rs. 200 for return shipping and handling (assumed)
#
# Usage: python cost_analysis.py   (run etl_pipeline.py first)

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

HANDLING_COST = 200
TARGET_RATES = [0.20, 0.10, 0.05]   # 5% is what the other categories already have


def calculate_savings():
    conn = sqlite3.connect('ecommerce_data_warehouse.db')
    df = pd.read_sql_query("SELECT * FROM transactions WHERE product_category = 'Apparel'", conn)
    conn.close()

    orders = len(df[df['event_type'] == 'purchase'])
    returns = df[df['event_type'] == 'return']

    avg_refund = returns['refund_amount'].mean()
    current_cost = returns['refund_amount'].sum() + len(returns) * HANDLING_COST

    print("Apparel orders: ", orders)
    print("Apparel returns:", len(returns), f"({len(returns) / orders:.1%})")
    print(f"Current cost of returns: Rs. {current_cost / 100000:.2f} lakh\n")

    results = []
    for rate in TARGET_RATES:
        new_returns = int(orders * rate)
        new_cost = new_returns * (avg_refund + HANDLING_COST)
        savings = current_cost - new_cost

        results.append({
            'Target': f"{rate:.0%} return rate",
            'Projected Returns': new_returns,
            'Cost (Lakhs)': round(new_cost / 100000, 2),
            'Savings (Lakhs)': round(savings / 100000, 2),
        })

    results = pd.DataFrame(results)
    print(results.to_string(index=False))

    # bar chart of the savings
    plt.figure(figsize=(7, 4.5))
    plt.bar(results['Target'], results['Savings (Lakhs)'], color='#2b5c8f', width=0.45)
    for i, value in enumerate(results['Savings (Lakhs)']):
        plt.text(i, value + 0.4, f"Rs. {value:.1f}L", ha='center', fontsize=9)
    plt.title("Savings from Reducing Apparel Returns")
    plt.ylabel("Savings (Rs. lakh)")
    plt.ylim(0, 18)
    plt.tight_layout()
    plt.savefig('projected_savings.png')
    plt.close()

    return results


if __name__ == '__main__':
    calculate_savings()
