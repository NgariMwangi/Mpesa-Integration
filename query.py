from utils import *
from fastapi import FastAPI, HTTPException

def query_transaction_status(transaction_id):
    print("hellocxbhuiwdhr")
    token=authenticator()
    url = "https://api.safaricom.co.ke/mpesa/transactionstatus/v1/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "Initiator": "TechAPI",
        "SecurityCredential": "GPf6sjofg8TYPGSYyWGg6QZRaNQLKfLRh03RfafwR371SS14FQ+orp5ONig2UgXL/4vBP2Y5F/pEoQDaQuA+29Mv2SkGF6zBsGGm7a2TiGLzIuAC9fQBT7NISx/nLi+nd+jSeFbz+P12Va41WD9Sy0a3qGs6SdIkJB3F0sTAvxZloQU56jAUKOEM52D9tHbNKkYVpHqzXVBccW7b6J2HFzeZwyK+vv+G73/azj3QzikACaF/wSDy3pObnHNRHZsp8skEvGyhVLPWm+ik3SBk9CakGP5VDeRzTR4Lo7DVZDU2z9XszIh7waPlskIp8tVkCpgXQyeuoq0DhHPkYDdR4Q==",
        "CommandID": "TransactionStatusQuery",
        "TransactionID": transaction_id,
        "PartyA": "4149503",
        "IdentifierType": "4",  # Shortcode identifier
        "ResultURL": "https://techtutor.co.ke/resulturl",
        "QueueTimeOutURL": "https://techtutor.co.ke/timeouturl",
        "Remarks": "Transaction status query",
        "Occasion": "Query"
    }
    response = requests.post(url, headers=headers, json=payload)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Transaction status query failed: {response.text}",
        )


