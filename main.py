from fastapi import FastAPI, HTTPException, Request, requests, Depends
from schema import STKResponse, STKPushPayload, MpesacallbackResponse, RegisterUrlPayload
from utils import *
from sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.orm import Session
import pytz, json

# Base class for SQLAlchemy models
Base = declarative_base()

from database import StkPushTransaction
# SQLite database URL
DATABASE_URL = "sqlite:///./stk_push.db"

# Create the SQLite engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)
# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
@app.post("/stkpush")
def stk_push(payload: STKPushPayload, db: Session = Depends(get_db)):
    
    phone_number = payload.phoneNumber
    account_number = payload.accountNumber
    amount = payload.amount
    token=authenticator()
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token}
    print(header)
    url = base_url + 'mpesa/stkpush/v1/processrequest'
    body = {
        "BusinessShortCode": business_short_code,
        "Password": generate_password(),
        "Timestamp": get_timestamp(),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://292d-217-199-146-223.ngrok-free.app/callbackurl",
        "AccountReference": account_number,
        "TransactionDesc": "Edwin is shouting at us"
    }
    r=requests.post(url, json=body, headers=header).json()
    print(r)
    if "MerchantRequestID" not in r:
        raise HTTPException(
            status_code=400, detail="Invalid STK Push response: Missing MerchantRequestID"
        )
        # Create and save the transaction
    transaction = StkPushTransaction(
        merchant_request_id=r["MerchantRequestID"],
        checkout_request_id=r["CheckoutRequestID"],
        phone_number=phone_number,
        amount=amount,
        account_reference=account_number
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return r




@app.post("/callbackurl")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint to handle the M-Pesa STK Push callback without schema restrictions.
    """
    # Parse the incoming JSON payload
    callback_data = await request.json()
    callback_data=callback_data["Body"]["stkCallback"]
        # Query the database for the existing record
    transaction = (
        db.query(StkPushTransaction).filter(StkPushTransaction.merchant_request_id == callback_data["MerchantRequestID"], StkPushTransaction.checkout_request_id == callback_data["CheckoutRequestID"]).first())

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    print(callback_data)
    transaction.status="Done"
    transaction.result_code=callback_data["ResultCode"]
    transaction.result_desc=callback_data["ResultDesc"]
    # Set the timezone to East Africa Time (Kenya)
    kenya_timezone = pytz.timezone("Africa/Nairobi")

    # Get the current time in UTC and convert to Kenyan time
    kenya_time = datetime.now(pytz.utc).astimezone(kenya_timezone)
    transaction.updated_at = kenya_time
        # Commit the changes to the database
    db.commit()

    # Refresh the session to reflect the updates
    db.refresh(transaction)

    
    if callback_data.get("ResultCode") == 0:
        # Payment was successful
        print(f"Payment Successful: {callback_data.get('Amount')} paid by {callback_data.get('PhoneNumber')}")
        # Update your database with payment details, etc.
    else:
        # Payment failed or was canceled
        print(f"Payment Failed: {callback_data.get('ResultDesc')}")
    
    # Respond to the M-Pesa API that you received the callback
    return {"status": "success", "message": "Callback received successfully"}
  
@app.post("/mpesa/c2b/registerurl",
    tags=['C2B'],
    description="Register validation and confirmation URLs on M-Pesa",
    summary="Register validation and confirmation URLs on M-Pesa"
    )
async def regiser_url(payload: RegisterUrlPayload):
    print(payload)
    print(type(payload))
    
    token=authenticator()
    payload={
         "ShortCode": "4149503",
   "ResponseType":"Completed",
   "ConfirmationURL":payload.ConfirmationUrl,
    }
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token}
    print(header)
    r = requests.post(
        "https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl",
        json=payload,
        headers=header
    ).json()

    return r

@app.post("/validationUrl", 
    tags=['C2B'],)
async def validation_url(request: Request):
    body = await request.json()
    with open('ValidateResponse.json', 'a') as outfile:
        json.dump(body, outfile)

    # in the mean time, accept all monies by returning 'ResultCode' of 0

    return {"ResultCode": 0, "ResultDesc": "Accepted"}

@app.post('/confirmationUrl',
    tags=['C2B'],)
async def confirmation_url(request: Request):
    body = await request.json()
    with open('ConfirmationResponse.json', 'a') as outfile:
        json.dump(body, outfile)

    # in the mean time, accept all monies by returning 'ResultCode' of 0

    return {"ResultCode": 0, "ResultDesc": "Accepted" }