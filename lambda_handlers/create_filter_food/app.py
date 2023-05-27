import json
import os
import boto3

table_name = os.getenv("TABLE_NAME")

sqs_client = boto3.client("sqs", "us-west-2")
dynamodb = boto3.resource('dynamodb')
def lambda_handler(event, context):
    table = dynamodb.Table(table_name)
    data = json.loads(event.get("body"))
    print("event body: ",data)
    print("event type: ",type(event.get("body")))
    print("Create New Food!!")
    food_id = data["food_item_id"]
    table.put_item(Item=data)
    record_list = record = table.query(KeyConditionExpression="food_item_id=:pk", ExpressionAttributeValues={':pk': food_id})['Items']
    print("New dynamo db records: ", record_list)
    return {
        "statusCode": 200,
        "body": json.dumps("SuccessFul")
    }