body={
    "Result": {
        "ResultType": 0,
        "ResultCode": 0,
        "ResultDesc": "The service request is processed successfully.",
        "OriginatorConversationID": "21dc-4436-8408-ee2f032ee36b9257921",
        "ConversationID": "AG_20250117_20305b55146d275e7daf",
        "TransactionID": "TAH0000000",
        "ResultParameters": {
            "ResultParameter": [
                {"Key": "DebitPartyName", "Value": "0790422909 - Dennis  ngari mwangi"},
                {"Key": "CreditPartyName", "Value": "4149503 -  TECH TUTOR ENTERPRISE"},
                {"Key": "OriginatorConversationID", "Value": "6b16-43f4-a9f6-8e81ad29eeab2987739"},
                {"Key": "InitiatedTime", "Value": 20250117170614},
                {"Key": "CreditPartyCharges"},
                {"Key": "DebitAccountType", "Value": "MMF Account For Customer"},
                {"Key": "TransactionReason"},
                {"Key": "ReasonType", "Value": "Pay Bill Online"},
                {"Key": "TransactionStatus", "Value": "Completed"},
                {"Key": "FinalisedTime", "Value": 20250117170614},
                {"Key": "Amount", "Value": 1.0},
                {"Key": "ConversationID", "Value": "AG_20250117_20503343d9b604c7af7e"},
                {"Key": "ReceiptNo", "Value": "TAH5J2K991"}
            ]
        },
        "ReferenceData": {
            "ReferenceItem": {
                "Key": "Occasion",
                "Value": "Query"
            }
        }
    }
}

Transaction_id=body["Result"]["TransactionID"]
x=body["Result"]["ResultParameters"]["ResultParameter"]
dict={}
for i in x:
    
    if i["Key"]=='DebitPartyName':
        dict=i
        break
value=dict["Value"]
phone_number, fullname = value.split(' - ', 1)
print(Transaction_id)
print(value)
print(phone_number)
print(fullname)
print(body["Result"]["ResultCode"])