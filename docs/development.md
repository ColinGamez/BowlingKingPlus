# Development guide

These instructions are for contributors working on the revival. Running the
development server does not make the original game playable yet.

## Run the development server

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

See [research findings](research.md) and the [implementation plan](roadmap.md).
The [client protocol notes](client-protocol.md) record recovered bootstrap
endpoints and message IDs. Follow the [research workflow](research-workflow.md)
to reproduce the local dump, protocol map, and native instruction inspection.

