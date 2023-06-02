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
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger()

def lambda_handler(event, context):
    try:
        logging.info("Delete New License!!")
        redis_conn = Redis(host=redis_host, port=redis_port, db=0)
        logging.info("Redis Connection Successful")
        table = dynamodb.Table(table_name)
        logging.info(f"Event body: ",event.get("body"))
        data = json.loads(event.get("body"))
        logging.info(f"Splitted response data {data}")
        if data.get("deleted_account_ids") is not None:
            for details in data.get("deleted_account_ids"):
                owner_id = details[0]
                sort_key = "LIC#" + details[1]
                cache_key = owner_id + "#" + details[1]
                if redis_conn.exists(cache_key):
                    logging.info("Data found in cache")
                    data["is_active"] = False
                    sqs_response = sqs_client.send_message(
                        QueueUrl=ASYNC_QUEUE_ARN,
                        MessageBody=json.dumps(data)
                    )
                    logging.info(f"Async SQS response: {sqs_response}")

                record_list = table.update_item(
                    Key={
                        'owner_id': owner_id,
                        'sort_key': sort_key
                    },
                    UpdateExpression='SET is_active = :val1, deleted_date = :val2',
                    ExpressionAttributeValues={
                        ':val1': False,
                        ':val2': data["deleted_date"]
                    }
                )
                logging.info(f"Updated dynamo db records reponse: {record_list}")
        else:
            owner_id = data.get("owner_id")
            license_type = data.get("type")
            cache_key = owner_id + "#" + license_type
            if redis_conn.exists(cache_key):
                logging.info("Data found in cache")
                sqs_response = sqs_client.send_message(
                    QueueUrl=ASYNC_QUEUE_ARN,
                    MessageBody=json.dumps(data)
                )
                logging.info(f"Async SQS response: {sqs_response}")
            sort_key = "LIC#" + data.get("type")
            key = {"owner_id": owner_id, "sort_key": sort_key}
            record_list = table.update_item(
                Key={
                    'owner_id': owner_id,
                    'sort_key': sort_key
                },
                UpdateExpression='SET quantity = :val1, deleted_date = :val2',
                ExpressionAttributeValues={
                    ':val1': data["quantity"],
                    ':val2': data["deleted_date"]
                }
            )
            logging.info(f"Updated dynamo db records reponse: {record_list}")
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