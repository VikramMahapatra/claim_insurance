from sqlalchemy.orm import Session
# from app import models, schemas
from app import models, schemas
from sqlalchemy import func
from datetime import datetime


def create_customer(db: Session, customer: schemas.CustomerSchema):
    db_customer = models.Customer(name=customer.name, email=customer.email, phone=customer.phone)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def get_customers(db: Session):
    return db.query(models.Customer).all()

def create_policy(db: Session, policy: schemas.ProductSchema):
    db_policy = models.Policy(**policy.dict())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

def get_policies(db: Session):
    return db.query(models.Policy).all()

def assign_policy(db: Session, customer_policy: schemas.CustomerPolicySchema):
    db_customer_policy = models.CustomerPolicy(**customer_policy.dict())
    db.add(db_customer_policy)
    db.commit()
    db.refresh(db_customer_policy)
    return db_customer_policy

def get_customer_policies(db: Session):
    return db.query(models.CustomerPolicy).all()

def get_claims_by_customer(db: Session, customer_id: int):
    claims = db.query(models.PolicyClaims).filter(models.PolicyClaims.customer_id == customer_id).all()

    total_claims = len(claims)
    approved_claims = db.query(func.count()).filter(
        models.PolicyClaims.customer_id == customer_id,
        models.PolicyClaims.status=="approved"
    ).scalar()

    failed_claims = db.query(func.count()).filter(
        models.PolicyClaims.customer_id == customer_id,
        models.PolicyClaims.status == "failed"
    ).scalar()

    pending_claims = db.query(func.count()).filter(
        models.PolicyClaims.customer_id == customer_id,
        models.PolicyClaims.status == "pending"
    ).scalar()

    return {
        "total_claims": total_claims,
        "approved_claims": approved_claims,
        "failed_claims": failed_claims,
        "pending_claims": pending_claims,
        "claims": claims
    }

def create_claim(db: Session, claim_data):
    new_claim = models.PolicyClaims(
        policy_id=claim_data.policy_id,
        customer_id=claim_data.customer_id,
        claim_amount_ask=claim_data.claim_amount_ask,
        claim_amount_approved=None  # Initially, no approval decision is made
    )
    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)
    return new_claim


def get_all_claims(db: Session):
    claims = db.query(models.PolicyClaims).filter(models.PolicyClaims).all()

    total_claims = len(claims)
    approved_claims = db.query(func.count()).filter(
        models.PolicyClaims.status=="approved"
    ).scalar()

    failed_claims = db.query(func.count()).filter(
        models.PolicyClaims.status == "failed"
    ).scalar()

    pending_claims = db.query(func.count()).filter(
        models.PolicyClaims.status == "pending"
    ).scalar()

    return {
        "total_claims": total_claims,
        "approved_claims": approved_claims,
        "failed_claims": failed_claims,
        "pending_claims": pending_claims,
        "claims": claims
    }

def get_top_customers_recommedations(db: Session):
    top_customers = (
        db.query(models.Customer.id, models.Customer.name, func.sum(models.Reward.reward).label("total_rewards"))
        .join(models.CustomerReward, models.Customer.id == models.CustomerReward.customer_id)
        .join(models.Reward, models.CustomerReward.reward_id == models.Reward.id)
        .group_by(models.Customer.id, models.Customer.name)
        .order_by(func.sum(models.Reward.reward).desc())
        .limit(3)
        .all()
    )

    return [{"customer_id": c[0], "customer_name": c[1], "total_rewards": c[2]} for c in top_customers]

def get_monthly_claim_counts(db: Session):
    # Extract year and month from claim date and count each status
    monthly_claims = (
        db.query(
            func.date_trunc('month', models.PolicyClaims.claim_date).label("month"),
            func.count().label("total_claims"),
            func.sum(func.case((models.PolicyClaims.status == "approved", 1), else_=0)).label("approved_claims"),
            func.sum(func.case((models.PolicyClaims.status == "failed", 1), else_=0)).label("failed_claims"),
            func.sum(func.case((models.PolicyClaims.status == "pending", 1), else_=0)).label("pending_claims")
        )
        .group_by(func.date_trunc('month', models.PolicyClaims.claim_date))
        .order_by(func.date_trunc('month', models.PolicyClaims.claim_date))
        .all()
    )

    # Convert to dictionary format
    results = [
        {
            "month": row.month.strftime("%Y-%m"),  # Convert date to YYYY-MM format
            "total_claims": row.total_claims,
            "approved_claims": row.approved_claims,
            "failed_claims": row.failed_claims,
            "pending_claims": row.pending_claims
        }
        for row in monthly_claims
    ]

    return results

def ask_question(customer_id: int, question: str, db: Session):
    chat_entry = db.query(models.Chat).filter(models.Chat.customer_id == customer_id).first()
    if not chat_entry:
        chat_entry = models.Chat(customer_id=customer_id, questions_answers=[])
        db.add(chat_entry)

    # Append the question with an empty answer
    qa_pair = {"question": question, "answer": ""}
    chat_entry.questions_answers.append(qa_pair)
    db.commit()
    db.refresh(chat_entry)

    # Call the external API to get the answer
    # response = requests.post(EXTERNAL_API_URL, json={"question": question})
    response = {
        "status_code": 200,
        "response": "This is hard coded response"
    }
    
    if response.status_code == 200:
        answer = response.json().get("response", "No response")
    else:
        answer = "Error fetching answer"


    chat_entry.questions_answers[-1]["answer"] = answer
    db.commit()
    db.refresh(chat_entry)

    return response['response']
