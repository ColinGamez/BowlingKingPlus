"""Read-only APK inventory. Never executes client code or contacts endpoints."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


def inspect_apk(path):
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = {item.filename for item in entries}
        managers = "assets/bin/Data/globalgamemanagers"
        versions = []
        if managers in names:
            # Bound decompression of an unexpected/untrusted archive member.
            if archive.getinfo(managers).file_size <= 32 * 1024 * 1024:
                data = archive.read(managers)
                versions = sorted({match.decode("ascii") for match in
                                   re.findall(rb"20\d{2}\.\d+\.\d+[abfp]\d+", data)})
        return {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": digest.hexdigest(),
            "entry_count": len(entries),
            "unity_version_candidates": versions,
            "native_libraries": [item.filename for item in entries
                                 if item.filename.startswith("lib/") and item.filename.endswith(".so")],
            "metadata_files": [item.filename for item in entries
                               if item.filename.endswith("global-metadata.dat")],
            "entries": [{"path": item.filename, "size_bytes": item.file_size,
                         "compressed_bytes": item.compress_size} for item in entries],
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts/apk-report.json"))
    args = parser.parse_args()
    try:
        if args.apk.resolve() == args.output.resolve():
            parser.error("output must not overwrite the input APK")
        report = inspect_apk(args.apk)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, zipfile.BadZipFile, RuntimeError) as error:
        parser.exit(1, f"Inspection failed: {error}\n")
    print(f"Report: {args.output}")
    print(f"SHA-256: {report['sha256']}")
    print(f"Unity candidates: {', '.join(report['unity_version_candidates']) or 'unknown'}")


if __name__ == "__main__":
    main()
