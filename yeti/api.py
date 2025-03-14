"""Python client for the Yeti API."""

import json
import logging
from typing import Any, Sequence

import requests
import requests_toolbelt.multipart.encoder as encoder

import yeti.errors as errors

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


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


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

        self._auth_function = ""
        self._auth_function_map = {
            "auth_api_key": self.auth_api_key,
        }

        self._apikey = None

    def do_request(
        self,
        method: str,
        url: str,
        json_data: dict[str, Any] | None = None,
        body: bytes | None = None,
        headers: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> bytes:
        """Issues a request to the given URL.

        Args:
            method: The HTTP method to use.
            url: The URL to issue the request to.
            json: The JSON payload to include in the request.
            body: The body to include in the request.
            headers: Extra headers to include in the request.
            retries: The number of times to retry the request.

        Returns:
            The response from the API; a bytes object.

        """

        if json_data and body:
            raise ValueError("You must provide either json or body, not both.")

        request_kwargs = {}

        if headers:
            request_kwargs["headers"] = headers
        if json_data:
            request_kwargs["json"] = json_data
        if body:
            request_kwargs["body"] = body

        try:
            if method == "POST":
                response = self.client.post(url, **request_kwargs)
            elif method == "PATCH":
                response = self.client.patch(url, **request_kwargs)
            elif method == "GET":
                response = self.client.get(url, **request_kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                if retries == 0:
                    raise errors.YetiAuthError(str(e)) from e
                self.refresh_auth()
                return self.do_request(
                    method, url, json_data, body, headers, retries - 1
                )

            raise errors.YetiApiError(e.response.status_code, e.response.text)

        return response.content

    def auth_api_key(self, apikey: str | None = None) -> None:
        """Authenticates a session using an API key."""
        # Use long-term refresh API token to get an access token
        if apikey is not None:
            self._apikey = apikey
        if not self._apikey:
            raise ValueError("No API key provided.")

        response = self.do_request(
            "POST",
            f"{self._url_root}{API_TOKEN_ENDPOINT}",
            headers={"x-yeti-apikey": self._apikey},
        )

        access_token = json.loads(response).get("access_token")
        if not access_token:
            raise RuntimeError(
                f"Failed to find access token in the response: {response}"
            )
        authd_session = requests.Session()
        authd_session.headers.update({"authorization": f"Bearer {access_token}"})
        self.client = authd_session

        self._auth_function = "auth_api_key"

    def refresh_auth(self):
        if self._auth_function:
            self._auth_function_map[self._auth_function]()
        else:
            logger.warning("No auth function set, cannot refresh auth.")

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
        response = self.do_request(
            "POST",
            f"{self._url_root}/api/v2/indicators/search",
            json_data=params,
        )
        return json.loads(response)["indicators"]

    def search_entities(self, name: str) -> list[YetiObject]:
        params = {"query": {"name": name}, "count": 0}
        response = self.do_request(
            "POST",
            f"{self._url_root}/api/v2/entities/search",
            json_data=params,
        )
        return json.loads(response)["entities"]

    def search_observables(self, value: str) -> list[YetiObject]:
        """Searches for an observable in Yeti.

        Args:
          value: The value of the observable to search for.

        Returns:
          The response from the API; a dict representing the observable.
        """
        params = {"query": {"value": value}, "count": 0}
        response = self.do_request(
            "POST", f"{self._url_root}/api/v2/observables/search", json_data=params
        )
        return json.loads(response)["observables"]

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
        response = self.do_request(
            "POST",
            f"{self._url_root}/api/v2/entities/",
            json_data=params,
        )
        return json.loads(response)

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
        response = self.do_request(
            "POST", f"{self._url_root}/api/v2/indicators/", json_data=params
        )
        indicator = json.loads(response)

        if tags:
            params = {"tags": tags, "ids": [indicator["id"]]}
            self.do_request(
                "POST", f"{self._url_root}/api/v2/indicators/tag", json_data=params
            )

        return indicator

    def patch_indicator(
        self,
        yeti_id: int,
        indicator_object: dict[str, Any],
    ) -> YetiObject:
        """Patches an indicator in Yeti."""
        params = {"indicator": indicator_object}
        response = self.do_request(
            "PATCH", f"{self._url_root}/api/v2/indicators/{yeti_id}", json_data=params
        )
        return json.loads(response)

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
        response = self.do_request(
            "POST", f"{self._url_root}/api/v2/dfiq/search", json_data=params
        )
        return json.loads(response)["dfiq"]

    def new_dfiq_from_yaml(self, dfiq_type: str, dfiq_yaml: str) -> YetiObject:
        """Creates a new DFIQ object in Yeti from a YAML string."""
        params = {
            "dfiq_type": dfiq_type,
            "dfiq_yaml": dfiq_yaml,
        }
        response = self.do_request(
            "POST", f"{self._url_root}/api/v2/dfiq/from_yaml", json_data=params
        )
        return json.loads(response)

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
        }
        response = self.do_request(
            "PATCH", f"{self._url_root}/api/v2/dfiq/{yeti_id}", json_data=params
        )
        return json.loads(response)

    def patch_dfiq(self, dfiq_object: dict[str, Any]) -> YetiObject:
        """Patches a DFIQ object in Yeti."""
        params = {
            "dfiq_type": dfiq_object["type"],
            "dfiq_object": dfiq_object,
        }
        response = self.do_request(
            "PATCH",
            f"{self._url_root}/api/v2/dfiq/{dfiq_object['id']}",
            json_data=params,
        )
        return json.loads(response)

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
        response = self.do_request(
            "POST", f"{self._url_root}/api/v2/dfiq/to_archive", json_data=params
        )
        return response

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
        response = self.do_request(
            "POST",
            f"{self._url_root}/api/v2/dfiq/from_archive",
            headers=headers,
            body=encoded_data.to_string(),
        )
        return json.loads(response)

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
        response = self.do_request(
            "POST", f"{self._url_root}/api/v2/observables/", json_data=params
        )
        return json.loads(response)

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

        response = self.do_request(
            "POST", f"{self._url_root}/api/v2/observables/bulk", json_data=params
        )
        return json.loads(response)

    def tag_object(
        self, yeti_object: dict[str, Any], tags: Sequence[str]
    ) -> dict[str, Any]:
        """Tags an object in Yeti."""
        params = {"tags": list(tags), "ids": [yeti_object["id"]]}
        endpoint = TYPE_TO_ENDPOINT[yeti_object["root_type"]]
        response = self.do_request(
            "POST", f"{self._url_root}{endpoint}/tag", json_data=params
        )
        return json.loads(response)

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
        response = self.do_request(
            "POST", f"{self._url_root}/api/v2/graph/add", json_data=params
        )
        return json.loads(response)

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
        response = self.do_request(
            "POST", f"{self._url_root}/api/v2/graph/search", json_data=params
        )
        return json.loads(response)
