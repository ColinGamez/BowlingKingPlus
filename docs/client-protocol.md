# Client protocol investigation

## Evidence scope

APK SHA-256: `d9dc4ba5890b2daa86cce0e02b263f59bdf2b4a320d10083fc8a8cda0a43a890`.
Addresses below apply to its **ARM64** `libil2cpp.so` only.

Il2CppDumper v6.7.46 identified metadata version 27 and selected native layout
27.1. It initially warned that the binary might be protected, but automatically
located registration structures and generated declarations and literal addresses.
The recovered declarations are research leads, not decompiled method bodies.

Local reports contain 113 `BowlingKingC2GS` message IDs and 150
`BowlingKingGS2C` message IDs, for 263 total. The full extracted dump and assets
remain local. Metadata declarations do not establish serialization or packet layout.

## HTTP bootstrap and account API

`BKApi` declares these endpoint constants:

| Purpose | Constant value |
| --- | --- |
| Initial base URL | `http://54.65.99.23:32000` |
| Version check | `https://bowlingver.pnixgamesdev2.com:89/VersionCheck.aspx` |
| Account check | `CheckUserType.aspx` |
| Registration | `Registration.aspx` |
| Login | `NewLogin.aspx` |

These addresses were recovered statically; availability has not been tested.
The API also declares `application/x-www-form-urlencoded` as its content type.
`BKApi.SetBaseUrl` and a mutable base URL mean the initial constant need not be
the server used after version negotiation.

| ARM64 method RVA | Research target |
| --- | --- |
| `0x78AAB0` | `BKApi.VersionCheck` request construction |
| `0x78B3F4` | `BKApi.Login` request construction |
| `0x86FBB4` | `PhaseTitle.VersionCheckCallback` response parsing |
| `0x870708` | `PhaseTitle.LoginCallback` response parsing |
| `0x791780` | `BKNetwork.Connect` |
| `0x791468` | `BKNetwork.Login` |

The version callback references `loginserverurl`, `resourceversion`, `servertype`,
`arrresourcefileurl`, `closedservertext`, `closedserverbeginutctime`, and
`closedserverendutctime`. Some references appear during IL2CPP metadata
initialization; their existence alone does not prove that all fields are required
in every response. Recover their types, conditions, and enclosing structure before
implementing a response.

The HTTP login method references `UID`, `StoreType`, `languagecode`, `c01`,
`g14`, `clientversion`, and `clientbundleversion`. The native instructions show
dictionary insertion patterns for these names. `clientbundleversion` references
`v1.50.19`; the semantics of opaque fields and final HTTP encoding need further
tracing. Do not treat managed parameter names as HTTP field names.

## Game server messages

| Direction | Name | ID |
| --- | --- | --- |
| Client → server | `RequestLogin` | 3001 |
| Client → server | `RequestLoginVer2` | 3107 |
| Server → client | `RequestLoginAck` | 4001 |
| Client → server | `JoinLaneReq` | 3003 |
| Server → client | `JoinLaneAck` | 4003 |
| Client → server | `SendBallPath` | 3009 |
| Client → server | `SendPinPath` | 3010 |
| Client → server | `SendScore` | 3011 |

`BKNetwork.Login` ends with a native branch at `0x791530` to `0x8109B0`, mapped
to `RequestLoginVer2(HostID remote, RmiContext rmiContext, string strUserName,
int nToken, bool bIsReTurn)`. This supports using version 2 as the initial
login research target for this client; merely implementing message 3001 would
miss this call path.

The declaration for `RequestLoginAck` includes a result boolean, `CActorInfo`,
a list of achievements, server time, an advertising flag, and `CActorInfo_Extra`.
These are managed arguments, not a verified sequence of wire bytes.

Ball/pin path submission and score submission are evidence of client gameplay
reporting. They do not establish whether server simulation or validation is needed.

## Next investigation

1. Trace version response lookups and conversions, including success/error envelope.
2. Trace login response values into the game-server IP, port, user name, and token.
3. Inspect the version-2 proxy serializer and ProudNet connection setup separately.
4. Validate the findings against a controlled Android startup capture.

No original service was contacted and no APK was patched during this pass.
