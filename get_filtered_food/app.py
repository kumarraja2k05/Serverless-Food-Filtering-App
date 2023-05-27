import json
import os
import boto3
import ast
from redis import Redis

table_name = os.getenv("TABLE_NAME")
QUEUE_ARN = os.getenv("AsyncSQSQueue")
dynamodb = boto3.resource('dynamodb')
redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")
sqs_client = boto3.client("sqs", "us-west-2")


def decimal_convert(record):
    resp = {}
    for item in record:
        for key, val in item.items():
            resp[key] = (str)(val)

    return resp

def lambda_handler(event, context):
    table = dynamodb.Table(table_name)
    print("ARN: ", QUEUE_ARN)
    food_id = (int)(event.get('queryStringParameters').get('id'))
    print("redis port: ", redis_port)
    print("redis_host: ", redis_host)
    redis_conn = Redis(host=redis_host, port=redis_port, db=0)
    print("Redis Connection Successfull!!")
    res = {}
    if redis_conn.exists(food_id):
        print("Data found in cache")
        cache_data = redis_conn.get(food_id)
        res = ast.literal_eval(cache_data.decode('utf-8'))
        print("Cache get value: ", res)

    else:
        record = table.query(KeyConditionExpression="food_item_id=:pk", ExpressionAttributeValues={':pk': food_id})['Items']
        res = decimal_convert(record)
        print("Data not found in cache,Fetching Data From DYnamoDB")
        print("DynamoDB response: ", res)
        sqs_response = sqs_client.send_message(
            QueueUrl=QUEUE_ARN,
            MessageBody=json.dumps(res)
        )
        print("sqs response: ", sqs_response)

    return {
        "statusCode": 200,
        "body": json.dumps(res)
    }