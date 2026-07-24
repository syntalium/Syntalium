# SNAP Canonicalization V1

## Status and Scope

This document defines the public, independent verification contract for a
Syntalium SNAP proof envelope. It is intentionally limited to deterministic
JSON canonicalization and SHA-256 integrity verification.

This contract is **not** a model, feature pipeline, forecasting method, trading
strategy, execution rule, or copy of the private Syntalium production engine.

## Proof Envelope

A V1 proof is one JSON object with exactly these members:

| Member | Required value |
| --- | --- |
| `spec_version` | String `SNAP-PROOF-1` |
| `hash_algorithm` | String `SHA-256` |
| `canonicalization` | String `SNAP-C14N-1` |
| `payload` | JSON object conforming to the value rules below |
| `fingerprint_sha256` | 64 lowercase hexadecimal characters |

Only `payload` is canonicalized and hashed. The other envelope members describe
how to verify it and carry the expected fingerprint. Envelope key order and
envelope whitespace are not part of the fingerprint.

## Allowed JSON Values

The payload may recursively contain:

- object;
- array;
- string;
- integer;
- boolean;
- `null`.

Floating-point numbers are forbidden, including values written with a decimal
point or exponent. Non-finite values such as `NaN`, `Infinity`, and
`-Infinity` are also forbidden. These restrictions avoid cross-language numeric
ambiguity.

Duplicate object keys are forbidden at every level. A parser must reject them
before canonicalization instead of silently keeping one value.

## `SNAP-C14N-1` Algorithm

Given a valid `payload`:

1. Parse the source as UTF-8 JSON while rejecting duplicate keys, floats, and
   non-finite numbers.
2. Sort every object's keys lexicographically by Unicode code point.
3. Serialize JSON with no insignificant whitespace: use `,` between array or
   object elements and `:` between a key and value, with no adjacent spaces.
4. Emit strings as JSON strings. Preserve Unicode characters rather than
   converting non-ASCII characters to `\uXXXX` escapes. JSON-required escaping
   for quotation marks, reverse solidus, and control characters still applies.
5. Do not apply Unicode normalization or case conversion.
6. Encode the serialized payload as UTF-8 bytes.
7. Compute SHA-256 over those bytes.
8. Encode the 32-byte digest as exactly 64 lowercase hexadecimal characters.

In Python, the serialization step is equivalent to:

```python
json.dumps(
    payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")
```

The equivalence applies only after the contract's duplicate-key and
floating-point rejection rules have been enforced.

## Verification Result

Verification succeeds when the independently computed lowercase SHA-256
fingerprint is equal to `fingerprint_sha256`. Implementations should use a
constant-time comparison where available.

Changing a payload value, key, array order, or string content changes the
canonical bytes and therefore should cause verification to fail against the
original fingerprint. Changing only insignificant source whitespace or object
key order does not change the fingerprint.

## Security and Evidence Boundary

This mechanism establishes deterministic record integrity. It does not
establish who created the record, when it first existed, whether a forecast was
accurate, whether a strategy was profitable, whether the private production
engine operated correctly, or what the market will do next. Those are separate
claims requiring separate evidence.
