import json

def lambda_handler(event, context):
    a = {"message": "hello world"}
    return {
        "statusCode": 200,
        "body": json.dumps(a),
        "headers": {
            "content-type": "application/json"
        }
    }