import json
import os
import boto3
from redis import Redis
import logging

table_name = os.getenv("TABLE_NAME")
ASYNC_QUEUE_ARN = os.getenv("AsyncSQSQueue")

sqs_client = boto3.client("sqs", "us-west-2")
dynamodb = boto3.resource('dynamodb')
redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logging.info("Delete New License!!")
        redis_conn = Redis(host=redis_host, port=redis_port, db=0)
        logging.info("Redis Connection Successful")
        table = dynamodb.Table(table_name)
        logging.info(f"Event body: ",event.get("body"))
        resp = event.get("body").split("&")
        logging.info(f"Splitted response data {resp}")
        account_id = resp[0].replace("id=","")
        serial_number = resp[1].replace("serial_number=","")
        request_type = resp[2].replace("type=","")
        action = resp[3].replace("action=","")
        data = {"account_id": account_id,"serial_number":serial_number, "type": request_type, "action": action}
        logging.info(f"Data recieved from request: {data}")
        if redis_conn.exists(account_id):
            logging.info("Data found in cache")
            sqs_response = sqs_client.send_message(
                QueueUrl=ASYNC_QUEUE_ARN,
                MessageBody=json.dumps(data)
            )
            logging.info(f"Async SQS response: {sqs_response}")
        data["sort_key"] = data["serial_number"] + "#" + data["type"]
        key = {"account_id": account_id, "sort_key": data["sort_key"]}
        record_list = table.delete_item(Key=key)
        logging.info(f"Delete dynamo db records reponse: {record_list}")
        return {
            "statusCode": 200,
            "body": json.dumps({"data": record_list,"msg": "SuccessFul"})
        }
    
    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }