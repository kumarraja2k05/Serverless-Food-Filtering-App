import json
import os
import boto3

QUEUE_ARN = os.getenv("SQSQueue")
table_name = os.getenv("TABLE_NAME")

sqs_client = boto3.client("sqs", "us-west-2")
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    print("ARN: ",QUEUE_ARN)
    table = dynamodb.Table(table_name)
    data = json.loads(event.get("Records")[0].get("body"))
    print("event body: ",event.get("Records")[0].get("body"))
    table.put_item(Item=data)
    sqs_response = sqs_client.receive_message(
        QueueUrl = QUEUE_ARN,
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    record_list = table.scan()
    print("dynamo db records: ",record_list)
    print("\nsqs response: ",sqs_response)
    return {
        "statusCode": 200,
        "body": "Hello New Function!!"
    }