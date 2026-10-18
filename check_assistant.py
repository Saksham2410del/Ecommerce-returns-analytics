# How often does the assistant get the right answer?
#
# Each test question comes with a SQL query I wrote by hand. Both queries are
# run, and the assistant passes if the main value of the correct answer
# (first row, first column) shows up in the first row of its answer.
#
# Usage: python check_assistant.py   (needs GEMINI_API_KEY in .env)

from ask_data import ask, run_sql

TESTS = [
    ("How many customers are there?",
     "SELECT COUNT(*) FROM customers"),

    ("How many items were returned in total?",
     "SELECT COUNT(*) FROM transactions WHERE event_type = 'return'"),

    ("What is the return rate of Apparel?",
     """SELECT ROUND(SUM(CASE WHEN event_type = 'return' THEN 1 ELSE 0 END) * 100.0
               / SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END), 2)
        FROM transactions WHERE product_category = 'Apparel'"""),

    ("Which product category has the highest return rate?",
     """SELECT product_category FROM transactions GROUP BY product_category
        ORDER BY SUM(CASE WHEN event_type = 'return' THEN 1 ELSE 0 END) * 1.0
                 / SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) DESC LIMIT 1"""),

    ("What is the total refund amount across all returns?",
     "SELECT ROUND(SUM(refund_amount), 2) FROM transactions WHERE event_type = 'return'"),

    ("How much money was refunded for Apparel?",
     """SELECT ROUND(SUM(refund_amount), 2) FROM transactions
        WHERE event_type = 'return' AND product_category = 'Apparel'"""),

    ("What percentage of all refunds came from Apparel?",
     """SELECT ROUND(SUM(CASE WHEN product_category = 'Apparel' THEN refund_amount ELSE 0 END) * 100.0
               / SUM(refund_amount), 2)
        FROM transactions WHERE event_type = 'return'"""),

    ("What is the most common return reason for Electronics?",
     """SELECT reason FROM transactions
        WHERE event_type = 'return' AND product_category = 'Electronics'
        GROUP BY reason ORDER BY COUNT(*) DESC LIMIT 1"""),

    ("How many Home items were returned because they were defective?",
     """SELECT COUNT(*) FROM transactions
        WHERE event_type = 'return' AND product_category = 'Home' AND reason = 'Defective'"""),

    ("How many purchases were paid with UPI?",
     "SELECT COUNT(*) FROM transactions WHERE event_type = 'purchase' AND payment_method = 'UPI'"),

    ("Which city has the most customers?",
     "SELECT location FROM customers GROUP BY location ORDER BY COUNT(*) DESC LIMIT 1"),

    ("How many customers are from Mumbai?",
     "SELECT COUNT(*) FROM customers WHERE location = 'Mumbai'"),

    ("What is the average purchase amount?",
     "SELECT ROUND(AVG(amount), 2) FROM transactions WHERE event_type = 'purchase'"),

    ("How many purchases were made in March 2024?",
     """SELECT COUNT(*) FROM transactions
        WHERE event_type = 'purchase' AND timestamp LIKE '2024-03%'"""),

    ("Which customer got the highest total refund?",
     """SELECT customer_id FROM transactions WHERE event_type = 'return'
        GROUP BY customer_id ORDER BY SUM(refund_amount) DESC LIMIT 1"""),
]


def same_value(expected, value):
    # numbers can differ slightly because of rounding
    if isinstance(expected, (int, float)) and isinstance(value, (int, float)):
        return abs(expected - value) <= 0.01 * abs(expected) + 0.01
    return str(expected).strip().lower() == str(value).strip().lower()


def main():
    passed = 0
    for question, correct_sql in TESTS:
        expected = run_sql(correct_sql).iloc[0, 0]
        try:
            sql, result = ask(question)
            first_row = list(result.iloc[0]) if len(result) > 0 else []
            ok = any(same_value(expected, value) for value in first_row)
        except Exception as e:
            first_row, ok = [f"error: {e}"], False

        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {question}")
        print(f"      expected {expected}, got {first_row}")

    print(f"\nCorrect answers: {passed} / {len(TESTS)}")


if __name__ == '__main__':
    main()
