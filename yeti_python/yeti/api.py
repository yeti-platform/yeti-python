"""Python client for the Yeti API."""

import requests

import json
from typing import Any, Sequence


TYPE_TO_ENDPOINT = {
    "indicator": "/api/v2/indicators",
    "entity": "/api/v2/entities",
    "observable": "/api/v2/observables",
    "dfiq": "/api/v2/dfiq",
}

OIDC_CALLBACK_ENDPOINT = "/api/v2/auth/oidc-callback-token"
API_TOKEN_ENDPOINT = "/api/v2/auth/api-token"


# typedef for a Yeti Objects
YetiObject = dict[str, Any]
YetiLinkObject = dict[str, Any]


class YetiApi:
    """API object to interact with the Yeti API.

    Attributes:
      client: The SSOFetcher client to use.
      _headers: The headers to use for all requests.
      _url_root: The root URL of the Yeti API.
    """

    def __init__(self, url_root: str):
        self.client = requests.Session()
        self._headers = {
            "Content-Type": "application/json",
        }
        self._url_root = url_root

    def auth_api_key(self, apikey: str) -> None:
        """Authenticates a session using an API key."""
        # Use long-term refresh API token to get an access token
        response = self.client.post(
            f"{self._url_root}{API_TOKEN_ENDPOINT}",
            headers={"x-yeti-apikey": apikey},
        )

        access_token = json.loads(response.text).get("access_token")
        authd_session = requests.Session()
        authd_session.headers.update({"authorization": f"Bearer {access_token}"})
        self.client = authd_session

    def search_indicators(
        self,
        name: str | None = None,
        indicator_type: str | None = None,
        pattern: str | None = None,
        tags: list[str] | None = None,
    ) -> list[YetiObject]:
        """Searches for an indicator in Yeti.

        One of name or pattern must be provided.

        Args:
          name: The name of the indicator to search for.
          indicator_type: The type of the indicator to search for.
          pattern: The pattern of the indicator to search for.
          tags: The tags of the indicator to search for.

        Returns:
          The response from the API; a dict representing the indicator.
        """

        if not any([name, indicator_type, pattern, tags]):
            raise ValueError(
                "You must provide one of name, indicator_type, pattern, or tags."
            )

        query = {}
        if name:
            query["name"] = name
        if pattern:
            query["pattern"] = pattern
        if indicator_type:
            query["type"] = indicator_type
        if tags:
            query["tags"] = tags
        params = {"query": query, "count": 0}
        response = self.client.post(
            f"{self._url_root}/api/v2/indicators/search",
            json=params,
        )
        return response.json()["indicators"]

    def search_entities(self, name: str) -> list[YetiObject]:
        params = {"query": {"name": name}, "count": 0}
        response = self.client.post(
            f"{self._url_root}/api/v2/entities/search",
            json=params,
        )
        return response.json()["entities"]

    def search_observables(self, value: str) -> list[YetiObject]:
        """Searches for an observable in Yeti.

        Args:
          value: The value of the observable to search for.

        Returns:
          The response from the API; a dict representing the observable.
        """
        params = {"query": {"value": value}, "count": 0}
        response = self.client.post(
            f"{self._url_root}/api/v2/observables/search", json=params
        )
        return response.json()["observables"]

    def new_entity(
        self, entity: dict[str, Any], tags: list[str] | None = None
    ) -> YetiObject:
        """Creates a new entity in Yeti.

        Args:
          entity: The entity to create.
          tags: The tags to associate with the entity.

        Returns:
          The response from the API; a dict representing the entity.
        """
        params = {"entity": entity}
        if tags:
            params["tags"] = tags
        response = self.client.post(f"{self._url_root}/api/v2/entities/", json=params)
        return response.json()

    def new_indicator(
        self,
        indicator: dict[str, Any],
        tags: list[str] | None = None,
    ) -> YetiObject:
        """Creates a new indicator in Yeti.

        Args:
          indicator: The indicator to create.
          tags: The tags to associate with the indicator.

        Returns:
          The response from the API; a dict representing the indicator.
        """
        params = {"indicator": indicator}
        response, _ = self.client.post(
            f"{self._url_root}/api/v2/indicators/", json=params
        )
        indicator = json.loads(response)

        if tags:
            params = {"tags": tags, "ids": [indicator["id"]]}
            self.client.post(f"{self._url_root}/api/v2/indicators/tag", json=params)

        return indicator

    def patch_indicator(
        self,
        yeti_id: int,
        indicator_object: dict[str, Any],
    ) -> YetiObject:
        """Patches an indicator in Yeti."""
        params = {"indicator": indicator_object}
        response = self.client.patch(
            f"{self._url_root}/api/v2/indicators/{yeti_id}", json=params
        )
        return response.json()

    def search_dfiq(self, name: str, dfiq_type: str | None = None) -> list[YetiObject]:
        """Searches for a DFIQ in Yeti.

        Args:
          name: The name of the DFIQ object to search for, e.g. "Suspicious DNS
            Query."
          dfiq_type: The type of the DFIQ object to search for, e.g. "scenario".

        Returns:
          The response from the API; a dict representing the DFIQ object.
        """
        query = {"name": name}
        if dfiq_type:
            query["type"] = dfiq_type
        params = {"query": query, "count": 0}
        response = self.client.post(f"{self._url_root}/api/v2/dfiq/search", json=params)
        return response.json()["dfiq"]

    def new_dfiq_from_yaml(self, dfiq_type: str, dfiq_yaml: str) -> YetiObject:
        """Creates a new DFIQ object in Yeti from a YAML string."""
        params = {
            "dfiq_type": dfiq_type,
            "dfiq_yaml": dfiq_yaml,
            "update_indicators": True,
        }
        response = self.client.post(
            f"{self._url_root}/api/v2/dfiq/from_yaml", json=params
        )
        return response.json()

    def patch_dfiq_from_yaml(
        self,
        dfiq_type: str,
        dfiq_yaml: str,
        yeti_id: int,
    ) -> YetiObject:
        """Patches a DFIQ object in Yeti from a YAML string."""
        params = {
            "dfiq_type": dfiq_type,
            "dfiq_yaml": dfiq_yaml,
            "update_indicators": True,
        }
        response = self.client.patch(
            f"{self._url_root}/api/v2/dfiq/{yeti_id}", json=params
        )
        return response.json()

    def download_dfiq_archive(self, dfiq_type: str | None = None) -> bytes:
        """Downloads an archive containing all DFIQ data from Yeti.

        Args:
          dfiq_type: Optional. The type of the DFIQ object include in the archive,
            e.g. "scenario".

        Returns:
          The archive contents as bytes.
        """
        params = {"count": 0}
        if dfiq_type:
            params["query"] = {"type": dfiq_type}
        response = self.client.post(
            f"{self._url_root}/api/v2/dfiq/to_archive", json=params
        )
        return body

    def upload_dfiq_archive(self, archive_path: str) -> dict[str, int]:
        """Uploads a DFIQ archive to Yeti.

        The archive must be a ZIP file containing all the DFIQ YAML data.

        Args:
          archive_path: The path to the archive file.

        Returns:
          A dict containing the number of DFIQ objects that were uploaded.
        """
        with open(archive_path, "rb") as archive:
            data = archive.read()
        encoded_data = encoder.MultipartEncoder(
            fields={"archive": ("archive.zip", data, "application/zip")}
        )
        headers = {"Content-Type": encoded_data.content_type}
        response = self.client.post(
            f"{self._url_root}/api/v2/dfiq/from_archive",
            extra_headers=headers,
            body=encoded_data.to_string(),
        )
        return response.json()

    def add_observable(
        self, value: str, observable_type: str, tags: list[str] | None = None
    ) -> YetiObject:
        """Adds an observable to Yeti.

        Args:
          value: The value of the observable to add.
          observable_type: The type of the observable to add.
          tags: The tags to associate with the observable.

        Returns:
          The response from the API; a dict representing the observable.
        """
        params = {"value": value, "type": observable_type, "tags": tags}
        response = self.client.post(
            f"{self._url_root}/api/v2/observables/", json=params
        )
        return response.json()

    def add_observables_bulk(
        self, observables: list[dict[str, Any]], tags: list[str] | None = None
    ) -> dict[str, list[YetiObject] | list[str]]:
        """Bulk-adds a list of observables to Yeti.

        See
        http://yeti-root/docs#/observables/bulk_add_api_v2_observables_bulk_post
        for details.

        Args:
          observables: The list of observables to add. Dictionaries should have a
            'value' (str) and a 'type' (str) key. See TACO_TYPE_MAPPING for a list
            of supported types.
          tags: The tags to associate with all observables.

        Returns:
          The response from the API; a dict with an 'added' key containing a list of
          dicts representing observables, and a 'failed' key containing a list of
          strings representing observables that could not be added.
        """
        if tags:
            for observable in observables:
                observable["tags"] = tags
        params = {
            "observables": observables,
        }

        response = self.client.post(
            f"{self._url_root}/api/v2/observables/bulk", json=params
        )
        return response.json()

    def tag_object(
        self, yeti_object: dict[str, Any], tags: Sequence[str]
    ) -> dict[str, Any]:
        """Tags an object in Yeti."""
        params = {"tags": list(tags), "ids": [yeti_object["id"]]}
        endpoint = TYPE_TO_ENDPOINT[yeti_object["root_type"]]
        result, _ = self.client.post(f"{self._url_root}{endpoint}/tag", json=params)
        return json.loads(result)

    def link_objects(
        self,
        source: YetiObject,
        target: YetiObject,
        link_type: str,
        description: str | None = None,
    ) -> YetiLinkObject:
        """Links two objects in Yeti.

        http://See yeti-root/docs#/graph/add_api_v2_graph_add_post
        for details.

        Args:
          source: The source object (as provided by Yeti).
          target: The target object (as provided by Yeti).
          link_type: The type of the link.
          description: The description of the link. Markdown supported.

        Returns:
          The response from the API; a dict representing the link.
        """
        params = {
            "source": f"{source['root_type']}/{source['id']}",
            "target": f"{target['root_type']}/{target['id']}",
            "link_type": link_type,
            "description": description,
        }
        response = self.client.post(f"{self._url_root}/api/v2/graph/add", json=params)
        return response.json()

    def search_graph(
        self,
        source: str,
        graph: str,
        target_types: list[str],
        min_hops: int = 1,
        max_hops: int = 1,
        direction: str = "outbound",
        include_original: bool = True,
    ) -> dict[str, Any]:
        """Searches the graph for objects related to a given object.

        See
        http://yeti-root/docs#/graph/search_api_v2_graph_search_post
        for details.

        Args:
          source: The ID of the source object (as provided by Yeti) in the format
            "<root_type>/<id>", such as 'dfiq/id'.
          graph: The graph to search, such as 'links'.
          target_types: The types of objects to search for.
          min_hops: The minimum number of hops to search.
          max_hops: The maximum number of hops to search.
          direction: The direction to search.
          include_original: Whether to include the source object in the results.

        Returns:
          The response from the API; a dict representing the graph.
        """
        params = {
            "count": 0,
            "source": source,
            "graph": graph,
            "min_hops": min_hops,
            "max_hops": max_hops,
            "direction": direction,
            "include_original": include_original,
            "target_types": target_types,
        }
        response = self.client.post(
            f"{self._url_root}/api/v2/graph/search", json=params
        )
        return response.json()
