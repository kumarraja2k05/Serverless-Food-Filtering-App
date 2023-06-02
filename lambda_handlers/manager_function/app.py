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
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger()


def lambda_handler(event, context):
    try:
        logger.info(f"Queue ARN {QUEUE_ARN}")
        data = json.loads(event.get("Records")[0].get("body"))
        logger.info(f"Event body {data}")
        logger.info(f"Api url {api_url}")
        response = requests.post(api_url, json=data)
        logger.info(f"Response value {response.json()}")
        resp = response.json()
        return json.dumps({"data": resp, "msg": "SuccessFul"})

    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }