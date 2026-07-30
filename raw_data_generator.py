import json
import random
import uuid
import os
from datetime import datetime, timedelta

def generate_users(num_users=2000):
    users = []
    locations = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Pune']
    
    for i in range(1, num_users + 1):
        users.append({
            "_id": f"U{str(i).zfill(5)}",
            "profile": {
                "location": random.choice(locations),
                "signup_date": (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))).isoformat()
            },
            "status": "active"
        })
    return users

def generate_events(num_users=2000, num_orders=8000):
    events = []
    categories = ['Electronics', 'Apparel', 'Home', 'Beauty']
    
    for i in range(1, num_orders + 1):
        user_id = f"U{str(random.randint(1, num_users)).zfill(5)}"
        order_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 180))
        category = random.choice(categories)
        price = round(random.uniform(500, 5000), 2)
        
        events.append({
            "event_id": f"EV{str(len(events)+1).zfill(6)}",
            "event_type": "purchase",
            "timestamp": order_date.isoformat(),
            "user_id": user_id,
            "payload": {
                "product_category": category,
                "amount": price,
                "payment_method": random.choice(['UPI', 'Credit Card', 'Debit Card'])
            }
        })
        
        return_prob = 0.35 if category == 'Apparel' else 0.05
            
        if random.random() < return_prob:
            return_date = order_date + timedelta(days=random.randint(2, 14))
            events.append({
                "event_id": f"EV{str(len(events)+1).zfill(6)}",
                "event_type": "return",
                "timestamp": return_date.isoformat(),
                "user_id": user_id,
                "payload": {
                    "product_category": category,
                    "refund_amount": price,
                    "reason": "Size Issue" if category == 'Apparel' else random.choice(["Defective", "Changed Mind"])
                }
            })
    return events

if __name__ == "__main__":
    os.makedirs('raw_data', exist_ok=True)
    
    users = generate_users()
    with open('raw_data/raw_users.json', 'w') as f:
        json.dump(users, f, indent=4)
        
    events = generate_events()
    with open('raw_data/raw_events.json', 'w') as f:
        json.dump(events, f, indent=4)
