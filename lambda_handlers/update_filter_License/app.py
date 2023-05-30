import json
import os
import boto3
from redis import Redis
from datetime import datetime

table_name = os.getenv("TABLE_NAME")
ASYNC_QUEUE_ARN = os.getenv("AsyncSQSQueue")

sqs_client = boto3.client("sqs", "us-west-2")
dynamodb = boto3.resource('dynamodb')
redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")


def decimal_convert(record):
    resp = {}
    for item in record:
        for key, val in item.items():
            resp[key] = (str)(val)

    return resp


def lambda_handler(event, context):
    print("redis port: ", redis_port)
    print("redis_host: ", redis_host)
    redis_conn = Redis(host=redis_host, port=redis_port, db=0)
    print("Redis Connection Successfull!!")
    table = dynamodb.Table(table_name)
    print("Update New License!!")
    data = json.loads(event.get("body"))
    print("event body: ", data)
    curr_time = datetime.now()
    data["updated_at"] = curr_time.strftime("%d-%m-%Y %H:%M:%S")
    del data["action"]
    account_id = data["account_id"]
    print("License id to be updated", type(account_id))
    if redis_conn.exists(account_id):
        print("Data found in cache")
        data["action"] = "update"
        sqs_response = sqs_client.send_message(
            QueueUrl=ASYNC_QUEUE_ARN,
            MessageBody=json.dumps(data)
        )
        print("sqs response: ", sqs_response)

    resp = table.update_item(
        Key={
            'account_id': account_id,
            'sort_key': data["serial_number"] + "#" + data["type"]
        },
        UpdateExpression='SET quantity = :val1, data_retention = :val2, quantity_used = :val3, friendly_name = :val4, start_date = :val5, is_active = :val6, end_date = :val7',
        ExpressionAttributeValues={
            ':val1': data["quantity"],
            ':val2': data["data_retention"],
            ':val3': data["quantity_used"],
            ':val4': data["friendly_name"],
            ':val5': data["start_date"],
            ':val6': data["is_active"],
            ':val7': data["end_date"]
        }
    )
    print("Update response value is: ", resp)
    record_list = table.query(KeyConditionExpression="account_id=:pk", ExpressionAttributeValues={':pk': account_id})[
        'Items']
    res = decimal_convert(record_list)
    print("Updated dynamo db records: ", res)
    return {
        "statusCode": 200,
        "body": json.dumps({"data": res, "msg": "SuccessFul"})
    }