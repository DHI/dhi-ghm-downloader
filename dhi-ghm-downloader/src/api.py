"""HTTP client methods for forecast downloader."""

from dataclasses import dataclass
from typing import Any, Dict

import requests


@dataclass
class ApiSettings:
    api_key: str
    project_id: str
    base_url: str
    environment: str
    timeout: int


class ApiClient:
    def __init__(self, settings: ApiSettings):
        """Initialize the API client with session and settings."""
        self.settings = settings
        self.session = requests.Session()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def _common_params(self, project_id: str) -> Dict[str, Any]:
        """Build common query parameters for API requests."""
        return {
            "dhiOpenApiKey": self.settings.api_key,
            "projectId": project_id,
            "environment": self.settings.environment,
        }

    def get_subprojects(self) -> Any:
        """Fetch available forecast subprojects for the configured root project."""
        return self.get("subProjectIds", params=self._common_params(self.settings.project_id))

    def get_timeseries(self, project_id: str, ts_id: str) -> Any:
        """Fetch one timeseries payload by timeseries ID."""
        params = self._common_params(project_id)
        params["tsId"] = ts_id
        return self.get(f"ghm-timeseries/{ts_id}", params=params, timeout=max(self.settings.timeout, 120))

    def get_timeseries_bulk(self, project_id: str, ids: list[str]) -> Any:
        """Fetch multiple timeseries payloads in one request."""
        body = {
            "openAPIkey": self.settings.api_key,
            "projectId": project_id,
            "environment": self.settings.environment,
            "ids": ids,
        }
        return self.post("ghm-timeseries/tsIds", body=body, timeout=max(self.settings.timeout, 120))

    def get(self, endpoint: str, params: Dict[str, Any], timeout: int | None = None) -> Any:
        """Execute a GET request and return the decoded JSON payload."""
        url = f"{self.settings.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=timeout or self.settings.timeout)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, body: Dict[str, Any], timeout: int | None = None) -> Any:
        """Execute a POST request and return the decoded JSON payload."""
        url = f"{self.settings.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=body, timeout=timeout or self.settings.timeout)
        response.raise_for_status()
        return response.json()
