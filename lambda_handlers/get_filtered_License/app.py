import json
import os
import boto3
import ast
from redis import Redis
import logging

table_name = os.getenv("TABLE_NAME")
QUEUE_ARN = os.getenv("AsyncSQSQueue")
dynamodb = boto3.resource('dynamodb')
redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")
sqs_client = boto3.client("sqs", "us-west-2")
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
        logging.info(f"Queue ARN: {QUEUE_ARN}")
        account_id = event.get('queryStringParameters').get('id')
        logging.info(f"Redis port: {redis_port}")
        logging.info(f"Redis_host: {redis_host}")
        redis_conn = Redis(host=redis_host, port=redis_port, db=0)
        logging.info("Redis Connection Successfull!!")
        res = {}
        if redis_conn.exists(account_id):
            logging.info("Data found in cache")
            cache_data = redis_conn.get(account_id)
            res = ast.literal_eval(cache_data.decode('utf-8'))
            logging.info(f"Cache get value: {res}")

        else:
            logging.info("Data not found in cache,Fetching Data From DYnamoDB")
            record = table.query(KeyConditionExpression="account_id=:pk", ExpressionAttributeValues={':pk': account_id})['Items']
            res = decimal_convert(record)
            logging.info(f"DynamoDB response: {res}")
            res["action"] = "update"
            sqs_response = sqs_client.send_message(
                QueueUrl=QUEUE_ARN,
                MessageBody=json.dumps(res)
            )
            logging.info(f"sqs response: {sqs_response}")

        return {
            "statusCode": 200,
            "body": json.dumps(res)
        }
    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }