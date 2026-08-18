import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sales_dataset(output_path: str = "data/raw/sales_data.csv", num_rows: int = 55000, seed: int = 42):
    """
    Generates a realistic synthetic sales dataset for business analytics testing.
    Includes business trends, seasonal variation, regional distribution, and edge cases.
    """
    np.random.seed(seed)
    random.seed(seed)

    print(f"Generating synthetic sales dataset ({num_rows} rows)...")

    # Categories & Products catalog
    catalog = [
        {"product_id": "PROD-001", "product_name": "UltraBook Pro 15", "category": "Electronics", "unit_price": 1200.00, "unit_cost": 850.00},
        {"product_id": "PROD-002", "product_name": "Smart Monitor 27", "category": "Electronics", "unit_price": 350.00, "unit_cost": 220.00},
        {"product_id": "PROD-003", "product_name": "Wireless Ergonomic Mouse", "category": "Accessories", "unit_price": 45.00, "unit_cost": 18.00},
        {"product_id": "PROD-004", "product_name": "Mechanical RGB Keyboard", "category": "Accessories", "unit_price": 95.00, "unit_cost": 45.00},
        {"product_id": "PROD-005", "product_name": "HD Noise Cancelling Headset", "category": "Electronics", "unit_price": 180.00, "unit_cost": 95.00},
        {"product_id": "PROD-006", "product_name": "Ergonomic Desk Chair", "category": "Furniture", "unit_price": 280.00, "unit_cost": 160.00},
        {"product_id": "PROD-007", "product_name": "Standing Electric Desk", "category": "Furniture", "unit_price": 550.00, "unit_cost": 340.00},
        {"product_id": "PROD-008", "product_name": "USB-C Multi-Port Hub", "category": "Accessories", "unit_price": 60.00, "unit_cost": 22.00},
        {"product_id": "PROD-009", "product_name": "Enterprise Server Rack 1U", "category": "Hardware", "unit_price": 2400.00, "unit_cost": 1750.00},
        {"product_id": "PROD-010", "product_name": "4K Ultra HD Webcam", "category": "Electronics", "unit_price": 110.00, "unit_cost": 55.00},
        {"product_id": "PROD-011", "product_name": "Portable SSD 2TB", "category": "Hardware", "unit_price": 160.00, "unit_cost": 90.00},
        {"product_id": "PROD-012", "product_name": "Smart LED Desk Lamp", "category": "Furniture", "unit_price": 40.00, "unit_cost": 18.00},
        {"product_id": "PROD-013", "product_name": "Laser Color Printer", "category": "Office Equipment", "unit_price": 420.00, "unit_cost": 280.00},
        {"product_id": "PROD-014", "product_name": "Paper Shredder Heavy Duty", "category": "Office Equipment", "unit_price": 130.00, "unit_cost": 70.00},
        {"product_id": "PROD-015", "product_name": "Executive Leather Notebook", "category": "Stationery", "unit_price": 25.00, "unit_cost": 8.00},
    ]

    # Customers list
    first_names = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Sneha", "Rahul", "Neha", "Amit", "Kavya",
                   "Siddharth", "Pooja", "Aditya", "Riya", "Karan", "Meera", "Arjun", "Tanvi", "Dev", "Isha"]
    last_names = ["Sharma", "Verma", "Patel", "Mehta", "Deshmukh", "Joshi", "Kulkarni", "Gupta", "Nair", "Rao",
                  "Chopra", "Singh", "Reddy", "Iyer", "Sen", "Bhat", "Das", "Saxena", "Roy", "Kapoor"]

    customers = []
    for i in range(1, 601):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        customers.append({
            "customer_id": f"CUST-{i:04d}",
            "customer_name": f"{fn} {ln}"
        })

    # Regional geography mapping
    regions = {
        "West": [
            {"state": "Maharashtra", "cities": ["Mumbai", "Pune", "Nagpur"]},
            {"state": "Gujarat", "cities": ["Ahmedabad", "Surat", "Vadodara"]}
        ],
        "North": [
            {"state": "Delhi", "cities": ["New Delhi", "North Delhi"]},
            {"state": "Punjab", "cities": ["Ludhiana", "Amritsar", "Chandigarh"]},
            {"state": "Uttar Pradesh", "cities": ["Noida", "Lucknow", "Kanpur"]}
        ],
        "South": [
            {"state": "Karnataka", "cities": ["Bengaluru", "Mysuru"]},
            {"state": "Tamil Nadu", "cities": ["Chennai", "Coimbatore"]},
            {"state": "Telangana", "cities": ["Hyderabad", "Warangal"]}
        ],
        "East": [
            {"state": "West Bengal", "cities": ["Kolkata", "Howrah"]},
            {"state": "Odisha", "cities": ["Bhubaneswar", "Cuttack"]}
        ]
    }

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 6, 30)
    total_days = (end_date - start_date).days

    rows = []
    order_id_counter = 10001

    region_names = list(regions.keys())
    region_weights = [0.35, 0.30, 0.25, 0.10] # West & North drive majority volume

    for i in range(num_rows):
        # Pick date with seasonal Q4 boost
        day_offset = random.randint(0, total_days)
        order_date = start_date + timedelta(days=day_offset)
        
        # Product & Customer
        product = random.choice(catalog)
        customer = random.choice(customers)

        # Region & Location
        region_name = np.random.choice(region_names, p=region_weights)
        state_info = random.choice(regions[region_name])
        state_name = state_info["state"]
        city_name = random.choice(state_info["cities"])

        # Casing inconsistency test cases (e.g. maharashtra vs Maharashtra)
        if random.random() < 0.03:
            state_name = state_name.lower()
        elif random.random() < 0.02:
            state_name = state_name.upper()

        # Quantity & Discount
        quantity = int(np.random.negative_binomial(n=3, p=0.4)) + 1
        discount = round(random.choice([0.0, 0.05, 0.10, 0.15, 0.20, 0.25]), 2)

        # Introduce intentional outliers and negative invalid numbers (0.2% of dataset)
        if random.random() < 0.001:
            quantity = -5  # Invalid quantity
        if random.random() < 0.001:
            discount = 1.50 # Invalid discount > 100%

        # Introduce missing values (0.3% of dataset)
        if random.random() < 0.003:
            city_name = None
        if random.random() < 0.003:
            discount = None

        rows.append({
            "order_id": f"ORD-{order_id_counter + (i // 2)}", # Shared order IDs for multi-item orders
            "order_date": order_date.strftime("%Y-%m-%d"),
            "customer_id": customer["customer_id"],
            "customer_name": customer["customer_name"],
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "category": product["category"],
            "quantity": quantity,
            "unit_price": product["unit_price"],
            "discount": discount,
            "cost": product["unit_cost"],
            "city": city_name,
            "state": state_name,
            "region": region_name
        })

    df = pd.DataFrame(rows)

    # Add duplicate rows (~0.8%) to test deduplication pipeline
    duplicate_rows = df.sample(frac=0.008, random_state=42)
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Successfully generated {len(df):,} sales records at '{output_path}'.")
    return output_path

if __name__ == "__main__":
    generate_sales_dataset()
