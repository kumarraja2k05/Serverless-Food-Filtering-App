import json
import os
import boto3

TOPIC_ARN = os.getenv("SNStopic")

sns_client = boto3.client("sns", "us-west-2")

def lambda_handler(event, context):
    payload = json.loads(event.get('body'))
    print("payload is: ", payload)
    print("\ntopic arn: ", TOPIC_ARN)
    sns_response = sns_client.publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps(payload)
    )
    print("\nsns response: ",sns_response)
    return {
        "statusCode": 200,
        "body": json.dumps("SuccessFul")
    }