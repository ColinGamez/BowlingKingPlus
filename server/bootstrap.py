"""Static-research bootstrap response. Android client validation is still pending."""

from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class BootstrapConfig:
    login_url: str

    def __post_init__(self):
        parsed = urlsplit(self.login_url)
        if (parsed.scheme not in ("http", "https") or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
                or parsed.query or parsed.fragment):
            raise ValueError("login URL must be an absolute HTTP(S) base URL without credentials, query or fragment")
        # Accessing .port validates malformed and out-of-range port values.
        parsed.port

    def version_response(self):
        return {
            "Result": True,
            "ERR": 0,
            "loginserverurl": self.login_url,
            # Dev server, no resource patch offered. Existing bundled assets only.
            "servertype": 0,
            "resourceversion": 0,
        }
