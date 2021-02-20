import unittest

from cloudfoundry_client.request_object import Request


class TestRequest(unittest.TestCase):
    def test_mandatory_should_be_present_even_when_none(self):
        request = Request(mandatory=None)
        self.assertTrue("mandatory" in request)
        self.assertIsNone(request["mandatory"])

    def test_optional_should_not_be_present_when_none(self):
        request = Request(mandatory="value")
        request["optional"] = None
        self.assertEqual("value", request["mandatory"])
        self.assertTrue("optional" not in request)
