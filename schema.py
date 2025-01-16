from pydantic import BaseModel,StringConstraints
from fastapi import FastAPI, HTTPException, Request
from typing_extensions import Annotated

class STKResponse(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResponseCode: int
    ResponseDescription: str
    CustomerMessage: str

class STKPushPayload(BaseModel):
    amount: int
    phoneNumber: Annotated[str, StringConstraints(strip_whitespace=True,min_length=1, max_length=12)]
    accountNumber: Annotated[str, StringConstraints(strip_whitespace=True,min_length=1, max_length=12)]
    transactionDescription: Annotated[str, StringConstraints(strip_whitespace=True,min_length=1, max_length=13)] | None = None

# Define a model for the callback data
class MpesacallbackResponse(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResultCode: int
    ResultDesc: str
    Amount: float
    MpesaReceiptNumber: str
    PhoneNumber: str
class RegisterUrlPayload(BaseModel):
    ConfirmationUrl: str