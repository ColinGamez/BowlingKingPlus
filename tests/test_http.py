import json
from http.server import ThreadingHTTPServer
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from server.http import Handler


class ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = Thread(target=cls.service.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.service.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.service.shutdown()
        cls.service.server_close()
        cls.thread.join()

    def test_health(self):
        with urlopen(self.base + "/health", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response)["status"], "ok")

    def test_status_does_not_claim_client_compatibility(self):
        with urlopen(self.base + "/status", timeout=3) as response:
            self.assertFalse(json.load(response)["original_client_compatible"])

    def test_unknown_game_endpoint_returns_404(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.base + "/login", timeout=3)
        with caught.exception as response:
            self.assertEqual(response.code, 404)
            self.assertEqual(json.load(response), {"error": "not_found"})
