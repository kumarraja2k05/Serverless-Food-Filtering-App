import json
import os
import boto3

TOPIC_ARN = os.getenv("SNStopic")

sns_client = boto3.client("sns", "us-west-2")

def lambda_handler(event, context):
    food_payload = json.loads(event.get('body'))
    print("payload is: ", food_payload)
    print("\ntopic arn: ", TOPIC_ARN)
    required_method = food_payload["request_type"].lower()
    print("required method is of type: ", required_method)
    if required_method == "insert":
        print("Reached Insert!!")
    elif required_method == "update":
        print("Reached Update!!")
    elif required_method == "delete":
        print("Reached delete!!")
    else:
        print("Wrong HTTP method recieved!!")
    sns_response = sns_client.publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps(food_payload)
    )
    print("\nsns response: ",sns_response)
    return {
        "statusCode": 200,
        "body": json.dumps("SuccessFul")
    }