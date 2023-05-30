import json
import os
import boto3
import requests
import logging

QUEUE_ARN = os.getenv("SQSQueue")
region = os.getenv("Region")
logical_id = os.getenv("Logical_ID")
api_url = os.getenv("API_URL")
sqs_client = boto3.client("sqs", "us-west-2")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info(f"Queue ARN {QUEUE_ARN}")
        data = json.loads(event.get("Records")[0].get("body"))
        logger.info(f"Event body {data}")
        required_method = data["action"].lower()
        account_id = data["account_id"]
        resp = None
        if required_method == "add":
            logger.info("Create New License")
            url = api_url + "/add"
            logger.info(f"Add Api url {url}")
            response = requests.post(url, json=data)
            logger.info(f"Create License response value {response.json()}")
            resp = response.json()
        elif required_method == "delete":
            logger.info("Delete License")
            url = api_url + "/delete"
            logger.info(f"Delete Api url {url}")
            response = requests.delete(url,data={"id":account_id,"serial_number": data["serial_number"], "type": data["type"], "action":required_method})
            logger.info(f"Delete License response value {response.json()}")
            resp = response.json()
        elif required_method == "update":
            logger.info("Update License")
            url = api_url + "/update"
            logger.info(f"Update Api url {url}")
            response = requests.put(url, json=data)
            logger.info(f"Update License response value {response.json()}")
            resp = response.json()
        else:
            logger.info("Please specify request_type as [add, update, delete]")
        return json.dumps({"data": resp,"msg": "SuccessFul"})
    
    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }