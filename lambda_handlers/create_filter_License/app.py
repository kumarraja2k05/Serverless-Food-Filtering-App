import json
import os
import boto3
from datetime import datetime
import logging
from redis import Redis

table_name = os.getenv("TABLE_NAME")
ASYNC_QUEUE_ARN = os.getenv("AsyncSQSQueue")
sqs_client = boto3.client("sqs", "us-west-2")
dynamodb = boto3.resource('dynamodb')
redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger()

table = dynamodb.Table(table_name)


def decimal_convert(record):
    resp = {}
    for item in record:
        for key, val in item.items():
            resp[key] = (str)(val)

    return resp


def get_data_dynamoDB(owner_id, type, res=None):
    sort_key = "LIC#" + type
    record_list = table.query(KeyConditionExpression="owner_id=:pk and sort_key=:sk",
                              ExpressionAttributeValues={':pk': owner_id, ':sk': sort_key})['Items']
    res = decimal_convert(record_list)
    logging.info(f"Fetching DynamoDb records: {res}")
    return res


def update_new_license(owner_id, data, redis_conn, curr_time):
    logging.info("Update New License")
    logging.info(f"Redis port: {redis_port}")
    logging.info(f"Redis_host: {redis_host}")
    logging.info("Redis Connection Successful")
    data["updated_at"] = curr_time.strftime("%d-%m-%Y %H:%M:%S")
    logging.info(f"License id to be updated: {owner_id}")
    cache_key = owner_id + "#" + data.get("type")
    if redis_conn.exists(cache_key):
        logging.info("Data found in cache")
        sqs_response = sqs_client.send_message(
            QueueUrl=ASYNC_QUEUE_ARN,
            MessageBody=json.dumps(data)
        )
        logging.info(f"Async SQS response: {sqs_response}")
    sort_key = "LIC#" + data.get("type")
    resp = table.update_item(
        Key={
            'owner_id': owner_id,
            'sort_key': sort_key
        },
        UpdateExpression='SET quantity = :val1, allocated_date = :val2, expiry = :val3, updated_at = :val4',
        ExpressionAttributeValues={
            ':val1': data["quantity"],
            ':val2': data["allocated_date"],
            ':val3': data["expiry"],
            ':val4': data["updated_at"]
        }
    )
    return resp


def create_new_license(data, curr_time):
    logging.info("Create New License")
    data["created_at"] = curr_time.strftime("%d-%m-%Y %H:%M:%S")
    data["updated_at"] = curr_time.strftime("%d-%m-%Y %H:%M:%S")
    data["is_active"] = True
    data["sort_key"] = "LIC#" + data.get("type")
    logging.info(f"Data to be created in DynamoDb: {data}")
    resp = table.put_item(Item=data)
    return resp


def delete_individual_License(data, redis_conn):
    logging.info("Reached Delete single account scenario")
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
    return record_list


def delete_multiple_accounts(data, redis_conn):
    logging.info("Reached multiple account scenario")
    for details in data.get("deleted_account_ids"):
        owner_id = details[0]
        sort_key = "LIC#" + details[1]
        cache_key = owner_id + "#" + details[1]
        logging.info(f"owner_id: {owner_id} , sort_key: {sort_key} , cache_key: {cache_key}")
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
        logging.info(f"Delete Multiple License dynamo db records reponse: {record_list}")


def lambda_handler(event, context):
    try:
        data = json.loads(event.get("body"))
        logging.info(f"event body {data}")
        redis_conn = Redis(host=redis_host, port=redis_port, db=0)
        dynamo_db_respone = {}
        if data.get("allocated_date"):
            curr_time = datetime.now()
            owner_id = data.get("owner_id")
            logging.info("DynamoDb Records Before pushing")
            res_dynamo_db = get_data_dynamoDB(owner_id, data.get("type"))
            if res_dynamo_db != {}:
                resp = update_new_license(owner_id, data, redis_conn, curr_time)
                logging.info(f"Update License response value is: {resp}")
                dynamo_db_respone = get_data_dynamoDB(data.get("owner_id"), data.get("type"))
            else:
                resp = create_new_license(data, curr_time)
                logging.info(f"Create License response value is: {resp}")
                dynamo_db_respone = get_data_dynamoDB(data.get("owner_id"), data.get("type"))
        elif data.get("deleted_date"):
            if data.get("deleted_account_ids") is not None:
                delete_multiple_accounts(data, redis_conn)
            else:
                resp = delete_individual_License(data, redis_conn)
                logging.info(f"Delete Single License dynamo db records reponse: {resp}")
                dynamo_db_respone = get_data_dynamoDB(data.get("owner_id"), data.get("type"))

        logging.info(f"DynamoDb Records After pushing: {dynamo_db_respone}")
        return {
            "statusCode": 200,
            "body": json.dumps({"data": dynamo_db_respone, "msg": "SuccessFul"})
        }
    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }