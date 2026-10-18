# E-Commerce Returns Analytics: Business Strategy Report (Simulated Dataset)

**To:** VP of Product, Director of Marketing  
**From:** Data Analytics Team  
**Date:** December 2025  
**Subject:** Root Cause Analysis of Return Rates & Profit Margin Erosion  

---

## 1. Executive Summary
We analyzed a simulated dataset of **10,900+ raw JSON transaction records**, covering **2,000 customer profiles** and **8,905 orders and returns** stored in a SQLite relational database (`customers` and `transactions` tables).

**Key Finding:** Return rates are heavily skewed toward a single category. While Electronics, Home, and Beauty maintain healthy baseline return rates around ~5%, **Apparel has an abnormal return rate of 31.7%**.

---

## 2. Category Performance & Financial Impact

Using SQL queries on the SQLite database, we analyzed return rates and refund liabilities across all four product categories:

| Product Category | Purchases | Returns | Return Rate (%) | Total Refunds (INR) | Share of Total Refunds | Return Reasons |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Apparel** | 1,898 | 601 | **31.7%** | **Rs. 16.63 Lakh** | **66.7%** | **100% Size Issue** |
| **Electronics** | 2,053 | 105 | 5.1% | Rs. 2.84 Lakh | 11.4% | Defective (53%), Changed Mind (47%) |
| **Home** | 1,989 | 100 | 5.0% | Rs. 2.85 Lakh | 11.4% | Defective (52%), Changed Mind (48%) |
| **Beauty** | 2,060 | 99 | 4.8% | Rs. 2.63 Lakh | 10.5% | Changed Mind (52%), Defective (48%) |
| **Total / Avg** | **8,000** | **905** | **11.3%** | **Rs. 24.94 Lakh** | **100%** | |

### Key Takeaways:
1. **Apparel drives 66% of all returned units** (601 out of 905 total returns).
2. **Apparel accounts for Rs. 16.6 Lakh out of Rs. 24.9 Lakh** in total refund liability.
3. Every single Apparel return (**100%**) was linked to **"Size Issue"**, indicating severe inconsistency in sizing guides or vendor variations.

---

## 3. Modeled Cost Savings Scenarios

Factoring in product refunds and an estimated Rs. 200 reverse logistics handling cost per returned item, we modeled the potential financial recovery from improving sizing guides:

| Scenario | Apparel Return Rate | Projected Returns | Total Drain (Refunds + Handling) | Modeled Savings |
| :--- | :--- | :--- | :--- | :--- |
| **Current Baseline** | 31.7% | 601 | Rs. 17.84 Lakh | **Baseline (Rs. 0)** |
| **Scenario 1: Updated Size Guides** | 20.0% | 379 | Rs. 11.25 Lakh | **Rs. 6.6 Lakh modeled savings** |
| **Scenario 2: Interactive Sizing Tool** | 10.0% | 189 | Rs. 5.61 Lakh | **Rs. 12.2 Lakh modeled savings** |
| **Scenario 3: 5% Industry Benchmark** | 5.0% | 94 | Rs. 2.79 Lakh | **Rs. 15.0 Lakh modeled savings** |

*Note: These figures are modeled estimates based on the 8,905 dataset transactions.*

---

## 4. Strategic Recommendations

### For the Marketing Team:
- **Immediate Action:** Review paid advertising on high-return Apparel SKUs. Nearly 1 in 3 Apparel orders comes back, so a large part of the ad spend on these products is likely wasted. (The dataset has no ad spend figures, so this needs to be checked against campaign data.)
- **Automation:** The daily Google Apps Script email (`automation.gs`) flags any category whose return rate goes above 15%, so campaigns can be reviewed early.

### For the Product Team:
- **Immediate Action:** Audit product page sizing guides for all Apparel items and add explicit chest/waist measurements.
- **Medium-term:** Implement a "True to Size" fit recommender to target the 10% return rate benchmark (modeling over Rs. 12 Lakhs in recovered margin).
