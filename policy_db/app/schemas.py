from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class InsuranceStatusEnum(str, Enum):
    APPROVED = "approved"
    PENDING = "pending"
    FAILED = "failed"

class CustomerSchema(BaseModel):
    id: Optional[int]
    name: str
    dob: str
    email: str
    phone: str
    aadhar: str
    pan: str
    cibil: Optional[int]
    
    class Config:
        orm_mode = True

class ProductSchema(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    premium_amount: float
    max_coverage: float
    min_cibil: int
    
    class Config:
        orm_mode = True

class CustomerPolicySchema(BaseModel):
    id: Optional[int]
    customer_id: int
    policy_id: int
    insurance_status: InsuranceStatusEnum
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    
    class Config:
        orm_mode = True

class PolicyClaimsSchema(BaseModel):
    id: Optional[int]
    policy_id: int
    customer_id: int
    claim_amount_ask: float
    claim_amount_approved: Optional[float]
    
    class Config:
        orm_mode = True

class RewardSchema(BaseModel):
    id: Optional[int]
    reward_type: Optional[str]
    reward_description: str
    reward: float
    reward_rule_id: Optional[int]
    
    class Config:
        orm_mode = True

class RewardRuleSchema(BaseModel):
    id: Optional[int]
    rule_name: int
    non_claim_years: int
    
    class Config:
        orm_mode = True

class CustomerRewardSchema(BaseModel):
    id: Optional[int]
    customer_id: int
    reward_id: int
    
    class Config:
        orm_mode = True

class ComplainSchema(BaseModel):
    id: Optional[int]
    customer_id: int
    complain_desc: str
    status: InsuranceStatusEnum

    class Config:
        orm_mode = True

class ChatSchema(BaseModel):
    customer_id: int
    questions_answers: List[dict]

    class Config:
        orm_mode = True