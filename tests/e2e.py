import os
import time
import unittest
from unittest.mock import MagicMock, patch

import requests

from yeti import errors
from yeti.api import YetiApi


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
        self.api.new_indicator(
            {
                "name": "testSearch",
                "type": "regex",
                "description": "test",
                "pattern": "test[0-9]",
                "diamond": "victim",
            }
        )
        time.sleep(5)
        result = self.api.search_indicators(
            name="testSear", description="test", tags=["testTag"]
        )
        self.assertEqual(len(result), 1, result)
        self.assertEqual(result[0]["name"], "testSearch")

    def test_find_indicator(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        self.api.new_indicator(
            {
                "name": "testGet",
                "type": "regex",
                "description": "test",
                "pattern": "test[0-9]",
                "diamond": "victim",
            }
        )
        time.sleep(5)
        indicator = self.api.find_indicator(name="testGet", type="regex")

        self.assertEqual(indicator["name"], "testGet")
        self.assertEqual(indicator["pattern"], "test[0-9]")
