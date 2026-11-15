import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.inspect_apk import inspect_apk


class InspectionTests(unittest.TestCase):
    def test_inventory_hash_and_version_without_extracting(self):
        with tempfile.TemporaryDirectory() as folder:
            apk = Path(folder) / "fixture.apk"
            with zipfile.ZipFile(apk, "w") as archive:
                archive.writestr("assets/bin/Data/globalgamemanagers", b"\x002020.3.37f1\x00")
                archive.writestr("lib/arm64-v8a/libil2cpp.so", b"fixture")
                archive.writestr("../outside.txt", b"must never be extracted")
            original = apk.read_bytes()
            report = inspect_apk(apk)
            self.assertEqual(report["sha256"], hashlib.sha256(original).hexdigest())
            self.assertEqual(report["entry_count"], 3)
            self.assertEqual(report["unity_version_candidates"], ["2020.3.37f1"])
            self.assertEqual(report["native_libraries"], ["lib/arm64-v8a/libil2cpp.so"])
            self.assertEqual(apk.read_bytes(), original)
            self.assertEqual(list(Path(folder).iterdir()), [apk])
