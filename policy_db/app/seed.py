from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
from models import (
    Customer, Product, CustomerPolicy, PolicyClaims, Reward, RewardRule, CustomerReward
)

# Database connection
# DATABASE_URL = "postgresql://adminmetlife:Metlifet24@metlifet24.postgres.database.azure.com:5432/metlifeClain-t24?sslmode=require"
DATABASE_URL = "postgresql://adminmetlife:Metlifet24@metlifet24.postgres.database.azure.com:5432/metlifeClain-t24?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def generate_dummy_data():
    # Insert Customers (50 records)
    customers = [
        Customer(
            name=f"Customer {i}",
            dob="1990-01-01",
            email=f"customer{i}@example.com",
            phone=f"98765432{i%10}",
            aadhar=f"1234567890{i%10}",
            pan=f"ABCDE{i%10}F",
            cibil=random.randint(600, 900)
        ) for i in range(1, 51)
    ]
    session.add_all(customers)
    session.commit()

    # Insert Products (5 records)
    products = [
        Product(
            name=f"Product {i}",
            description=f"Insurance product {i}",
            premium_amount=random.uniform(5000, 50000),
            max_coverage=random.uniform(100000, 1000000),
            min_cibil=random.randint(650, 850)
        ) for i in range(1, 6)
    ]
    session.add_all(products)
    session.commit()

    # Insert Customer Policies (50 records)
    customer_policies = [
        CustomerPolicy(
            customer_id=random.randint(1, 50),
            policy_id=random.randint(1, 5),
            insurance_status="approved",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=365 * random.randint(1, 5))
        ) for _ in range(50)
    ]
    session.add_all(customer_policies)
    session.commit()

    # Insert Policy Claims (50 records)
    claims = [
        PolicyClaims(
            policy_id=random.randint(1, 5),
            customer_id=random.randint(1, 50),
            claim_amount_ask=random.uniform(1000, 10000),
            status=random.choice(["approved", "pending", "failed"])
        ) for _ in range(50)
    ]
    session.add_all(claims)
    session.commit()

    # Insert Rewards (50 records)
    rewards = [
        Reward(
            reward_type="Bonus",
            reward_description="Loyalty reward",
            reward=random.uniform(10, 500)
        ) for _ in range(50)
    ]
    session.add_all(rewards)
    session.commit()

    # Insert Reward Rules (5 records)
    reward_rules = [
        RewardRule(
            rule_name=f"Rule {i}",
            non_claim_years=random.randint(1, 5),
            product_id=random.randint(1, 5)
        ) for i in range(1, 6)
    ]
    session.add_all(reward_rules)
    session.commit()

    # Insert Customer Rewards (50 records)
    customer_rewards = [
        CustomerReward(
            customer_id=random.randint(1, 50),
            reward_id=random.randint(1, 50)
        ) for _ in range(50)
    ]
    session.add_all(customer_rewards)
    session.commit()

    print("✅ Dummy data inserted successfully!")

# Run the function
if __name__ == "__main__":
    generate_dummy_data()
