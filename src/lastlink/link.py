import os
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
from lastlink.node import Node

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
if os.environ.get('Environment', 'Test') == 'Prod':
    logger.setLevel(logging.INFO)


class Link():

    ddb = boto3.resource('dynamodb')
    table = ddb.Table('LastLinkTable')

    def __init__(self, linkId):
        self.linkId = linkId
        self.latest_link = self.get_latest_link()

    def __getitem__(self, item):
        return self.latest_link[item]

    def get_latest_link(self, limit=1):
        limit = min(limit, 10)
        latest_link = self.table.query(
            KeyConditionExpression=Key("LinkId").eq(self.linkId),
            ScanIndexForward=False,
            Limit=limit)
        logger.debug(latest_link)
        if len(latest_link.get('Items', [])) == 0:
            return None
        return latest_link['Items'][0]

    def is_node_in_chain(self, node):
        upstream = [node.parent, node.prev, node.name]
        link = self.table.query(
            KeyConditionExpression=Key("LinkId").eq(self.linkId),
            FilterExpression=Attr('Node').is_in(upstream),
            ScanIndexForward=False,
            Limit=3)
        logger.debug("Searching chain for node link: %s", node.name)
        logger.debug("Found link %s", link)
        return len(link['Items']) == 2

    def set_latest_link(self, newlink):
        latest_index = self.latest_link['NodeIndex'] + 1
        node = Node(newlink)
        if not node:
            raise Exception("Cannot parse new link")
        if (node.parent == 'ROOT' and node.prev == 'ROOT') \
           or node.override \
           or not (self.is_node_in_chain(node)):
            raise Exception("Parents or Previous node not in Chain")
        new_latest = {
            'LinkId': self.linkId,
            'NodeIndex': latest_index,
            'Node': newlink
        }
        try:
            self.table.put_item(Item=new_latest)
            self.latest_link = new_latest
        except Exception:
            self.get_latest_link()
