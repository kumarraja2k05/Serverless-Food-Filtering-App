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
    print("redis port: ", redis_port)
    print("redis_host: ", redis_host)
    redis_conn = Redis(host=redis_host, port=redis_port, db=0)
    print("Redis Connection Successfull!!")
    table = dynamodb.Table(table_name)
    print("Update New Food!!")
    data = json.loads(event.get("body"))
    print("event body: ",data)
    food_id = data["food_item_id"]
    print("Food id to be updated", type(food_id))
    if redis_conn.exists(food_id):
        print("Data found in cache")
        sqs_response = sqs_client.send_message(
            QueueUrl=ASYNC_QUEUE_ARN,
            MessageBody=json.dumps(data)
        )
        print("sqs response: ", sqs_response)

    # table.put_item(Item=data)
    resp = table.update_item(
        Key={
            'food_item_id': food_id,
            'category': data["category"]
        },
        UpdateExpression = 'SET calory = :val1, request_type= :val2',
        ExpressionAttributeValues={
            ':val1': data["calory"],
            ':val2': data["request_type"]
         }
    )
    print("Update response value is: ", resp)
    record_list = table.query(KeyConditionExpression="food_item_id=:pk", ExpressionAttributeValues={':pk': food_id})['Items']
    print("Updated dynamo db records: ",record_list)
    return {
        "statusCode": 200,
        "body": json.dumps({"msg": "SuccessFul"})
    }