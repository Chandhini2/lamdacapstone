import os
import json

def lambda_handler(event, context):
    # S3 trigger will send records; just log for now
    records = event.get("Records", [])
    info = [{"bucket": r["s3"]["bucket"]["name"], "key": r["s3"]["object"]["key"]} for r in records]
    return {"statusCode": 200, "body": json.dumps({"received": info})}