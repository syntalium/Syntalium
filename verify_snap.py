#!/usr/bin/env python3
"""Independent verifier for the public Syntalium SNAP proof contract."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
from pathlib import Path
from typing import Any, NoReturn, Sequence


SPEC_VERSION = "SNAP-PROOF-1"
HASH_ALGORITHM = "SHA-256"
CANONICALIZATION = "SNAP-C14N-1"
ENVELOPE_KEYS = {
    "spec_version",
    "hash_algorithm",
    "canonicalization",
    "payload",
    "fingerprint_sha256",
}
FINGERPRINT_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ContractViolation(ValueError):
    """Raised when input violates the public proof contract."""


def _reject_float(value: str) -> NoReturn:
    raise ContractViolation(f"floating-point numbers are forbidden: {value}")


def _reject_non_finite(value: str) -> NoReturn:
    raise ContractViolation(f"non-finite numbers are forbidden: {value}")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractViolation(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _validate_value(value: Any, path: str = "payload") -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        raise ContractViolation(f"{path}: floating-point numbers are forbidden")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractViolation(f"{path}: object keys must be strings")
            _validate_value(item, f"{path}.{key}")
        return
    raise ContractViolation(f"{path}: unsupported value type {type(value).__name__}")


def canonicalize_payload(payload: dict[str, Any]) -> bytes:
    """Return deterministic SNAP-C14N-1 UTF-8 bytes for a valid payload."""
    if not isinstance(payload, dict):
        raise ContractViolation("payload must be a JSON object")
    _validate_value(payload)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def fingerprint_payload(payload: dict[str, Any]) -> str:
    """Return the lowercase SHA-256 fingerprint for a valid payload."""
    return hashlib.sha256(canonicalize_payload(payload)).hexdigest()


def load_envelope(path: Path) -> dict[str, Any]:
    """Load UTF-8 JSON while rejecting ambiguous JSON constructs."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContractViolation(f"cannot read UTF-8 input: {exc}") from exc

    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_object_without_duplicates,
            parse_float=_reject_float,
            parse_constant=_reject_non_finite,
        )
    except ContractViolation:
        raise
    except json.JSONDecodeError as exc:
        raise ContractViolation(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ContractViolation("proof envelope must be a JSON object")
    return parsed


def validate_envelope(envelope: dict[str, Any]) -> None:
    """Validate V1 envelope metadata and payload value rules."""
    actual_keys = set(envelope)
    if actual_keys != ENVELOPE_KEYS:
        missing = sorted(ENVELOPE_KEYS - actual_keys)
        extra = sorted(actual_keys - ENVELOPE_KEYS)
        details: list[str] = []
        if missing:
            details.append(f"missing keys: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected keys: {', '.join(extra)}")
        raise ContractViolation("; ".join(details))

    if envelope["spec_version"] != SPEC_VERSION:
        raise ContractViolation(f"spec_version must be {SPEC_VERSION}")
    if envelope["hash_algorithm"] != HASH_ALGORITHM:
        raise ContractViolation(f"hash_algorithm must be {HASH_ALGORITHM}")
    if envelope["canonicalization"] != CANONICALIZATION:
        raise ContractViolation(f"canonicalization must be {CANONICALIZATION}")
    if not isinstance(envelope["payload"], dict):
        raise ContractViolation("payload must be a JSON object")

    fingerprint = envelope["fingerprint_sha256"]
    if not isinstance(fingerprint, str) or not FINGERPRINT_PATTERN.fullmatch(
        fingerprint
    ):
        raise ContractViolation(
            "fingerprint_sha256 must be 64 lowercase hexadecimal characters"
        )
    _validate_value(envelope["payload"])


def verify_envelope(envelope: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """Verify an already parsed envelope and return structured output and exit code."""
    try:
        validate_envelope(envelope)
        actual = fingerprint_payload(envelope["payload"])
        expected = envelope["fingerprint_sha256"]
    except ContractViolation as exc:
        return {
            "ok": False,
            "status": "invalid_input",
            "error": str(exc),
        }, 2

    if not hmac.compare_digest(actual, expected):
        return {
            "ok": False,
            "status": "fingerprint_mismatch",
            "expected_fingerprint_sha256": expected,
            "actual_fingerprint_sha256": actual,
        }, 1

    return {
        "ok": True,
        "status": "verified",
        "spec_version": SPEC_VERSION,
        "fingerprint_sha256": actual,
    }, 0


def verify_path(path: Path) -> tuple[dict[str, Any], int]:
    """Load and verify a proof file."""
    try:
        envelope = load_envelope(path)
    except ContractViolation as exc:
        return {
            "ok": False,
            "status": "invalid_input",
            "error": str(exc),
        }, 2
    return verify_envelope(envelope)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point with stable JSON output and documented exit codes."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        output = {
            "ok": False,
            "status": "invalid_input",
            "error": "usage: python verify_snap.py <proof-envelope.json>",
        }
        print(json.dumps(output, sort_keys=True))
        return 2

    output, exit_code = verify_path(Path(arguments[0]))
    print(json.dumps(output, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
