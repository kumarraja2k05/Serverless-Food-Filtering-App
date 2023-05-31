import json
import unittest
from unittest.mock import call, patch
from lambda_handlers.start_app.app import lambda_handler as app

class TestStartApp(unittest.TestCase):
    payload_event = {
        'resource': '/fwaas/v1/inventory',
        'path': '/fwaas/v1/inventory',
        'httpMethod': 'POST',
        'headers': {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'CloudFront-Forwarded-Proto': 'https',
            'CloudFront-Is-Desktop-Viewer': 'true',
            'CloudFront-Is-Mobile-Viewer': 'false',
            'CloudFront-Is-SmartTV-Viewer': 'false',
            'CloudFront-Is-Tablet-Viewer': 'false',
            'CloudFront-Viewer-ASN': '9498',
            'CloudFront-Viewer-Country': 'IN',
            'Content-Type': 'application/json',
            'Host': 'auhymz4fmb.execute-api.us-west-2.amazonaws.com',
            'Postman-Token': '9ff81be7-c221-47d2-a6c4-29ba5a8ed0d4',
            'User-Agent': 'PostmanRuntime/7.32.2',
            'Via': '1.1 860065ea331017b0ace9fee85adf8e5c.cloudfront.net (CloudFront)',
            'X-Amz-Cf-Id': 'xOJT4Tb_QPDE92Ly4T_fWVWSjW4x0qrsVkqeOOtmVY07IfXs8GPsTA==',
            'X-Amzn-Trace-Id': 'Root=1-6475d822-3113dbab71afe03132279651',
            'X-Forwarded-For': '182.74.58.202, 15.158.41.105',
            'X-Forwarded-Port': '443',
            'X-Forwarded-Proto': 'https'
        },
        'multiValueHeaders': {
            'Accept': ['*/*'],
            'Accept-Encoding': ['gzip, deflate, br'],
            'CloudFront-Forwarded-Proto': ['https'],
            'CloudFront-Is-Desktop-Viewer': ['true'],
            'CloudFront-Is-Mobile-Viewer': ['false'],
            'CloudFront-Is-SmartTV-Viewer': ['false'],
            'CloudFront-Is-Tablet-Viewer': ['false'],
            'CloudFront-Viewer-ASN': ['9498'],
            'CloudFront-Viewer-Country': ['IN'],
            'Content-Type': ['application/json'],
            'Host': ['auhymz4fmb.execute-api.us-west-2.amazonaws.com'],
            'Postman-Token': ['9ff81be7-c221-47d2-a6c4-29ba5a8ed0d4'],
            'User-Agent': ['PostmanRuntime/7.32.2'],
            'Via': ['1.1 860065ea331017b0ace9fee85adf8e5c.cloudfront.net (CloudFront)'],
            'X-Amz-Cf-Id': ['xOJT4Tb_QPDE92Ly4T_fWVWSjW4x0qrsVkqeOOtmVY07IfXs8GPsTA=='],
            'X-Amzn-Trace-Id': ['Root=1-6475d822-3113dbab71afe03132279651'],
            'X-Forwarded-For': ['182.74.58.202, 15.158.41.105'],
            'X-Forwarded-Port': ['443'],
            'X-Forwarded-Proto': ['https']
        },
        'queryStringParameters': None,
        'multiValueQueryStringParameters': None,
        'pathParameters': None,
        'stageVariables': None,
        'requestContext': {
            'resourceId': 'ywycdb',
            'resourcePath': '/fwaas/v1/inventory',
            'httpMethod': 'POST',
            'extendedRequestId': 'Fu61aGUkvHcFVcQ=',
            'requestTime': '30/May/2023:11:04:02 +0000',
            'path': '/Prod/fwaas/v1/inventory',
            'accountId': '901414274132',
            'protocol': 'HTTP/1.1',
            'stage': 'Prod',
            'domainPrefix': 'auhymz4fmb',
            'requestTimeEpoch': 1685444642374,
            'requestId': 'a1dc6b7e-dc9e-432a-af0f-285654878de7',
            'identity': {
                'cognitoIdentityPoolId': None,
                'accountId': None,
                'cognitoIdentityId': None,
                'caller': None,
                'sourceIp': '182.74.58.202',
                'principalOrgId': None,
                'accessKey': None,
                'cognitoAuthenticationType': None,
                'cognitoAuthenticationProvider': None,
                'userArn': None,
                'userAgent': 'PostmanRuntime/7.32.2',
                'user': None
            },
            'domainName': 'auhymz4fmb.execute-api.us-west-2.amazonaws.com',
            'apiId': 'auhymz4fmb'
        },
        'body': '{\r\n\t"action": "add",\r\n\t"account_id": "ACC-100",\r\n\t"type": "fwaas7",\r\n\t"serial_number": "85DEKH",\r\n\t"friendly_name": "Inventory",\r\n\t"quantity": 102,\r\n\t"quantity_used": 21,\r\n\t"start_date": "2019-11-08T01:34:29+00:00",\r\n\t"end_date": "2027-11-08 01:34:29",\r\n\t"data_retention": 97,\r\n\t"is_active": true\r\n}',
        'isBase64Encoded': False
    }
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
