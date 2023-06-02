import json
import os
import boto3
from redis import Redis
from datetime import datetime
import logging

table_name = os.getenv("TABLE_NAME")
ASYNC_QUEUE_ARN = os.getenv("AsyncSQSQueue")

sqs_client = boto3.client("sqs", "us-west-2")
dynamodb = boto3.resource('dynamodb')
redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")
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
        logging.info("Update New License")
        logging.info(f"Redis port: {redis_port}")
        logging.info(f"Redis_host: {redis_host}")
        redis_conn = Redis(host=redis_host, port=redis_port, db=0)
        logging.info("Redis Connection Successful")
        table = dynamodb.Table(table_name)
        data = json.loads(event.get("body"))
        logging.info(f"Event body: {data}")
        curr_time = datetime.now()
        data["updated_at"] = curr_time.strftime("%d-%m-%Y %H:%M:%S")
        owner_id = data["owner_id"]
        sort_key = "LIC#" + data["type"]
        logging.info(f"License id to be updated: {owner_id}")
        if redis_conn.exists(owner_id):
            logging.info("Data found in cache")
            sqs_response = sqs_client.send_message(
                QueueUrl=ASYNC_QUEUE_ARN,
                MessageBody=json.dumps(data)
            )
            logging.info(f"Async SQS response: {sqs_response}")

        resp = table.update_item(
            Key={
                'owner_id': owner_id,
                'sort_key': sort_key
            },
            UpdateExpression='SET quantity = :val1, allocated_date = :val2, quantity_used = :val3, expiry = :val4, updated_at = :val5',
            ExpressionAttributeValues={
                ':val1': data["quantity"],
                ':val2': data["allocated_date"],
                ':val3': data["quantity_used"],
                ':val4': data["expiry"],
                ':val5': data["updated_at"]
            }
        )
        logging.info(f"Update response value is: {resp}")
        record_list = table.query(KeyConditionExpression="owner_id=:pk and sort_key=:sk",ExpressionAttributeValues={':pk': owner_id, ':sk': sort_key})['Items']
        converted_data = decimal_convert(record_list)
        logging.info(f"Updated dynamo db records: {converted_data}")
        return {
            "statusCode": 200,
            "body": json.dumps({"data": converted_data, "msg": "SuccessFul"})
        }
    
    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }