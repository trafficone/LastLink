import unittest
from mock import MagicMock
import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/..')
import lastlink.node as n

known_good_json_node = 'http://sprunge.us/XzqDTN'
known_bad_url = 'http://badurl.badurl'


class TestGoodNode(unittest.TestCase):
    test_node = n.Node(known_good_json_node)

    def test_valid_node(self):
        assert self.test_node.valid == True

    def test_init_n(self):
        assert isinstance(self.test_node,n.Node)

    def test_node_attrs(self):
        attrs = ['name','parent','prev','valid','type']
        for attr in attrs:
            assert attr in dir(self.test_node)


