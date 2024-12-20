import unittest
from unittest.mock import patch, MagicMock
from yeti.api import YetiApi


class TestYetiApi(unittest.TestCase):
    def setUp(self):
        self.api = YetiApi("http://fake-url")

    @patch("yeti.api.requests.Session.post")
    def test_auth_api_key(self, mock_post):
        mock_response = MagicMock()
        mock_response.text = '{"access_token": "fake_token"}'
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
        mock_response.json.return_value = {"indicators": [{"name": "test"}]}
        mock_post.return_value = mock_response

        result = self.api.search_indicators(name="test")
        self.assertEqual(result, [{"name": "test"}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/indicators/search",
            json={"query": {"name": "test"}, "count": 0},
        )

    @patch("yeti.api.requests.Session.post")
    def test_search_entities(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"entities": [{"name": "test_entity"}]}
        mock_post.return_value = mock_response

        result = self.api.search_entities(name="test_entity")
        self.assertEqual(result, [{"name": "test_entity"}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/entities/search",
            json={"query": {"name": "test_entity"}, "count": 0},
        )

    @patch("yeti.api.requests.Session.post")
    def test_search_observables(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"observables": [{"value": "test_value"}]}
        mock_post.return_value = mock_response

        result = self.api.search_observables(value="test_value")
        self.assertEqual(result, [{"value": "test_value"}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/observables/search",
            json={"query": {"value": "test_value"}, "count": 0},
        )

    @patch("yeti.api.requests.Session.post")
    def test_new_entity(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "new_entity"}
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
        mock_response.json.return_value = {"id": "new_indicator"}
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
        mock_response.json.return_value = {"id": "patched_indicator"}
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
        mock_response.json.return_value = {"dfiq": [{"name": "test_dfiq"}]}
        mock_post.return_value = mock_response

        result = self.api.search_dfiq(name="test_dfiq")
        self.assertEqual(result, [{"name": "test_dfiq"}])
        mock_post.assert_called_with(
            "http://fake-url/api/v2/dfiq/search",
            json={"query": {"name": "test_dfiq"}, "count": 0},
        )

    @patch("yeti.api.requests.Session.post")
    def test_new_dfiq_from_yaml(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "new_dfiq"}
        mock_post.return_value = mock_response

        result = self.api.new_dfiq_from_yaml("type", "yaml_content")
        self.assertEqual(result, {"id": "new_dfiq"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/dfiq/from_yaml",
            json={
                "dfiq_type": "type",
                "dfiq_yaml": "yaml_content",
                "update_indicators": True,
            },
        )

    @patch("yeti.api.requests.Session.patch")
    def test_patch_dfiq_from_yaml(self, mock_patch):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "patched_dfiq"}
        mock_patch.return_value = mock_response

        result = self.api.patch_dfiq_from_yaml("type", "yaml_content", 1)
        self.assertEqual(result, {"id": "patched_dfiq"})
        mock_patch.assert_called_with(
            "http://fake-url/api/v2/dfiq/1",
            json={
                "dfiq_type": "type",
                "dfiq_yaml": "yaml_content",
                "update_indicators": True,
            },
        )

    @patch("yeti.api.requests.Session.post")
    def test_download_dfiq_archive(self, mock_post):
        mock_response = MagicMock()
        mock_response.bytes = b"archive_content"
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
        mock_response.json.return_value = {"uploaded": 1}
        mock_post.return_value = mock_response

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"data")):
            result = self.api.upload_dfiq_archive("path/to/archive.zip")
            self.assertEqual(result, {"uploaded": 1})
        self.assertEqual(
            mock_post.call_args[0][0], "http://fake-url/api/v2/dfiq/from_archive"
        )
        self.assertRegex(
            mock_post.call_args[1]["extra_headers"]["Content-Type"],
            "multipart/form-data; boundary=[a-f0-9]{32}",
        )

    @patch("yeti.api.requests.Session.post")
    def test_add_observable(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "new_observable"}
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
        mock_response.json.return_value = {"added": [], "failed": []}
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
        mock_response.json.return_value = {"id": "tagged_object"}
        mock_post.return_value = mock_response

        result = self.api.tag_object({"id": "1", "root_type": "indicator"}, ["tag1"])
        self.assertEqual(result, {"id": "tagged_object"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/indicators/tag",
            json={"tags": ["tag1"], "ids": ["1"]},
        )

    @patch("yeti.api.requests.Session.post")
    def test_link_objects(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "link"}
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
        mock_response.json.return_value = {"graph": "data"}
        mock_post.return_value = mock_response

        result = self.api.search_graph("source", "graph", ["type"])
        self.assertEqual(result, {"graph": "data"})
        mock_post.assert_called_with(
            "http://fake-url/api/v2/graph/search",
            json={
                "count": 0,
                "source": "source",
                "graph": "graph",
                "min_hops": 1,
                "max_hops": 1,
                "direction": "outbound",
                "include_original": True,
                "target_types": ["type"],
            },
        )


if __name__ == "__main__":
    unittest.main()
