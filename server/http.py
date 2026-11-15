"""Project HTTP routes. These are not the original game's protocol."""

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health":
            self.respond(200, {"status": "ok", "service": "BowlingKingPlus"})
        elif path == "/status":
            self.respond(200, {
                "phase": "research",
                "original_client_compatible": False,
                "implemented": ["health", "status"],
                "pending": ["proudnet", "login", "matchmaking", "multiplayer"],
            })
        else:
            self.respond(404, {"error": "not_found"})

    def respond(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
