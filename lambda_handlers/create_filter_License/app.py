import json
import os
import boto3
from datetime import datetime
import logging

table_name = os.getenv("TABLE_NAME")
sqs_client = boto3.client("sqs", "us-west-2")
dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def decimal_convert(record):
    resp = {}
    for item in record:
        for key, val in item.items():
            resp[key] = (str)(val)

    return resp


def lambda_handler(event, context):
    try:
        table = dynamodb.Table(table_name)
        data = json.loads(event.get("body"))
        logging.info(f"event body {data}")
        logging.info("Create New License!!")
        account_id = data["account_id"]
        data["sort_key"] = data["serial_number"] + "#" + data["type"]
        del data["action"]
        curr_time = datetime.now()
        data["created_at"] = curr_time.strftime("%d-%m-%Y %H:%M:%S")
        data["updated_at"] = curr_time.strftime("%d-%m-%Y %H:%M:%S")
        logging.info(f"Data to be created in DynamoDb: {data}")
        table.put_item(Item=data)
        record_list = record = table.query(KeyConditionExpression="account_id=:pk", ExpressionAttributeValues={':pk': account_id})['Items']
        res = decimal_convert(record_list)
        logging.info(f"New License DynamoDb records: {res}")
        return {
            "statusCode": 200,
            "body": json.dumps({"data": res, "msg": "SuccessFul"})
        }
    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }