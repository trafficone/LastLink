import os
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
if os.environ.get('Environment', 'Test') == 'Prod':
    logger.setLevel(logging.INFO)

# Known Node Types
INVALID = 'invalid'
JSON    = 'json'
JPEG    = 'jpeg'
PICKLE  = 'pickle'


class Node():

    def __init__(self, node_url):
        self.name = node_url
        self.mark_invalid()
        self.override = False
        try:
            r = requests.get(node_url)
            r.raise_for_status()
        except Exception:
            return
        if not r:
            return
        try:
            node_data = r.json()
            self.json_node(node_data)
            return
        except Exception:
            logger.debug("Node not JSON type")
        try:
            node_data = r.content
            test = bytes([x[0]&x[1] for x in zip(node_data[0:10],b'\xff\xff\x00\x00'+b'\xff'*4)])
            jpeg_header = '\xFF\xE0\x00x00JFIF'
            if test == jpeg_header:
                self.jpeg_node(node_data)
                return
        except Exception:
            logger.debug("Node not JPEG type")
        raise Exception("Unable to determine Node type")


    def jpeg_node(self,data):
        # TODO: Implement JPEG Node processor
        self.valid = True
        self.override = True
        self.type = JPEG

    def json_node(self, data):
        if 'timestamp' not in data or \
           'parent' not in data or \
           'prev' not in data or \
           'payload' not in data:
            raise Exception("JSON data is not a node")
        self.valid = True
        self.type = JSON
        self.timestamp = data['timestamp']
        self.parent = data['parent']
        self.prev = data['prev']
        self.payload = data['payload']

    def mark_invalid(self):
        self.valid  = False
        self.parent = None
        self.prev   = None
        self.pyload = None
        self.type   = INVALID

    def __bool__(self):
        """
        Validate node is part of a network.
        """
        return self.valid
