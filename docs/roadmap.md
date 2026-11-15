# Implementation plan

- [x] Preserve original APK locally and exclude binaries from version control.
- [x] Add repeatable archive inventory and hashing.
- [x] Add a runnable development service and automated checks.
- [ ] Recover IL2CPP type/method structure and locate bootstrap/login call sites.
- [ ] Identify server configuration and required remote content.
- [ ] Run a controlled Android test and record startup/network behavior locally.
- [ ] Document first request bytes, framing, message IDs, and response schema.
- [ ] Implement the smallest compatible handshake and login flow.
- [ ] Reach the main menu with a local test profile.
- [ ] Implement matchmaking and a complete two-client match.
- [ ] Investigate iOS client compatibility and signing separately.

First client milestone: a patched Android client reaches the main menu through
the local server. Health-route success does not count as client compatibility.
