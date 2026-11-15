import http.client
import json
from pathlib import Path
from threading import Thread
import unittest
from urllib.parse import urlencode

from server.app import DevelopmentServer
from server.bootstrap import BootstrapConfig
from server.codec import decode_message, encode_message
from server.http import MAX_REQUEST_BYTES


class BootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = DevelopmentServer(("127.0.0.1", 0), login_url="http://192.168.1.10:8080")
        cls.thread = Thread(target=cls.service.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.service.shutdown()
        cls.service.server_close()
        cls.thread.join()

    def request(self, body, *, path="/VersionCheck.aspx?CallCount=1", headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.service.server_port, timeout=3)
        try:
            connection.request("POST", path, body=body, headers=headers or {
                "Content-Type": "application/x-www-form-urlencoded"})
            response = connection.getresponse()
            return response.status, response.read(), response.getheader("Content-Type")
        finally:
            connection.close()

    def test_dotnet_request_produces_decryptable_bootstrap(self):
        fixture = Path(__file__).parent / "fixtures/http_crypto_vectors.json"
        request = json.loads(fixture.read_text(encoding="utf-8"))["vectors"][0]["ciphertext"]
        status, body, content_type = self.request(urlencode({"MSG": request}))
        self.assertEqual(status, 200)
        self.assertTrue(content_type.startswith("text/plain"))
        self.assertEqual(decode_message(body.decode("ascii"), "version"), {
            "Result": True, "ERR": 0, "loginserverurl": "http://192.168.1.10:8080",
            "servertype": 0, "resourceversion": 0,
        })

    def test_malformed_or_ambiguous_messages_are_rejected(self):
        valid = encode_message({"UID": "test"}, "version")
        for body in ("", "MSG=bad", "other=1", urlencode({"MSG": [valid, valid]}, doseq=True),
                     urlencode({"MSG": encode_message({}, "account")}),
                     urlencode({"MSG": encode_message({}, "version")}) + "&" + "&".join(f"k{i}=v" for i in range(17))):
            with self.subTest(body=body):
                status, response, _ = self.request(body)
                self.assertEqual(status, 400)
                self.assertEqual(json.loads(response)["error"], "invalid_message")

    def test_body_limit_and_content_type(self):
        self.assertEqual(self.request("x" * (MAX_REQUEST_BYTES + 1))[0], 413)
        self.assertEqual(self.request("{}", headers={"Content-Type": "application/json"})[0], 415)

    def test_unimplemented_login_is_not_reported_as_success(self):
        self.assertEqual(self.request("MSG=anything", path="/NewLogin.aspx")[0], 404)

    def test_status_keeps_client_validation_pending(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.service.server_port, timeout=3)
        try:
            connection.request("GET", "/status")
            response = json.loads(connection.getresponse().read())
            self.assertFalse(response["original_client_compatible"])
            self.assertEqual(response["client_validation"], "pending")
        finally:
            connection.close()

    def test_invalid_http_framing(self):
        cases = [([], 411), ([('Content-Length', '-1')], 400),
                 ([('Content-Length', '1'), ('Content-Length', '1')], 400),
                 ([('Content-Length', '9' * 5000)], 413),
                 ([('Transfer-Encoding', 'chunked')], 400)]
        for headers, expected in cases:
            with self.subTest(headers=headers[:1]):
                connection = http.client.HTTPConnection("127.0.0.1", self.service.server_port, timeout=3)
                try:
                    connection.putrequest("POST", "/VersionCheck.aspx")
                    connection.putheader("Content-Type", "application/x-www-form-urlencoded")
                    for name, value in headers:
                        connection.putheader(name, value)
                    connection.endheaders()
                    response = connection.getresponse()
                    self.assertEqual(response.status, expected)
                    response.read()
                finally:
                    connection.close()


class BootstrapConfigTests(unittest.TestCase):
    def test_rejects_invalid_advertised_login_urls(self):
        for url in ("", "localhost:8080", "ftp://example.test", "http://user:pass@example.test",
                    "http://example.test:99999", "http://example.test/?query=1", "http://example.test/#frag"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                BootstrapConfig(url)
