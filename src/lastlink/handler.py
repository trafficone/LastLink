# import requests
import logging
import boto3
import json
from urllib.parse import parse_qs

logger = logging.getLogger()
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

ddb = boto3.resource('dynamodb')


def params_from_headers(headers, body):
    # Handles content both as JSON and WWW form
    cf = "Content-Type"
    if cf not in headers:
        cf = cf.lower()
        if cf not in headers:
            logger.error("Invalid Event: Paylad has not Content-Type header")
            raise Exception("Content-Type not found")
    if headers[cf].startswith("application/x-www-form-urlencoded"):
        parameters = parse_qs(body)
        parameters = dict([(x, y[0]) for x, y in parameters.items()])
    elif headers[cf].startswith("application/json"):
        parameters = json.loads(body)
    else:
        logger.error("Content is of type {} and not supported".format(headers[cf]))
        raise Exception("Unsupported Content Type")
    return parameters


def get_latest_link(linkId):
    latest_link = ddb.query(
        TableName='LastLinkTable',
        KeyConditions={"LinkId": {
                        "ComparisonOperator": "EQ",
                        "AttributeValueList": [{"S": linkId}]}},
        ScanIndexForward=True,
        Limit=1)
    if latest_link == {}:
        raise Exception("Link ID %s Not Found" % linkId)
    return latest_link


def set_latest_link(linkId, latest_link, newlink):
    latest_index = latest_link['NodeIndex'] + 1
    new_latest = {
        'LinkId': linkId,
        'NodeIndex': latest_index,
        'Node': newlink
    }
    table = ddb.table('LastLinkTable')
    table.putItem(new_latest)


def lambda_handler(event, context):
    if "httpMethod" not in event or "headers" not in event:
        logger.error("Invalid Event Triggered: No HTTP Method and/or headers Found!")
        # return server_error_reply("Invalid Resource")
        raise Exception("Invalid Resource")
    try:
        parameters = params_from_headers(event["headers"], event.get("body", None))
    except Exception as e:
        # return server_error_reply(e)
        raise Exception(e)
    linkId = parameters.get('linkid', 'TEST')
    link = get_latest_link(linkId)
    if event['httpMethod'] == 'POST':
        if 'newlink' not in parameters:
            raise Exception("NewLink not set")
        newlink = parameters['newlink']
        link = set_latest_link(linkId, link, newlink)
    return {"statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": link["Node"]}
