import json
import os
import uuid
import boto3

TABLE_NAME = os.getenv("TABLE_NAME", "ShopVerseProducts")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    # Event could be from API Gateway HTTP proxy; parse body safely
    try:
        body = event.get("body") or "{}"
        payload = json.loads(body) if isinstance(body, str) else body
        name = payload.get("name")
        if not name:
            return {"statusCode": 400, "body": json.dumps({"error": "name is required"})}
        product_id = str(uuid.uuid4())
        item = {"product_id": product_id, "name": name}
        table.put_item(Item=item)
        return {"statusCode": 201, "body": json.dumps({"product_id": product_id})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}