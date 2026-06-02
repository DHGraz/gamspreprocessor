"""A class for querying a Fedora 3 repository.


This only wraps the API query for finding objects by PID pattern, which is used in 
the export process. It is not meant to be a general-purpose API client for Fedora 3, 
and it does not implement any other API endpoints or features.
"""

import dataclasses
import re
from typing import ClassVar, Generator

import requests
from lxml import etree as ET
from gamspreprocessor.gams3.object import Gams3Object


@dataclasses.dataclass
class Gams3Query:
    "A class for querying a Fedora 3 repository."

    NAMESPACES: ClassVar[dict[str, str]] = {
        "ftypes": "http://www.fedora.info/definitions/1/0/types/"
    }

    base_url: str
    api_url: str = dataclasses.field(init=False)

    def __post_init__(self):
        "Set the API URL based on the base URL."
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]
        self.api_url = f"{self.base_url}/objects"

    def find_objects(self, pid_pattern: str) -> Generator[Gams3Object, None, None]:
        """Find all objects with the given pid.
        
        Args:
            pid_pattern: A pattern to match PIDs, e.g. "o:foo*"
        Yields:
            Gams3Object instances for each matching PID.
        Raises:
            ValueError: If the PID pattern is invalid.
        """
        if not self.is_valid_pid_pattern(pid_pattern):
            raise ValueError(f"Invalid PID pattern: '{pid_pattern}'")
        initial_url = self._build_initial_query_url(pid_pattern)
        for pid in self._fetch_paginated_pids(initial_url):
            yield Gams3Object(pid=pid, base_url=self.base_url)

    def is_valid_pid_pattern(self, pattern: str) -> bool:
        "Check if the given PID pattern is valid."
        return re.match(r"^[:a-zA-Z0-9_.?*-]{3,}$", pattern) is not None

    def _build_initial_query_url(self, pid_pattern: str) -> str:
        "Build the first page URL for a PID query."
        return f"{self.api_url}?query=pid%7E{pid_pattern}&resultFormat=xml&pid=true"

    def _build_continuation_url(self, initial_url: str, session_token: str) -> str:
        "Build a continuation URL by appending the latest session token."
        return f"{initial_url}&sessionToken={requests.utils.quote(session_token)}"

    def _extract_session_token(self, tree: ET._Element) -> str | None:
        "Extract the session token from a query result page."
        token_node = tree.find("./ftypes:listSession/ftypes:token", namespaces=self.NAMESPACES)
        if token_node is None or token_node.text is None:
            return None
        token = token_node.text.strip()
        return token or None

    def _extract_pids(self, tree: ET._Element) -> Generator[str, None, None]:
        "Yield all PID values from a query result page."
        for pid_node in tree.findall(
            "./ftypes:resultList/ftypes:objectFields/ftypes:pid",
            namespaces=self.NAMESPACES,
        ):
            if pid_node.text is None:
                continue
            pid = pid_node.text.strip()
            if pid:
                yield pid

    def _fetch_paginated_pids(self, initial_url: str) -> Generator[str, None, None]:
        "Fetch PIDs from a paginated API endpoint."
        url = initial_url
        previous_token = None

        while url:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            tree = ET.fromstring(response.content)

            for pid in self._extract_pids(tree):
                yield pid

            session_token = self._extract_session_token(tree)
            if session_token is None or session_token == previous_token:
                break

            url = self._build_continuation_url(initial_url, session_token)
            previous_token = session_token