# Architecture

The initial implementation has two independent pieces:

1. A read-only APK inventory tool that produces reproducible local evidence.
2. A small HTTP development service for health and implementation status.

The HTTP routes are project tooling, not recovered Bowling King endpoints.
Unknown requests return 404 instead of invented game responses.

Once the client protocol is mapped, add a transport adapter separately from
account, profile, matchmaking, and match-state logic. Keep binary decoding and
encoding separate from those services so captured fixtures can verify each layer.
Do not select a database or authentication scheme until recovered requirements
make those choices meaningful.

ProudNet presence is confirmed; its wire protocol and compatibility are not.
A generic HTTP backend alone will not establish original-client compatibility.
