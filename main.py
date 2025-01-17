from fastapi import FastAPI, HTTPException, Request, requests, Depends
from schema import STKResponse, STKPushPayload, MpesacallbackResponse, RegisterUrlPayload
from utils import *
from sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.orm import Session
import pytz, json
from query import query_transaction_status
from typing import List, Dict
# Base class for SQLAlchemy models
Base = declarative_base()

from database import StkPushTransaction, Transaction
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
        "CallBackURL": "https://techtutor.co.ke/callbackurl",
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
   "ConfirmationURL":"https://techtutor.co.ke/confirmationurl",
   "ValidationURL":"https://techtutor.co.ke/validationurl"
    }
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token}
    print(header)
    r = requests.post(
        "https://api.safaricom.co.ke/mpesa/c2b/v2/registerurl",
        json=payload,
        headers=header
    ).json()

    return r

@app.post("/validationurl", 
    tags=['C2B'],)
async def validation_url(request: Request):
    body = await request.json()
    print(f'validation: {body}')
    with open('ValidateResponse.json', 'a') as outfile:
        json.dump(body, outfile)

    # in the mean time, accept all monies by returning 'ResultCode' of 0

    return {"ResultCode": 0, "ResultDesc": "Accepted"}

@app.post('/confirmationurl',
    tags=['C2B'],)
async def confirmation_url(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    print(f'confirmation: {body}')
    with open('ConfirmationResponse.json', 'a') as outfile:
        json.dump(body, outfile)
    try:
        transaction = Transaction(
        transaction_number=body['TransID'],
        trans_amount=body['TransAmount'],
        first_name=body['FirstName'],
        trans_time=body['TransTime'],
        account_reference=body['BillRefNumber']
    )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
    except Exception as e:
        print(f"Error when storing paybill trans in db: {e}")
    try:
     print(f"trans id when calling quering endpoint: {body['TransID']}")
     query_transaction_status(body['TransID'])
    except Exception as e:
        print(f"Error when quering transaction by transaction id: {e}")

    # in the mean time, accept all monies by returning 'ResultCode' of 0

    return {"ResultCode": 0, "ResultDesc": "Accepted" }
@app.post('/resulturl',
    tags=['C2B'],)
async def result_url(request: Request,  db: Session = Depends(get_db)):
    body = await request.json()
    print(f'result: {body}')
    with open('ConfirmationResponse.json', 'a') as outfile:
        json.dump(body, outfile)
    if body["Result"]["ResultCode"]==0:
        x=body["Result"]["ResultParameters"]["ResultParameter"]
        y={}
        for i in x:
            if i["Key"]=='ReceiptNo':
                y=i
                break
        Transaction_id=y["Value"]

        transaction = (db.query(Transaction).filter(Transaction.transaction_number == Transaction_id).first())
        if transaction:
            
            dict={}
            for i in x:
                if i["Key"]=='DebitPartyName':
                    dict=i
                    break
            value=dict["Value"]
            phone_number, fullname = value.split(' - ', 1)
            transaction.phone_number=phone_number
            transaction.full_name=fullname
            # Commit the changes to the database
            db.commit()

            # Refresh the session to reflect the updates
            db.refresh(transaction)
            print("fullname and phone number updated correctly")
        else:
            print(f'Transaction with transaction id {Transaction_id} not found in the database')
        # in the mean time, accept all monies by returning 'ResultCode' of 0
    else:
        print(f"Wrong response from query transaction callback url received: {body}")
    return {"ResultCode": 0, "ResultDesc": "Accepted" }
@app.post('/timeouturl',
    tags=['C2B'],)
async def timeout_url(request: Request):
    body = await request.json()
    print(f'timeout: {body}')
    with open('ConfirmationResponse.json', 'a') as outfile:
        json.dump(body, outfile)

    # in the mean time, accept all monies by returning 'ResultCode' of 0

    return {"ResultCode": 0, "ResultDesc": "Accepted" }


@app.get("/transactions/{account_reference}", response_model=Dict[str, List[Dict]])
def get_transactions_by_account_reference(account_reference: str, db: Session = Depends(get_db)):
    """
    Get records from both StkPushTransaction and Transaction tables with the same account_reference.
    """
    # Query the `StkPushTransaction` table
    stk_push_transactions = db.query(StkPushTransaction).filter(StkPushTransaction.account_reference == account_reference).all()
    
    # Query the `Transaction` table
    transactions = db.query(Transaction).filter(Transaction.account_reference == account_reference).all()
    
    # Return the data in a structured format
    return {
        "stk_push_transactions": [
            {
                "id": stk.id,
                "merchant_request_id": stk.merchant_request_id,
                "checkout_request_id": stk.checkout_request_id,
                "phone_number": stk.phone_number,
                "account_reference": stk.account_reference,
                "amount": stk.amount,
                "status": stk.status,
                "result_code": stk.result_code,
                "result_desc": stk.result_desc,
                "created_at": stk.created_at,
                "updated_at": stk.updated_at,
            }
            for stk in stk_push_transactions
        ],
        "transactions": [
            {
                "id": txn.id,
                "account_reference": txn.account_reference,
                "transaction_number": txn.transaction_number,
                "trans_amount": txn.trans_amount,
                "first_name": txn.first_name,
                "phone_number": txn.phone_number,
                "trans_time": txn.trans_time,
                "full_name": txn.full_name,
            }
            for txn in transactions
        ],
    }
