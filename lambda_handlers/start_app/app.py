import json
import os
import boto3
import logging

TOPIC_ARN = os.getenv("SNStopic")
sns_client = boto3.client("sns", "us-west-2")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        payload = json.loads(event.get('body'))
        logger.info(f"Payload is {payload}")
        logger.info(f"Topic arn is {TOPIC_ARN} ")
        sns_response = sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(payload)
        )
        logger.info(f"sns response {sns_response}")
        return {
            "statusCode": 200,
            "body": json.dumps("SuccessFul")
        }
    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }

