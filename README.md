# BowlingKingPlus

Community research and replacement-server project for Bowling King.

**Status:** initial research scaffold. The development HTTP server is operational;
original game login, ProudNet transport, and multiplayer are not implemented.
No compatibility with the original client is claimed yet.

## Quick start

Requires Python 3.12 or newer. No third-party packages are required.

```powershell
python -m unittest discover -s tests -v
python -m server
```

Visit <http://127.0.0.1:8080/health>. The server binds to loopback by default.
Use `python -m server --host 0.0.0.0 --port 8080` when testing on a trusted LAN.
This is a development service, not a production deployment.

## Inspect a local client

```powershell
python tools/inspect_apk.py "Bowling+King_1.50.19_APKPure.apk"
```

This reads the archive without running or modifying it and writes a JSON inventory
to `artifacts/apk-report.json`. Reports, original apps, extracted code/assets,
and traffic captures remain outside Git. Put additional research material under
`local/`. Do not commit account credentials or live session tokens.

## Layout

| Path | Purpose |
| --- | --- |
| `server/` | Development HTTP service; future protocol adapters belong here |
| `tools/` | Repeatable client inspection tools |
| `tests/` | Server behavior and inspection checks |
| `docs/` | Evidence, architecture, and research plan |
| `artifacts/` | Generated reports, ignored by Git |
| `local/` | Private clients, dumps, captures, ignored by Git |

See [research findings](docs/research.md) and the [implementation plan](docs/roadmap.md).

## Project boundaries

An independent, unofficial project, unaffiliated with Miniclip or the original
developers. Original game binaries and assets are not distributed here. This
repository does not currently grant a project license; choose one before accepting
external contributions that require redistribution terms.
