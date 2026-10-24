import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def json_log(message, **fields):
    logger.info(json.dumps({
        "message": message,
        **fields
    }))
