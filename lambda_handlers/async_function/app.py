import json
import os
import boto3
from redis import Redis
import logging

redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger()


def lambda_handler(event, context):
    try:
        data = json.loads(event.get("Records")[0].get("body"))
        logging.info("Event body: ", data)
        redis_conn = Redis(host=redis_host, port=redis_port, db=0)
        logging.info("Redis connection Successful")
        cache_key = data.get("owner_id") + "#" + data.get("type")
        if data.get("deleted_date"):
            redis_conn.set(cache_key, (str)(data))
            logging.info("Delete called and Update the cache")
        else:
            redis_conn.set(cache_key, (str)(data))
            logging.info("Cache updated successfully!!")

    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }