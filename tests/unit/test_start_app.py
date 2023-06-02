import json
import unittest
from unittest.mock import call, patch
from lambda_handlers.start_app.app import lambda_handler as app
from helpers.load_json import JsonLoader
class TestStartApp(unittest.TestCase):
    payload_event = JsonLoader().load_start_app_json()
    request_body = {
        "action": "add",
        "account_id": "ACC-100",
        "type": "fwaas7",
        "serial_number": "85DEKH",
        "friendly_name": "Inventory",
        "quantity": 102,
        "quantity_used": 21,
        "start_date": "2019-11-08T01:34:29+00:00",
        "end_date": "2027-11-08 01:34:29",
        "data_retention": 97,
        "is_active": True
    }
    
    TOPIC_ARN = "arn:aws:sns:us-west-2:901414274132:LicenseSelection"
    
    @patch("lambda_handlers.start_app.app.sns_client")
    def test_start_app_function(self,m_sns_client):
        sns_response = m_sns_client.publish(
            TopicArn=TestStartApp.TOPIC_ARN,
            Message=json.dumps(TestStartApp.request_body)
        )
        res = app(TestStartApp.payload_event,"")
        print("reponse: ",res)
        data = json.loads(res["body"])
        print("reponse recieved: ", data)
        assert res["statusCode"] == 200
        # assert "message" in ret["body"]
        assert data == "SuccessFul"
