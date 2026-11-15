from http.server import ThreadingHTTPServer

from server.bootstrap import BootstrapConfig
from server.http import Handler


class DevelopmentServer(ThreadingHTTPServer):
    def __init__(self, address, *, login_url=None):
        # Validate explicit configuration before opening the listening socket.
        config = BootstrapConfig(login_url) if login_url is not None else None
        super().__init__(address, Handler)
        self.bootstrap = config or BootstrapConfig(f"http://127.0.0.1:{self.server_port}")
