from fastapi import FastAPI, HTTPException, Request, requests
from schema import STKResponse, STKPushPayload, MpesacallbackResponse
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
        "CallBackURL": "https://techtutor.co.ke/callbackurl",
        "AccountReference": account_number,
        "TransactionDesc": "Edwin is shouting at us"
    }
    r=requests.post(url, json=body, headers=header).json()
    return r



app = FastAPI()



@app.post("/callbackurl")
async def mpesa_callback(request: Request, callback_data: MpesacallbackResponse):
    """
    Endpoint to handle the M-Pesa STK Push callback.
    """
    # Process the callback data
    print(f"Received M-Pesa Callback: {callback_data}")
    
    # You can handle the callback response here, for example:
    if callback_data.ResultCode == 0:
        # Payment was successful, you can process the transaction
        print(f"Payment Successful: {callback_data.Amount} paid by {callback_data.PhoneNumber}")
        # Update your database with payment details, etc.
    else:
        # Payment failed or was canceled, handle accordingly
        print(f"Payment Failed: {callback_data.ResultDesc}")
    
    # Respond to the M-Pesa API that you received the callback (200 OK)
    return {"status": "success", "message": "Callback received successfully"}
