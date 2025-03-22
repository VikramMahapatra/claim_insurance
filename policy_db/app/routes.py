from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from redis import Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

redis = Redis(host="localhost", port=6379, decode_responses=True)
FastAPICache.init(RedisBackend(redis), prefix="customer_cache")

router = APIRouter()

@router.post("/customers/", response_model=schemas.CustomerSchema)
def create_customer(customer: schemas.CustomerSchema, db: Session = Depends(get_db)):
    return crud.create_customer(db, customer)

@router.get("/customers/", response_model=list[schemas.CustomerSchema])
@cache(expire=10800)
def get_customers(db: Session = Depends(get_db)):
    return crud.get_customers(db)

@router.post("/policies/", response_model=schemas.ProductSchema)
def create_policy(policy: schemas.ProductSchema, db: Session = Depends(get_db)):
    return crud.create_policy(db, policy)

@router.get("/policies/", response_model=list[schemas.ProductSchema])
@cache(expire=10800)
def get_policies(db: Session = Depends(get_db)):
    return crud.get_policies(db)

@router.post("/customer_policies/", response_model=schemas.CustomerPolicySchema)
def assign_policy(customer_policy: schemas.CustomerPolicySchema, db: Session = Depends(get_db)):
    return crud.assign_policy(db, customer_policy)

@router.get("/customer_policies/", response_model=list[schemas.CustomerPolicySchema])
@cache(expire=10800)
def get_customer_policies(db: Session = Depends(get_db)):
    return crud.get_customer_policies(db)


@router.get("/claims/{customer_id}", response_model=list[schemas.PolicyClaimsSchema])
@cache(expire=10800)
def get_claims_by_customer(customer_id: int, db: Session = Depends(get_db)):
    return crud.get_claims_by_customer(db, customer_id)


@router.get("/get_all_claims", response_model=list[schemas.PolicyClaimsSchema])
@cache(expire=10800)
def get_all_claims(db: Session = Depends(get_db)):
    return crud.get_all_claims(db)

@router.get("/get_recommendations", response_model=list[schemas.CustomerSchema, schemas.CustomerRewardSchema, schemas.RewardSchema])
@cache(expire=10800)
def get_all_claims(db: Session = Depends(get_db)):
    return crud.get_top_customers_recommedations(db)

@router.get("/get_monthly_claim_count", response_model=list[schemas.PolicyClaimsSchema])
@cache(expire=10800)
def get_monthly_claims_count(db: Session = Depends(get_db)):
    return crud.get_top_customers_recommedations(db)

@router.post("/answer_question", response_model=list[schemas.ChatSchema])
def user_question(db: Session = Depends(get_db)):
    return crud.ask_question(db)



