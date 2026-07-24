from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "snap-proof-v1.synthetic.json"
VERIFIER = ROOT / "verify_snap.py"

sys.path.insert(0, str(ROOT))

import verify_snap  # noqa: E402


class SnapProofTests(unittest.TestCase):
    def load_fixture(self) -> dict[str, Any]:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def run_cli(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VERIFIER), str(path)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def write_json(self, directory: Path, name: str, value: Any) -> Path:
        path = directory / name
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    def test_valid_fixture_passes(self) -> None:
        output, exit_code = verify_snap.verify_path(FIXTURE)
        self.assertEqual(0, exit_code)
        self.assertTrue(output["ok"])
        self.assertEqual(
            self.load_fixture()["fingerprint_sha256"],
            output["fingerprint_sha256"],
        )

    def test_different_key_order_has_same_hash(self) -> None:
        first = {"z": 1, "a": {"y": True, "b": None}}
        second = {"a": {"b": None, "y": True}, "z": 1}
        self.assertEqual(
            verify_snap.fingerprint_payload(first),
            verify_snap.fingerprint_payload(second),
        )

    def test_one_character_change_changes_hash(self) -> None:
        original = self.load_fixture()["payload"]
        changed = copy.deepcopy(original)
        changed["symbol"] = "BTCUSDU"
        self.assertNotEqual(
            verify_snap.fingerprint_payload(original),
            verify_snap.fingerprint_payload(changed),
        )

    def test_tampered_envelope_fails_verification(self) -> None:
        envelope = self.load_fixture()
        envelope["payload"]["symbol"] = "ETHUSDT"
        output, exit_code = verify_snap.verify_envelope(envelope)
        self.assertEqual(1, exit_code)
        self.assertFalse(output["ok"])
        self.assertEqual("fingerprint_mismatch", output["status"])

    def test_duplicate_keys_are_rejected(self) -> None:
        duplicate_json = """{
          "spec_version": "SNAP-PROOF-1",
          "hash_algorithm": "SHA-256",
          "canonicalization": "SNAP-C14N-1",
          "payload": {"snap_id": "A", "snap_id": "B"},
          "fingerprint_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
        }"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text(duplicate_json, encoding="utf-8")
            output, exit_code = verify_snap.verify_path(path)
        self.assertEqual(2, exit_code)
        self.assertEqual("invalid_input", output["status"])
        self.assertIn("duplicate JSON key", output["error"])

    def test_floats_are_rejected(self) -> None:
        with self.assertRaises(verify_snap.ContractViolation):
            verify_snap.canonicalize_payload({"confidence": 0.5})

        float_json = """{
          "spec_version": "SNAP-PROOF-1",
          "hash_algorithm": "SHA-256",
          "canonicalization": "SNAP-C14N-1",
          "payload": {"confidence": 0.5},
          "fingerprint_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
        }"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "float.json"
            path.write_text(float_json, encoding="utf-8")
            output, exit_code = verify_snap.verify_path(path)
        self.assertEqual(2, exit_code)
        self.assertIn("floating-point numbers are forbidden", output["error"])

    def test_malformed_fingerprint_is_rejected(self) -> None:
        envelope = self.load_fixture()
        envelope["fingerprint_sha256"] = "ABC123"
        output, exit_code = verify_snap.verify_envelope(envelope)
        self.assertEqual(2, exit_code)
        self.assertEqual("invalid_input", output["status"])

    def test_unicode_canonicalization_is_stable(self) -> None:
        first = {"місто": "Київ", "drink": "café", "emoji": "🔐"}
        second = {"emoji": "🔐", "drink": "café", "місто": "Київ"}
        canonical = verify_snap.canonicalize_payload(first)
        self.assertEqual(canonical, verify_snap.canonicalize_payload(second))
        self.assertIn("Київ".encode("utf-8"), canonical)
        self.assertNotIn(b"\\u", canonical)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            verify_snap.fingerprint_payload(first),
        )

    def test_cli_exit_codes(self) -> None:
        valid = self.run_cli(FIXTURE)
        self.assertEqual(0, valid.returncode)
        self.assertTrue(json.loads(valid.stdout)["ok"])

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)

            tampered = self.load_fixture()
            tampered["payload"]["record_status"] = "CHANGED"
            tampered_path = self.write_json(directory, "tampered.json", tampered)
            mismatch = self.run_cli(tampered_path)
            self.assertEqual(1, mismatch.returncode)
            self.assertEqual(
                "fingerprint_mismatch",
                json.loads(mismatch.stdout)["status"],
            )

            invalid = self.load_fixture()
            invalid["payload"]["value"] = 1.25
            invalid_path = self.write_json(directory, "invalid.json", invalid)
            contract_error = self.run_cli(invalid_path)
            self.assertEqual(2, contract_error.returncode)
            self.assertEqual(
                "invalid_input",
                json.loads(contract_error.stdout)["status"],
            )

    def test_schema_is_valid_json_and_has_no_private_fields(self) -> None:
        schema_path = ROOT / "schemas" / "snap-proof-v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual("object", schema["type"])
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            {
                "spec_version",
                "hash_algorithm",
                "canonicalization",
                "payload",
                "fingerprint_sha256",
            },
            set(schema["properties"]),
        )


if __name__ == "__main__":
    unittest.main()
