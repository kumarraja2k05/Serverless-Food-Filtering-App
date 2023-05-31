import json

class JsonLoader:
    def load_add_endpoint_json(self):
        with open('C:\\Users\\kraja\\Watchguard Work\\POC\\License Management System\\Serverless-Food-Filtering-App\\common_events\\add_endpoint.json') as file:
            data = json.load(file)
            return data
