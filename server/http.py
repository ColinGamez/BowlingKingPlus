"""Development routes and the recovered HTTP version-check entry point."""

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit

from server.codec import decode_message, encode_message


MAX_REQUEST_BYTES = 64 * 1024


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health":
            self.respond(200, {"status": "ok", "service": "BowlingKingPlus"})
        elif path == "/status":
            self.respond(200, {
                "phase": "research",
                "original_client_compatible": False,
                "implemented": ["health", "status", "encrypted_version_check"],
                "client_validation": "pending",
                "pending": ["proudnet", "login", "matchmaking", "multiplayer"],
            })
        else:
            self.respond(404, {"error": "not_found"})

    def do_POST(self):
        if urlsplit(self.path).path != "/VersionCheck.aspx":
            self.respond(404, {"error": "not_found"})
            return
        if self.headers.get("Transfer-Encoding"):
            self.respond(400, {"error": "unsupported_transfer_encoding"})
            return
        lengths = self.headers.get_all("Content-Length", [])
        if not lengths:
            self.respond(411, {"error": "content_length_required"})
            return
        if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
            self.respond(400, {"error": "invalid_content_length"})
            return
        # Bound conversion too: arbitrarily long decimal headers must not raise
        # Python's integer digit-limit exception outside the request error path.
        significant_length = lengths[0].lstrip("0") or "0"
        if len(significant_length) > len(str(MAX_REQUEST_BYTES)):
            self.respond(413, {"error": "request_too_large"})
            return
        length = int(significant_length)
        if length > MAX_REQUEST_BYTES:
            self.respond(413, {"error": "request_too_large"})
            return
        if self.headers.get_content_type() != "application/x-www-form-urlencoded":
            self.respond(415, {"error": "expected_form_body"})
            return
        self.connection.settimeout(5)
        try:
            body = self.rfile.read(length)
            if len(body) != length:
                raise ValueError("incomplete body")
            fields = parse_qs(body.decode("ascii"), keep_blank_values=True,
                              strict_parsing=True, max_num_fields=16, errors="strict")
            if len(fields.get("MSG", [])) != 1:
                raise ValueError("one MSG field is required")
            decode_message(fields["MSG"][0], "version")
        except TimeoutError:
            self.respond(408, {"error": "request_timeout"})
            return
        except (ValueError, UnicodeError, RecursionError):
            self.respond(400, {"error": "invalid_message"})
            return
        response = encode_message(self.server.bootstrap.version_response(), "version")
        self.send_body(200, response.encode("ascii"), "text/plain; charset=us-ascii")

    def respond(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_body(status, body, "application/json; charset=utf-8")

    def send_body(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
