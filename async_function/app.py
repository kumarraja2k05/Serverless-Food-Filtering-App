import json
import os
import boto3
from redis import Redis

redis_port = os.getenv("REDIS_PORT")
redis_host = os.getenv("REDIS_HOST")

def lambda_handler(event, context):
    data = json.loads(event.get("Records")[0].get("body"))
    print("event body: ", data)
    redis_conn = Redis(host=redis_host, port=redis_port, db=0)
    print("redis response: ", redis_conn)
    redis_conn.set(data["food_item_id"],(str)(data))
    print("Cache updated successfully!!")