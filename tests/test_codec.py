import json
from pathlib import Path
import unittest

from server.codec import decode_message, decrypt, encode_message, encrypt


class CodecTests(unittest.TestCase):
    def test_matches_independent_dotnet_vectors_in_both_directions(self):
        fixture = Path(__file__).parent / "fixtures/http_crypto_vectors.json"
        for vector in json.loads(fixture.read_text(encoding="utf-8"))["vectors"]:
            with self.subTest(profile=vector["profile"]):
                self.assertEqual(encrypt(vector["plaintext"], vector["profile"]), vector["ciphertext"])
                self.assertEqual(decrypt(vector["ciphertext"], vector["profile"]), vector["plaintext"])

    def test_form_decoded_plus_and_base64_line_breaks(self):
        ciphertext = encrypt('{"UID":"local-test","clientbundleversion":"v1.50.19"}', "version")
        self.assertIn("+", ciphertext)
        encoded = ciphertext.replace("+", " ")
        self.assertIn("local-test", decrypt(encoded[:40] + "\r\n" + encoded[40:], "version"))

    def test_unicode_message(self):
        payload = {"name": "ボウリング", "Result": True}
        self.assertEqual(decode_message(encode_message(payload, "account"), "account"), payload)

    def test_invalid_ciphertexts_are_rejected(self):
        for value in ("", "not base64!", "AA==", "A" * 24, "\u2603"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                decrypt(value, "version")

    def test_non_object_and_nonstandard_json_are_rejected(self):
        for value in ("[]", "null", '{"x":NaN}', '{"x":Infinity}', "invalid json"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode_message(encrypt(value, "version"), "version")
