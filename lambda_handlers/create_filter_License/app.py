import json
import os
import boto3
from datetime import datetime

table_name = os.getenv("TABLE_NAME")

sqs_client = boto3.client("sqs", "us-west-2")
dynamodb = boto3.resource('dynamodb')


def decimal_convert(record):
    resp = {}
    for item in record:
        for key, val in item.items():
            resp[key] = (str)(val)

    return resp


def lambda_handler(event, context):
    table = dynamodb.Table(table_name)
    data = json.loads(event.get("body"))
    print("event body: ", data)
    print("event type: ", type(event.get("body")))
    print("Create New License!!")
    account_id = data["account_id"]
    data["sort_key"] = data["serial_number"] + "#" + data["type"]
    del data["action"]
    curr_time = datetime.now()
    data["created_at"] = curr_time.strftime("%d-%m-%Y %H:%M:%S")
    data["updated_at"] = curr_time.strftime("%d-%m-%Y %H:%M:%S")
    print("partition key: ", data["account_id"])
    print("sort key: ", data["sort_key"])
    print("whole data to be pushed: ", data)
    table.put_item(Item=data)
    record_list = record = table.query(KeyConditionExpression="account_id=:pk", ExpressionAttributeValues={':pk': account_id})['Items']
    res = decimal_convert(record_list)
    print("New dynamo db records: ", res)
    return {
        "statusCode": 200,
        "body": json.dumps({"data": res, "msg": "SuccessFul"})
    }