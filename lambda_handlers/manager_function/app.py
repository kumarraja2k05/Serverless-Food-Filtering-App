import json
import os
import boto3
import requests

QUEUE_ARN = os.getenv("SQSQueue")
region = os.getenv("Region")
logical_id = os.getenv("Logical_ID")
api_url = os.getenv("API_URL")
sqs_client = boto3.client("sqs", "us-west-2")

def lambda_handler(event, context):
    print("ARN: ",QUEUE_ARN)
    data = json.loads(event.get("Records")[0].get("body"))
    print("event body: ",data)
    required_method = data["action"].lower()
    account_id = data["account_id"]
    resp = None
    if required_method == "add":
        print("Create New License")
        url = api_url + "/add"
        print("Api url: ",url)
        response = requests.post(url, json=data)
        print("response value: ",response.json())
        resp = response.json()
    elif required_method == "delete":
        print("Delete License")
        url = api_url + "/delete"
        print("Api url: ",url)
        response = requests.delete(url,data={"id":account_id,"serial_number": data["serial_number"], "type": data["type"], "action":required_method})
        print("response value: ",response.json())
        resp = response.json()
    elif required_method == "update":
        url = api_url + "/update"
        print("Api url: ",url)
        print("Update License")
        response = requests.put(url, json=data)
        print("response value: ",response.json())
        resp = response.json()
    else:
        print("Please specify request_type as [insert, update, delete]")
    return json.dumps({"data": resp,"msg": "SuccessFul"})