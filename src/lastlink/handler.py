# import requests
import logging
import json
import os
from urllib.parse import parse_qs
from lastlink.link import Link

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
if os.environ.get('Environment', 'Test') == 'Prod':
    logger.setLevel(logging.INFO)


def params_from_headers(headers, body, queryString):
    # Handles content both as JSON and WWW form - also queryString
    logger.debug(headers)
    logger.debug(body)
    cf = "Content-Type"
    parameters = {}
    if cf not in headers:
        cf = cf.lower()
        if cf not in headers and queryString is None:
            logger.error("Invalid Event: Payload has no Content-Type header")
            raise Exception("Content-Type not found")
    else:
        if headers[cf].startswith("application/x-www-form-urlencoded"):
            parameters = parse_qs(body)
            parameters = dict([(x, y[0]) for x, y in parameters.items()])
        elif headers[cf].startswith("application/json"):
            parameters = json.loads(body)
        else:
            logger.error("Content is of type {} and not supported".format(headers[cf]))
            raise Exception("Unsupported Content Type")
    parameters.update(queryString)
    return parameters


def lambda_handler(event, context):
    if "httpMethod" not in event or "headers" not in event:
        logger.error("Invalid Event Triggered: No HTTP Method and/or headers Found!")
        raise Exception("Invalid Resource")
    try:
        parameters = params_from_headers(event["headers"],
                                         event.get("body", None),
                                         event.get('queryStringParameters', {}))
    except Exception as e:
        raise Exception(e)
    linkId = parameters.get('linkid', 'TEST')
    link = Link(linkId)
    if event['httpMethod'] == 'POST':
        if 'newlink' not in parameters:
            raise Exception("NewLink not set")
        newlink = parameters['newlink']
        link.set_latest_link(newlink)
    elif link.latest_link is None:
        raise Exception("Link ID %s Not Found")
    return {"statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": link["Node"]}
