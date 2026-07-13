import unittest
from unittest.mock import MagicMock, patch

from app.sdk.client import Client


class Phase8SDKTests(unittest.TestCase):
    @patch("app.sdk.client.requests.request")
    def test_client_uses_api_key_and_parses_payload(self, request_mock: MagicMock) -> None:
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"query": "insurance", "count": 1, "results": [{"path": "a.md"}]}
        request_mock.return_value = response

        client = Client(base_url="http://localhost:8000", api_key="secret")
        result = client.search("insurance")

        self.assertEqual(result.query, "insurance")
        self.assertEqual(result.count, 1)

        _, kwargs = request_mock.call_args
        self.assertEqual(kwargs["headers"]["X-API-Key"], "secret")


if __name__ == "__main__":
    unittest.main()
