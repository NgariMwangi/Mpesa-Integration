from fastapi import FastAPI, HTTPException, Request, requests
from schema import STKResponse, STKPushPayload
from utils import *

app = FastAPI()
@app.post("/stkpush")
def stk_push(payload: STKPushPayload):
    
    phone_number = payload.phoneNumber
    account_number = business_short_code
    amount = 1
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
      
        "AccountReference": account_number,
        "TransactionDesc": "Edwin is shouting at us"
    }
    r=requests.post(url, json=body, headers=header).json()
    return r