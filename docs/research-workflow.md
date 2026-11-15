# Reproduce the static research

The server and basic inspection tools need only Python. Native research also
uses [Il2CppDumper v6.7.46](https://github.com/Perfare/Il2CppDumper/releases/tag/v6.7.46),
Capstone, and pyelftools. Third-party tools and their output remain local.
The dumper's [metadata definitions](https://github.com/Perfare/Il2CppDumper/blob/v6.7.46/Il2CppDumper/Il2Cpp/MetadataClass.cs)
describe the version-dependent structures it reads.

## Prepare a dump on Windows

Download the `Il2CppDumper-net6-win-v6.7.46.zip` release into `local/tooling/`
and expand it to `local/tooling/il2cppdumper/`. Extract these two APK entries
locally, preserving the original APK:

- `lib/arm64-v8a/libil2cpp.so` → `local/client/libil2cpp.so`
- `assets/bin/Data/Managed/Metadata/global-metadata.dat` → `local/client/global-metadata.dat`

Create `artifacts/il2cpp/`. In the downloaded tool's `config.json`, set
`RequireAnyKey` to `false` for noninteractive execution. With a newer installed
.NET runtime, the following process-scoped setting allows major-version roll-forward:

```powershell
$env:DOTNET_ROLL_FORWARD = 'Major'
& local/tooling/il2cppdumper/Il2CppDumper.exe local/client/libil2cpp.so local/client/global-metadata.dat artifacts/il2cpp
python tools/map_protocol.py artifacts/il2cpp/dump.cs
```

The mapper writes `artifacts/protocol-map.json`, including message directions,
IDs, interesting method signatures/RVAs, and a hash of its input dump. It rejects
inputs without Bowling King RMI declarations.

## Inspect native instructions

Use a research virtual environment so optional packages remain separate:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r tools/requirements-research.txt
.venv/Scripts/python.exe tools/disassemble_arm64.py local/client/libil2cpp.so 0x791468 0x791538 --dump artifacts/il2cpp/dump.cs
.venv/Scripts/python.exe tools/disassemble_arm64.py local/client/libil2cpp.so 0x86FBB4 0x87027C --literals artifacts/il2cpp/stringliteral.json --dump artifacts/il2cpp/dump.cs
```

The disassembler translates virtual addresses using ELF executable segments and
uses AArch64 relative relocations to annotate literal references. Branch names
come from the dump and can be ambiguous when methods share an address.
Register tracking is deliberately limited to simple straight-line patterns and
resets at control-flow edges. An absent annotation does not prove an absent
reference. This tool does not recover higher-level control flow or field schemas.
