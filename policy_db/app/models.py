from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from sqlalchemy.types import Enum as PyEnum
from enum import Enum

class Status(Enum):
    APPROVED = "approved"
    PENDING = "pending"
    FAILED = "failed"

class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dob = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    aadhar = Column(String, nullable=False, unique=True)
    pan = Column(String, nullable=False, unique=True)
    cibil = Column(Integer, nullable=True)

    policies = relationship("CustomerPolicy", back_populates="customer")
    claims = relationship("PolicyClaims", back_populates="customer")
    rewards = relationship("CustomerReward", back_populates="customer")

class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    premium_amount = Column(Float, nullable=False)
    max_coverage = Column(Float, nullable=False)
    min_cibil = Column(Integer, nullable=False)

    policies = relationship("CustomerPolicy", back_populates="policy")
    claims = relationship("PolicyClaims", back_populates="policy")
    rewards = relationship("RewardRule", back_populates="product")

class CustomerPolicy(Base):
    __tablename__ = "customer_policy"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    insurance_status = Column(PyEnum(Status), nullable=False, default=lambda: Status.PENDING)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    customer = relationship("Customer", back_populates="policies")
    policy = relationship("Product", back_populates="policies")

class PolicyClaims(Base):
    __tablename__ = "policy_claims"
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    claim_amount_ask = Column(Float, nullable=False)
    status = Column(PyEnum(Status), nullable=True, default=lambda: Status.PENDING)

    customer = relationship("Customer", back_populates="claims")
    policy = relationship("Product", back_populates="claims")

class Reward(Base):
    __tablename__ = "reward"
    id = Column(Integer, primary_key=True, index=True)
    reward_type = Column(String, nullable=True)
    reward_description = Column(String, nullable=False)
    reward = Column(Float, nullable=False)
    reward_rule_id = Column(Integer, ForeignKey("reward_rule.id"), nullable=True)

    rewardrule = relationship("RewardRule", back_populates="rewards")

class RewardRule(Base):
    __tablename__ = "reward_rule"
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String, nullable=False)
    non_claim_years = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)

    product = relationship("Product", back_populates="rewards")
    rewards = relationship("Reward", back_populates="rewardrule")

class CustomerReward(Base):
    __tablename__ = "customer_reward"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("reward.id"), nullable=False)

    customer = relationship("Customer", back_populates="rewards")
    reward = relationship("Reward")

class Complain(Base):
    __tablename__ = "complain"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    complain_desc = Column(String, nullable=True)
    status = Column(PyEnum(Status), nullable=False, default=lambda: Status.PENDING)

class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    questions_answers = Column(JSON, nullable=True, default=[])
    
    customer = relationship("Customer")

