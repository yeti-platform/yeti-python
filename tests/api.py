import unittest
from unittest.mock import patch, MagicMock
from yeti.api import YetiApi
from yeti import errors

import requests


class TestYetiApi(unittest.TestCase):
    def setUp(self):
        self.api = YetiApi("http://fake-url")

    @patch("yeti.api.requests.Session.post")
    def test_auth_api_key(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"access_token": "fake_token"}'
        mock_post.return_value = mock_response

        self.api.auth_api_key("fake_apikey")
        self.assertEqual(self.api.client.headers["authorization"], "Bearer fake_token")
        mock_post.assert_called_with(
            "http://fake-url/api/v2/auth/api-token",
            headers={"x-yeti-apikey": "fake_apikey"},
        )

    @patch("yeti.api.requests.Session.post")
    def test_search_indicators(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"indicators": [{"name": "test"}]}'
        mock_post.return_value = mock_response

        result = self.api.search_indicators(
            name="test", description="test_description", tags=["tag1"]
        )
        self.assertEqual(result, [{"name": "test"}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/indicators/search",
            json={
                "query": {
                    "name": "test",
                    "description": "test_description",
                    "tags": ["tag1"],
                },
                "count": 100,
                "page": 0,
            },
        )

    @patch("yeti.api.requests.Session.post")
    def test_search_entities(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"entities": [{"name": "test_entity"}]}'
        mock_post.return_value = mock_response

        result = self.api.search_entities(
            name="test_entity", description="test_description"
        )
        self.assertEqual(result, [{"name": "test_entity"}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/entities/search",
            json={
                "query": {"name": "test_entity", "description": "test_description"},
                "count": 100,
                "page": 0,
            },
        )

    @patch("yeti.api.requests.Session.post")
    def test_search_observables(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"observables": [{"value": "test_value"}]}'
        mock_post.return_value = mock_response

        result = self.api.search_observables(value="test_value", tags=["tag1"])
        self.assertEqual(result, [{"value": "test_value"}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/observables/search",
            json={
                "query": {"value": "test_value", "tags": ["tag1"]},
                "count": 100,
                "page": 0,
            },
        )

    @patch("yeti.api.requests.Session.post")
    def test_search_bloom(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'[{"value": "test.com", "hits": ["filter1"]}]'
        mock_post.return_value = mock_response

        result = self.api.search_bloom(["test.com"])
        self.assertEqual(result, [{"value": "test.com", "hits": ["filter1"]}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/bloom/search",
            json={"values": ["test.com"]},
        )

    @patch("yeti.api.requests.Session.post")
    def test_new_entity(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "new_entity"}'
        mock_response.content = b'{"id": "new_entity"}'
        mock_post.return_value = mock_response

        result = self.api.new_entity({"name": "test_entity"})
        self.assertEqual(result, {"id": "new_entity"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/entities/",
            json={"entity": {"name": "test_entity"}},
        )

    @patch("yeti.api.requests.Session.post")
    def test_new_indicator(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "new_indicator"}'
        mock_post.return_value = mock_response

        result = self.api.new_indicator({"name": "test_indicator"})
        self.assertEqual(result, {"id": "new_indicator"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/indicators/",
            json={"indicator": {"name": "test_indicator"}},
        )

    @patch("yeti.api.requests.Session.patch")
    def test_patch_indicator(self, mock_patch):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "patched_indicator"}'
        mock_patch.return_value = mock_response

        result = self.api.patch_indicator(1, {"name": "patched_indicator"})
        self.assertEqual(result, {"id": "patched_indicator"})
        mock_patch.assert_called_with(
            "http://fake-url/api/v2/indicators/1",
            json={"indicator": {"name": "patched_indicator"}},
        )

    @patch("yeti.api.requests.Session.post")
    def test_search_dfiq(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"dfiq": [{"name": "test_dfiq"}]}'
        mock_post.return_value = mock_response

        result = self.api.search_dfiq(
            name="test_dfiq", dfiq_yaml="yaml_content", dfiq_tags=["tag1"]
        )
        self.assertEqual(result, [{"name": "test_dfiq"}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/dfiq/search",
            json={
                "query": {
                    "name": "test_dfiq",
                    "dfiq_yaml": "yaml_content",
                    "dfiq_tags": ["tag1"],
                },
                "count": 100,
                "filter_aliases": [["dfiq_tags", "list"], ["dfiq_id", "text"]],
                "page": 0,
            },
        )

    @patch("yeti.api.requests.Session.post")
    def test_new_dfiq_from_yaml(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "new_dfiq"}'
        mock_post.return_value = mock_response

        result = self.api.new_dfiq_from_yaml("type", "yaml_content")
        self.assertEqual(result, {"id": "new_dfiq"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/dfiq/from_yaml",
            json={
                "dfiq_type": "type",
                "dfiq_yaml": "yaml_content",
            },
        )

    @patch("yeti.api.requests.Session.patch")
    def test_patch_dfiq_from_yaml(self, mock_patch):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "patched_dfiq"}'
        mock_patch.return_value = mock_response

        result = self.api.patch_dfiq_from_yaml("type", "yaml_content", 1)
        self.assertEqual(result, {"id": "patched_dfiq"})
        mock_patch.assert_called_with(
            "http://fake-url/api/v2/dfiq/1",
            json={
                "dfiq_type": "type",
                "dfiq_yaml": "yaml_content",
            },
        )

    @patch("yeti.api.requests.Session.patch")
    def test_patch_dfiq(self, mock_patch):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "patched_dfiq"}'
        mock_patch.return_value = mock_response

        result = self.api.patch_dfiq(
            {"name": "patched_dfiq", "id": 1, "type": "question"}
        )
        self.assertEqual(result, {"id": "patched_dfiq"})
        mock_patch.assert_called_with(
            "http://fake-url/api/v2/dfiq/1",
            json={
                "dfiq_object": {"name": "patched_dfiq", "type": "question", "id": 1},
                "dfiq_type": "question",
            },
        )

    @patch("yeti.api.requests.Session.post")
    def test_download_dfiq_archive(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b"archive_content"
        mock_post.return_value = mock_response

        result = self.api.download_dfiq_archive()
        self.assertEqual(result, b"archive_content")
        mock_post.assert_called_with(
            "http://fake-url/api/v2/dfiq/to_archive",
            json={"count": 0},
        )

    @patch("yeti.api.requests.Session.post")
    def test_upload_dfiq_archive(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"uploaded": 1}'
        mock_post.return_value = mock_response

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"data")):
            result = self.api.upload_dfiq_archive("path/to/archive.zip")
            self.assertEqual(result, {"uploaded": 1})
        self.assertEqual(
            mock_post.call_args[0][0], "http://fake-url/api/v2/dfiq/from_archive"
        )
        self.assertRegex(
            mock_post.call_args[1]["headers"]["Content-Type"],
            "multipart/form-data; boundary=[a-f0-9]{32}",
        )

    @patch("yeti.api.requests.Session.post")
    def test_add_observable(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "new_observable"}'
        mock_post.return_value = mock_response

        result = self.api.add_observable("value", "type")
        self.assertEqual(result, {"id": "new_observable"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/observables/",
            json={"value": "value", "type": "type", "tags": None},
        )

    @patch("yeti.api.requests.Session.post")
    def test_add_observables_bulk(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"added": [], "failed": []}'
        mock_post.return_value = mock_response

        result = self.api.add_observables_bulk([{"value": "value", "type": "type"}])
        self.assertEqual(result, {"added": [], "failed": []})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/observables/bulk",
            json={"observables": [{"value": "value", "type": "type"}]},
        )

    @patch("yeti.api.requests.Session.post")
    def test_tag_object(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "tagged_object"}'
        mock_post.return_value = mock_response

        result = self.api.tag_object({"id": "1", "root_type": "indicator"}, ["tag1"])
        self.assertEqual(result, {"id": "tagged_object"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/indicators/tag",
            json={"tags": ["tag1"], "ids": ["1"]},
        )

    @patch("yeti.api.requests.Session.post")
    def test_new_tag(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"name": "testtag"}'
        mock_post.return_value = mock_response

        result = self.api.new_tag("testtag")
        self.assertEqual(result, {"name": "testtag"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/tags/",
            json={"name": "testtag"},
        )

        result = self.api.new_tag("wdesc", description="desc")
        mock_post.assert_called_with(
            "http://fake-url/api/v2/tags/",
            json={"name": "wdesc", "description": "desc"},
        )

    @patch("yeti.api.requests.Session.post")
    def test_search_tags(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"tags": [{"name": "tag1"}]}'
        mock_post.return_value = mock_response

        result = self.api.search_tags("tag1")
        self.assertEqual(result, [{"name": "tag1"}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/tags/search",
            json={"name": "tag1", "count": 100, "page": 0},
        )

    @patch("yeti.api.requests.Session.post")
    def test_link_objects(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "link"}'
        mock_post.return_value = mock_response

        result = self.api.link_objects(
            {"id": "1", "root_type": "indicator"},
            {"id": "2", "root_type": "entity"},
            "link_type",
        )
        self.assertEqual(result, {"id": "link"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/graph/add",
            json={
                "source": "indicator/1",
                "target": "entity/2",
                "link_type": "link_type",
                "description": None,
            },
        )

    @patch("yeti.api.requests.Session.post")
    def test_search_graph(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b'{"graph": "data"}'
        mock_post.return_value = mock_response

        result = self.api.search_graph("source", ["type"])
        self.assertEqual(result, {"graph": "data"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/graph/search",
            json={
                "count": 50,
                "page": 0,
                "source": "source",
                "graph": "links",
                "min_hops": 1,
                "max_hops": 1,
                "direction": "outbound",
                "include_original": True,
                "target_types": ["type"],
            },
        )

    @patch("yeti.api.requests.Session.post")
    def test_error_message(self, mock_post):
        # create mock requests response that raises an requests.exceptions.HTTPError for status
        mock_response = MagicMock()
        mock_exception_with_status_code = requests.exceptions.HTTPError()
        mock_exception_with_status_code.response = MagicMock()
        mock_exception_with_status_code.response.status_code = 400
        mock_exception_with_status_code.response.text = "error_message"
        mock_response.raise_for_status.side_effect = mock_exception_with_status_code
        mock_post.return_value = mock_response

        with self.assertRaises(errors.YetiApiError) as raised:
            self.api.new_indicator({"name": "test_indicator"})

        self.assertEqual(str(raised.exception), "error_message")
        self.assertEqual(raised.exception.status_code, 400)

    @patch("yeti.api.requests.Session.post")
    def test_get_yara_bundle_with_overlays(self, mock_post):
        # Mock the YARA bundle response
        mock_response = MagicMock()
        mock_response.content = b'{"bundle": "bundlestring"}'
        mock_post.return_value = mock_response

        # Call the method with overlays
        result = self.api.get_yara_bundle_with_overlays(
            overlays=["overlay1", "overlay2"]
        )

        # Check the result
        self.assertEqual(result, {"bundle": "bundlestring"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/indicators/yara/bundle",
            json={
                "ids": [],
                "tags": [],
                "exclude_tags": [],
                "overlays": ["overlay1", "overlay2"],
            },
        )

    @patch("yeti.api.requests.Session.get")
    def test_find_indicator(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "found_indicator"}'
        mock_get.return_value = mock_response

        result = self.api.find_indicator(name="test_indicator", type="indicator.test")
        self.assertEqual(result, {"id": "found_indicator"})
        mock_get.assert_called_with(
            "http://fake-url/api/v2/indicators/?name=test_indicator&type=indicator.test",
        )

        # Test 404 case
        mock_exception_with_status_code = requests.exceptions.HTTPError()
        mock_exception_with_status_code.response = MagicMock()
        mock_exception_with_status_code.response.status_code = 404
        mock_response.raise_for_status.side_effect = mock_exception_with_status_code
        mock_get.return_value = mock_response

        result = self.api.find_indicator(name="not_found", type="indicator.test")
        self.assertIsNone(result)

    @patch("yeti.api.requests.Session.get")
    def test_find_entity(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "found_entity"}'
        mock_get.return_value = mock_response

        result = self.api.find_entity(name="test_entity", type="entity.test")
        self.assertEqual(result, {"id": "found_entity"})
        mock_get.assert_called_with(
            "http://fake-url/api/v2/entities/?name=test_entity&type=entity.test",
        )

        # Test 404 case
        mock_exception_with_status_code = requests.exceptions.HTTPError()
        mock_exception_with_status_code.response = MagicMock()
        mock_exception_with_status_code.response.status_code = 404
        mock_response.raise_for_status.side_effect = mock_exception_with_status_code
        mock_get.return_value = mock_response

        result = self.api.find_entity(name="not_found", type="entity.test")
        self.assertIsNone(result)

    @patch("yeti.api.requests.Session.get")
    def test_find_observable(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "found_observable"}'
        mock_get.return_value = mock_response

        result = self.api.find_observable(value="test_value", type="observable.test")
        self.assertEqual(result, {"id": "found_observable"})
        mock_get.assert_called_with(
            "http://fake-url/api/v2/observables/?value=test_value&type=observable.test",
        )

        # Test 404 case
        mock_exception_with_status_code = requests.exceptions.HTTPError()
        mock_exception_with_status_code.response = MagicMock()
        mock_exception_with_status_code.response.status_code = 404
        mock_response.raise_for_status.side_effect = mock_exception_with_status_code
        mock_get.return_value = mock_response

        result = self.api.find_observable(value="not_found", type="observable.test")
        self.assertIsNone(result)

    @patch("yeti.api.requests.Session.get")
    def test_find_dfiq(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b'{"id": "found_dfiq"}'
        mock_get.return_value = mock_response

        result = self.api.find_dfiq(name="test_dfiq", dfiq_type="scenario")
        self.assertEqual(result, {"id": "found_dfiq"})
        mock_get.assert_called_with(
            "http://fake-url/api/v2/dfiq/?name=test_dfiq&type=scenario",
        )

        # Test 404 case
        mock_exception_with_status_code = requests.exceptions.HTTPError()
        mock_exception_with_status_code.response = MagicMock()
        mock_exception_with_status_code.response.status_code = 404
        mock_response.raise_for_status.side_effect = mock_exception_with_status_code
        mock_get.return_value = mock_response

        result = self.api.find_dfiq(name="not_found", dfiq_type="scenario")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
