import os
import time
import unittest

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

    def test_search_entities(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        self.api.new_entity(
            {
                "name": "testSearch",
                "type": "malware",
                "description": "test",
            },
            tags=["testtag"],
        )
        time.sleep(5)
        result = self.api.search_entities(name="testSear", description="tes")
        self.assertEqual(len(result), 1, result)
        self.assertEqual(result[0]["name"], "testSearch")
        self.assertEqual(result[0]["tags"][0]["name"], "testtag")

    def test_get_multiple_entities(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        self.api.new_entity(
            {
                "name": "testGet1",
                "type": "malware",
                "description": "test",
            },
            tags=["testtag1"],
        )
        self.api.new_entity(
            {
                "name": "testGet2",
                "type": "malware",
                "description": "test",
            },
            tags=["testtag2"],
        )
        time.sleep(5)
        entities = self.api.get_multiple_entities(["testGet1", "testGet2"])
        self.assertEqual(len(entities), 2)
        names = [entity["name"] for entity in entities]
        self.assertCountEqual(names, ["testGet1", "testGet2"])

    def test_search_indicators(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        self.api.new_indicator(
            {
                "name": "testSearch",
                "type": "regex",
                "description": "test",
                "pattern": "test[0-9]",
                "diamond": "victim",
            },
            tags=["testtag"],
        )
        time.sleep(5)
        result = self.api.search_indicators(
            name="testSear", description="tes", tags=["testtag"]
        )
        self.assertEqual(len(result), 1, result)
        self.assertEqual(result[0]["name"], "testSearch")
        self.assertEqual(result[0]["tags"][0]["name"], "testtag")

    def test_find_indicator(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        self.api.new_indicator(
            {
                "name": "testGet",
                "type": "regex",
                "description": "test",
                "pattern": "test[0-9]",
                "diamond": "victim",
            },
            tags=["testtag"],
        )
        time.sleep(5)
        indicator = self.api.find_indicator(name="testGet", type="regex")

        self.assertEqual(indicator["name"], "testGet")
        self.assertEqual(indicator["pattern"], "test[0-9]")
        self.assertEqual(indicator["tags"][0]["name"], "testtag")

    def test_get_multiple_indicators(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        self.api.new_indicator(
            {
                "name": "testGet1",
                "type": "regex",
                "description": "test",
                "pattern": "test[0-9]",
                "diamond": "victim",
            },
            tags=["testtag1"],
        )
        self.api.new_indicator(
            {
                "name": "testGet2",
                "type": "regex",
                "description": "test",
                "pattern": "test[0-9]",
                "diamond": "victim",
            },
            tags=["testtag2"],
        )
        time.sleep(5)
        indicators = self.api.get_multiple_indicators(["testGet1", "testGet2"])
        self.assertEqual(len(indicators), 2)
        names = [indicator["name"] for indicator in indicators]
        self.assertCountEqual(names, ["testGet1", "testGet2"])

    def test_link_objects(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        indicator = self.api.new_indicator(
            {
                "name": "testLink",
                "type": "regex",
                "description": "test",
                "pattern": "test[0-9]",
                "diamond": "victim",
            }
        )
        malware = self.api.new_entity(
            {
                "name": "testMalware",
                "type": "malware",
                "description": "test",
            }
        )
        self.api.link_objects(
            source=indicator,
            target=malware,
            link_type="indicates",
            description="test link",
        )

        # get neighbors
        neighbors = self.api.search_graph(
            f'indicator/{indicator["id"]}',
            target_types=["malware"],
            include_original=False,
        )
        self.assertEqual(len(neighbors["vertices"]), 1)
        self.assertEqual(
            neighbors["vertices"][f'entities/{malware["id"]}']["name"], "testMalware"
        )

    def test_new_tag(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        tag = self.api.new_tag("testTag", description="test")
        self.assertEqual(tag["name"], "testTag")
        self.assertEqual(tag["description"], "test")

    def test_search_tags(self):
        self.api.auth_api_key(os.getenv("YETI_API_KEY"))
        self.api.new_tag("testSearchTag", description="testDesc")
        time.sleep(5)

        tags = self.api.search_tags(name="testSearch")
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0]["name"], "testSearchTag")
        self.assertEqual(tags[0]["description"], "testDesc")
