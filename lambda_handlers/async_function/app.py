import json
import os
import boto3
from redis import Redis
import logging

redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        data = json.loads(event.get("Records")[0].get("body"))
        logging.info("Event body: ", data)
        redis_conn = Redis(host=redis_host, port=redis_port, db=0)
        logging.info("Redis connection Successful")
        if data["action"] == "delete":
            redis_conn.delete(data["account_id"])
            logging.info("Deleting the cache")
        else:
            logging.info("Cache updated successfully!!")
            del data["action"]
            redis_conn.set(data["account_id"], (str)(data))
    
    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }