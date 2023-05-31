import json
import unittest
from unittest.mock import call, patch
from lambda_handlers.manager_function.app import lambda_handler as app
from helpers.load_json import JsonLoader

class TestManagerFunction(unittest.TestCase):
    add_payload_event = JsonLoader().load_add_endpoint_json()

    add_reponse = {
        'data': {
            'quantity': '102',
            'created_at': '31-05-2023 04:08:12',
            'end_date': '2027-11-08 01:34:29',
            'friendly_name': 'Inventory',
            'data_retention': '97',
            'quantity_used': '21',
            'sort_key': '85DEKH#fwaas7',
            'account_id': 'ACC-100',
            'serial_number': '85DEKH',
            'updated_at': '31-05-2023 04:08:12',
            'start_date': '2019-11-08T01:34:29+00:00',
            'is_active': 'True',
            'type': 'fwaas7'
        },
        "msg": "SuccessFul"
    }
    

    
    api_url = "https://lsu3y25nyg.execute-api.us-west-2.amazonaws.com/Dev/fwaas/v1/inventory/add"

    @patch("lambda_handlers.manager_function.app.requests")
    def test_add_logic(self, m_requests):
        m_requests.post.return_value.json.return_value = TestManagerFunction.add_reponse
        res = app(TestManagerFunction.add_payload_event, "")
        m_requests.post.assert_called_with(TestManagerFunction.api_url,json=json.loads(TestManagerFunction.add_payload_event.get("Records")[0].get("body")))
        data = json.loads(res)
        assert data["data"] == TestManagerFunction.add_reponse["data"]
        assert data["msg"] == "SuccessFul"

    # @patch("lambda_handlers.manager_function.app.api_url")
    # @patch("lambda_handlers.manager_function.app.requests")
    # def test_update_logic(self, m_requests, m_api_url):
    #     m_api_url.return_value = TestManagerFunction.api_url
    #     m_requests.post.return_value.json.return_value = TestManagerFunction.add_reponse

