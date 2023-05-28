import json
import os
import boto3
from redis import Redis

table_name = os.getenv("TABLE_NAME")
ASYNC_QUEUE_ARN = os.getenv("AsyncSQSQueue")

sqs_client = boto3.client("sqs", "us-west-2")
dynamodb = boto3.resource('dynamodb')
redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")

def lambda_handler(event, context):
    redis_conn = Redis(host=redis_host, port=redis_port, db=0)
    print("Redis Connection Successfull!!")
    table = dynamodb.Table(table_name)
    print("Delete New Food!!")
    print("event body: ",event.get("body"))
    resp = event.get("body").split("&")
    print("response: ",resp)
    food_id = (int)(resp[0].replace("id=",""))
    request_type = resp[2].replace("request_type=","")
    category = resp[1].replace("category=","").replace("+"," ")
    data = {"food_item_id": food_id,"request_type":request_type, "category": category}
    print("data: ",data)
    print("Food id to be deleted", type(food_id))
    if redis_conn.exists(food_id):
        print("Data found in cache")
        sqs_response = sqs_client.send_message(
            QueueUrl=ASYNC_QUEUE_ARN,
            MessageBody=json.dumps(data)
        )
        print("sqs response: ", sqs_response)
    key = {"food_item_id": food_id, "category": data["category"]}
    record_list = table.delete_item(Key=key)
    print("Delete dynamo db records: ",record_list)
    return {
        "statusCode": 200,
        "body": json.dumps({"msg": "SuccessFul"})
    }