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
    global api_url
    print("ARN: ",QUEUE_ARN)
    data = json.loads(event.get("Records")[0].get("body"))
    print("event body: ",data)
    print("Api url: ",api_url)
    required_method = data["request_type"].lower()
    food_id = data["food_item_id"]
    if required_method == "create":
        print("Create New Food")
        response = requests.post(api_url, json=data)
        print("response value: ",response.json())
    elif required_method == "delete":
        print("Delete Food")
        # api_url = f"{api_url}/{food_id}"
        response = requests.delete(api_url,data={"id":food_id,"category": data["category"],"request_type":required_method})
        print("response value: ",response.json())
    elif required_method == "update":
        print("Update Food")
        response = requests.put(api_url, json=data)
        print("response value: ",response.json())
    else:
        print("Please specify request_type as [insert, update, delete]")
    return json.dumps({"msg": "SuccessFul"})