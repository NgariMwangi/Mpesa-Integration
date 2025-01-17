from utils import *
from fastapi import FastAPI, HTTPException

def query_transaction_status(transaction_id):
    token=authenticator()
    url = "https://api.safaricom.co.ke/mpesa/transactionstatus/v1/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "Initiator": "TechAPI",
        "SecurityCredential": "5f462fe40146a4501aeb69d775c0eb06a5377802bc439a04214a4c4579995d0c1ac23d3f3d5916b3c7f88893523162d07525cf0966050c9b2bcceea59034baa739dd0e6c275820ab2752eb2e922a14b316ac11f3f1e816dd95cc7f3cf6392d34ec89bb2376fd144188482a1f0d447996c8f624b4ecf4acb4e2bd50c519e05a4d4a77f54b1727db66a44f198e8ada25a4437134717c55a8d29f4958aa0e4c3ccd34c1af29b932d557d760c25b5d92f45ac10f1a2aa22175348392f109baf0095d3cf165a96ea79f84fa05b7dff5e7763cbd3096b610664687dab04f9418ea941f13c8577d506e8835fc3d6e0b97f9e6d21070462d62c96c0baba352eeacaee23a",
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

query_transaction_status("TAH5J2K991")
