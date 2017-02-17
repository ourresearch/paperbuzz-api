import unittest
from nose.tools import nottest
from nose.tools import assert_equals
from nose.tools import assert_not_equals
from nose.tools import assert_true
import requests
from ddt import ddt, data
import requests_cache


requests_cache.install_cache('requests_cache', expire_after=60*60*24*7)  # expire_after is in seconds

test_dois = [
    ("test", "passes"),
    # ("test", "fails")
]



@ddt
class MyTestCase(unittest.TestCase):
    _multiprocess_can_split_ = True

    @data(*test_dois)
    def test_dois(self, test_data):
        (a, b) = test_data
        assert_equals(a, "test")
        assert_equals(b, "passes")
