# Initial client evidence

Inspected locally on 2026-11-16. These observations describe the supplied archive;
they do not establish the state of any original online services.

| Item | Observation |
| --- | --- |
| Input filename | `Bowling+King_1.50.19_APKPure.apk` |
| File size | 89,518,153 bytes |
| ZIP entries | 2,578 |
| Unity version string | `2020.3.37f1` in `assets/bin/Data/globalgamemanagers` |
| Runtime | IL2CPP libraries for ARMv7 and ARM64 |
| Managed metadata | `assets/bin/Data/Managed/Metadata/global-metadata.dat` |
| Network library | `libProudNetClientPlugin.so` for both architectures |
| Message type names | `BowlingKingC2GSProxy`, `BowlingKingGS2CStub` |
| Gameplay names | `BowlingBallController`, `BowlingGameSystem`, `BowlingPin` |
| Bundled content | Bowling scene references and numerous Unity assets |

Version 1.50.19 is taken from the filename, not yet independently decoded from
the Android manifest. Names found in metadata do not prove particular methods
are executable, or that local physics can run without a server.

## Still unknown

- Bootstrap configuration and actual game server endpoints.
- Login request/response structures and ordering.
- ProudNet handshake, framing, serialization, message IDs, and transport choices.
- Which simulation and validation responsibilities live on the client/server.
- Required assets or configuration downloaded after installation.
- Whether a suitable older client makes reconstruction simpler.

Record discoveries with the APK SHA-256, archive path, method/type or offset,
and confidence. Keep guesses separate from verified observations. Do not contact
original endpoints automatically during static inspection.
