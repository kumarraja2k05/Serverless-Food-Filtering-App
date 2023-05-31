import json
import os
import boto3
import requests

region = os.getenv("Region")
logical_id = os.getenv("Logical_ID")
api_url = os.getenv("API_URL")
<<<<<<< Updated upstream
sqs_client = boto3.client("sqs", "us-west-2")

def lambda_handler(event, context):
    global api_url
    print("ARN: ",QUEUE_ARN)
    data = json.loads(event.get("Records")[0].get("body"))
    print("event body: ",data)
    print("Api url: ",api_url)
    required_method = data["request_type"].lower()
    food_id = data["food_item_id"]
    if required_method == "create":
        print("Create New Food")
        response = requests.post(api_url, json=data)
        print("response value: ",response.json())
    elif required_method == "delete":
        print("Delete Food")
        # api_url = f"{api_url}/{food_id}"
        response = requests.delete(api_url,data={"id":food_id,"category": data["category"],"request_type":required_method})
        print("response value: ",response.json())
    elif required_method == "update":
        print("Update Food")
        response = requests.put(api_url, json=data)
        print("response value: ",response.json())
    else:
        print("Please specify request_type as [insert, update, delete]")
    return json.dumps({"msg": "SuccessFul"})
=======
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        data = json.loads(event.get("Records")[0].get("body"))
        logger.info(f"Event body {data}")
        required_method = data["action"].lower()
        account_id = data["account_id"]
        resp = None
        if required_method == "add":
            logger.info("Create New License")
            url = api_url + "/add"
            logger.info(f"Add Api url {url}")
            response = requests.post(url, json=data).json()
            logger.info(f"Create License response value {response}")
            resp = response
        elif required_method == "delete":
            logger.info("Delete License")
            url = api_url + "/delete"
            logger.info(f"Delete Api url {url}")
            response = requests.delete(url,data={"id":account_id,"serial_number": data["serial_number"], "type": data["type"], "action":required_method})
            logger.info(f"Delete License response value {response.json()}")
            resp = response.json()
        elif required_method == "update":
            logger.info("Update License")
            url = api_url + "/update"
            logger.info(f"Update Api url {url}")
            response = requests.put(url, json=data)
            logger.info(f"Update License response value {response.json()}")
            resp = response.json()
        else:
            logger.info("Please specify request_type as [add, update, delete]")
        return json.dumps(resp)
    
    except ValueError as e:
        logger.error(e)
        return {
            "statusCode": 502,
            "body": json.dumps({"error": str(e)})
        }
>>>>>>> Stashed changes
