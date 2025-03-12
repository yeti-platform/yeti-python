import os
import time
import unittest
from unittest.mock import MagicMock, patch

import requests

from yeti import errors
from yeti.api import YetiApi

# os.environ["YETI_ENDPOINT"] = "http://dev-frontend-1:3000"
# os.environ["YETI_API_KEY"] = (
#     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGVzdGluZyIsInN1YiI6InlldGkiLCJzY29wZXMiOlsiYWxsIl0sImNyZWF0ZWQiOiIyMDI1LTAzLTExVDIzOjQ1OjU5Ljg3OTQ1OVoiLCJleHAiOm51bGwsImxhc3RfdXNlZCI6bnVsbCwiZW5hYmxlZCI6dHJ1ZSwiZXhwaXJlZCI6ZmFsc2V9.yTidlJ5r8mURLpV9ER3APpO5MlPoG30Z0PqtMLbY1Vg"
# )


class YetiEndToEndTest(unittest.TestCase):
    def setUp(self):
        self.api = YetiApi(os.getenv("YETI_ENDPOINT"))

    def test_auth_api_key(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        self.api.search_indicators(name="test")

    def test_no_auth(self):
        with self.assertRaises(errors.YetiAuthError) as error:
            self.api.search_indicators(name="test")
        self.assertIn(
            "401 Client Error: Unauthorized for url: ",
            str(error.exception),
        )

    def test_new_indicator(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        indicator = self.api.new_indicator(
            {
                "name": "test",
                "type": "regex",
                "description": "test",
                "pattern": "test[0-9]",
                "diamond": "victim",
            }
        )
        self.assertEqual(indicator["name"], "test")
        self.assertRegex(indicator["id"], r"[0-9]+")

    def test_auth_refresh(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        self.api.search_indicators(name="test")

        time.sleep(3)

        self.api.search_indicators(name="test")

    def test_search_indicators(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        result = self.api.search_indicators(name="test")
        self.assertEqual(len(result), 1, result)
