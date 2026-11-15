"""Summarize an Il2CppDumper dump without publishing the full client dump."""

import argparse
import hashlib
import json
from pathlib import Path
import re


BLOCK = re.compile(
    r"// Namespace: ([^\n]*)\n([^\n]+ // TypeDefIndex: \d+)\n\{\n(.*?)\n\}",
    re.S,
)


def map_dump(text):
    blocks = BLOCK.findall(text.replace("\r\n", "\n"))
    messages = []
    targets = []
    for namespace, declaration, body in blocks:
        if namespace in ("BowlingKingC2GS", "BowlingKingGS2C") and re.search(r"class Common\b", declaration):
            for name, number in re.findall(r"public const RmiID (\w+) = (\d+);", body):
                messages.append({"namespace": namespace, "name": name, "id": int(number)})
        if re.search(r"class (BKApi|BKNetwork|PhaseTitle)\s", declaration):
            methods = []
            pending_rva = None
            for line in body.splitlines():
                rva = re.search(r"// RVA: (0x[\dA-Fa-f]+)", line)
                if rva:
                    pending_rva = rva.group(1)
                if line.strip().endswith("{ }") and pending_rva:
                    methods.append({"rva": pending_rva, "signature": line.strip()[:-4].rstrip()})
                    pending_rva = None
            targets.append({"declaration": declaration, "methods": methods})
    if not messages:
        raise ValueError("No Bowling King RMI constants found; check the dump input")
    return {"message_count": len(messages), "messages": messages, "research_targets": targets,
            "limitations": "Declarations and RVAs only; no wire framing or serialization inferred."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts/protocol-map.json"))
    args = parser.parse_args()
    try:
        if args.dump.resolve() == args.output.resolve():
            parser.error("output must not overwrite the dump")
        raw = args.dump.read_bytes()
        report = map_dump(raw.decode("utf-8-sig"))
        report["dump_sha256"] = hashlib.sha256(raw).hexdigest()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(1, f"Mapping failed: {error}\n")
    print(f"Mapped {report['message_count']} messages: {args.output}")


if __name__ == "__main__":
    main()
