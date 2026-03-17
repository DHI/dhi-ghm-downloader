import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

try:
    from src.api import ApiClient, ApiSettings
except ModuleNotFoundError:
    PROJECT_SRC_ROOT = Path(__file__).resolve().parents[1].joinpath("dhi-ghm-downloader")
    if str(PROJECT_SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_SRC_ROOT))
    from src.api import ApiClient, ApiSettings


class TestApiClient(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = ApiSettings(
            api_key="abc",
            project_id="root-project",
            base_url="https://example.test/api/",
            environment="prod",
            timeout=30,
        )

    @patch("src.api.requests.Session")
    def test_common_params(self, mock_session_cls: Mock) -> None:
        client = ApiClient(self.settings)
        params = client._common_params("child")
        self.assertEqual(
            params,
            {
                "dhiOpenApiKey": "abc",
                "projectId": "child",
                "environment": "prod",
            },
        )

    @patch("src.api.requests.Session")
    def test_get_subprojects(self, mock_session_cls: Mock) -> None:
        client = ApiClient(self.settings)
        client.get = Mock(return_value=[{"id": "x"}])
        result = client.get_subprojects()
        self.assertEqual(result, [{"id": "x"}])
        client.get.assert_called_once_with(
            "subProjectIds",
            params={
                "dhiOpenApiKey": "abc",
                "projectId": "root-project",
                "environment": "prod",
            },
        )

    @patch("src.api.requests.Session")
    def test_get_timeseries(self, mock_session_cls: Mock) -> None:
        client = ApiClient(self.settings)
        client.get = Mock(return_value={"ok": True})
        result = client.get_timeseries("child", "136")
        self.assertEqual(result, {"ok": True})
        client.get.assert_called_once_with(
            "ghm-timeseries/136",
            params={
                "dhiOpenApiKey": "abc",
                "projectId": "child",
                "environment": "prod",
                "tsId": "136",
            },
            timeout=120,
        )

    @patch("src.api.requests.Session")
    def test_get_timeseries_bulk(self, mock_session_cls: Mock) -> None:
        client = ApiClient(self.settings)
        client.post = Mock(return_value={"done": True})
        result = client.get_timeseries_bulk("child", ["1", "2"])
        self.assertEqual(result, {"done": True})
        client.post.assert_called_once_with(
            "ghm-timeseries/tsIds",
            body={
                "openAPIkey": "abc",
                "projectId": "child",
                "environment": "prod",
                "ids": ["1", "2"],
            },
            timeout=120,
        )

    @patch("src.api.requests.Session")
    def test_get_uses_session(self, mock_session_cls: Mock) -> None:
        response = Mock()
        response.json.return_value = {"x": 1}
        session = Mock()
        session.get.return_value = response
        mock_session_cls.return_value = session

        client = ApiClient(self.settings)
        result = client.get("/endpoint", params={"a": "b"})

        self.assertEqual(result, {"x": 1})
        session.get.assert_called_once_with(
            "https://example.test/api/endpoint",
            params={"a": "b"},
            timeout=30,
        )
        response.raise_for_status.assert_called_once()

    @patch("src.api.requests.Session")
    def test_post_uses_session(self, mock_session_cls: Mock) -> None:
        response = Mock()
        response.json.return_value = {"x": 2}
        session = Mock()
        session.post.return_value = response
        mock_session_cls.return_value = session

        client = ApiClient(self.settings)
        result = client.post("/endpoint", body={"a": "b"}, timeout=50)

        self.assertEqual(result, {"x": 2})
        session.post.assert_called_once_with(
            "https://example.test/api/endpoint",
            json={"a": "b"},
            timeout=50,
        )
        response.raise_for_status.assert_called_once()

    @patch("src.api.requests.Session")
    def test_close(self, mock_session_cls: Mock) -> None:
        session = Mock()
        mock_session_cls.return_value = session
        client = ApiClient(self.settings)
        client.close()
        session.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
