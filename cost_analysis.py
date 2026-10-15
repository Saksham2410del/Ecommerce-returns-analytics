import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def calculate_savings():
    conn = sqlite3.connect('ecommerce_data_warehouse.db')
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()

    apparel_orders = df[(df['product_category'] == 'Apparel') & (df['event_type'] == 'purchase')]
    apparel_returns = df[(df['product_category'] == 'Apparel') & (df['event_type'] == 'return')]

    total_orders = len(apparel_orders)
    total_returns = len(apparel_returns)
    current_return_rate = total_returns / total_orders
    total_refunds = apparel_returns['refund_amount'].sum()
    avg_refund = total_refunds / total_returns

    shipping_cost = 200.0
    current_loss = total_refunds + (total_returns * shipping_cost)

    targets = [
        {"label": "20% Return Rate", "rate": 0.20},
        {"label": "10% Return Rate", "rate": 0.10},
        {"label": "5% Return Rate (Baseline)", "rate": 0.05}
    ]

    savings_list = []
    for t in targets:
        proj_returns = int(total_orders * t['rate'])
        proj_loss = (proj_returns * avg_refund) + (proj_returns * shipping_cost)
        savings = current_loss - proj_loss
        savings_lakhs = savings / 100000

        savings_list.append({
            "Target": t['label'],
            "Projected Returns": proj_returns,
            "Total Loss (Rs)": round(proj_loss, 2),
            "Savings (Lakhs)": round(savings_lakhs, 2)
        })

    savings_df = pd.DataFrame(savings_list)

    plt.figure(figsize=(7, 4.5))
    bars = plt.bar(savings_df['Target'], savings_df['Savings (Lakhs)'], color='#2b5c8f', width=0.45)
    plt.title("Estimated Cost Savings from Reducing Apparel Returns", fontsize=11)
    plt.ylabel("Savings in Lakhs (INR)", fontsize=10)
    plt.ylim(0, 18)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.4, f"Rs. {height:.1f}L", ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig('projected_savings.png')
    plt.close()
    return savings_df

if __name__ == '__main__':
    calculate_savings()
