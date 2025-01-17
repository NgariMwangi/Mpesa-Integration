from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from main import Base

class StkPushTransaction(Base):
    __tablename__ = "stk_push_transactions"

    id = Column(Integer, primary_key=True, index=True)
    merchant_request_id = Column(String, unique=True, nullable=False)  # Unique identifier for the STK push
    checkout_request_id = Column(String, unique=True, nullable=False)  # Unique identifier for checkout
    phone_number = Column(String, nullable=False)  # Customer's phone number
    account_reference=Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)  # Amount requested
    status = Column(String, default="Pending")  # Status of the transaction
    result_code = Column(Integer, nullable=True)  # Callback result code
    result_desc = Column(String, nullable=True)  # Callback result description
    created_at = Column(DateTime, default=datetime.utcnow)  # Time when the transaction was initiated
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update time

class Transaction(Base):
    """
    Database model to store transaction details.
    """
    __tablename__ = 'paybill_offline'

    id = Column(String, primary_key=True, unique=True, index=True)
    transaction_number = Column(String, nullable=False)
    trans_amount = Column(Float, nullable=False)
    first_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    trans_time = Column(DateTime, nullable=False)
    full_name = Column(String, nullable=True)