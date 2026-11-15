# Architecture

The initial implementation has two independent pieces:

1. A read-only APK inventory tool that produces reproducible local evidence.
2. An HTTP development service with health, implementation status, and an
   encrypted version-check bootstrap handler.

Health and status are project tooling. `POST /VersionCheck.aspx` implements the
statically recovered MSG/encrypted-JSON transport and a minimal bootstrap response.
The account codec is implemented, but account routes and ProudNet remain pending.
Unknown requests return 404. Actual Android startup validation is still pending.

Install runtime dependencies with `python -m pip install -r requirements.txt`.
Run with `python -m server`. For LAN testing, use `--host 0.0.0.0 --login-url
http://<your-lan-ip>:8080` so the advertised login URL is reachable by the device.
The default advertised URL points to loopback for local testing. This does not
redirect an unmodified APK, configure HTTPS, or implement login.

Once the client protocol is mapped, add a transport adapter separately from
account, profile, matchmaking, and match-state logic. Keep binary decoding and
encoding separate from those services so captured fixtures can verify each layer.
Do not select a database or authentication scheme until recovered requirements
make those choices meaningful.

ProudNet presence is confirmed; its wire protocol and compatibility are not.
A generic HTTP backend alone will not establish original-client compatibility.
