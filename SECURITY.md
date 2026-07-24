# Security and Public Disclosure Policy

## Purpose

This repository exposes a small, independent proof layer for Syntalium. Its
purpose is to let anyone reproduce canonical JSON serialization, SHA-256
fingerprinting, and tamper detection without access to the private production
system.

The public proof layer and the private intelligence layer have different
disclosure boundaries:

- The **proof layer is public**: its contract, schema, sanitized fixtures,
  independent verifier, tests, and CI workflow may be published.
- The **intelligence edge is private**: production source code, model logic,
  features, weights, thresholds, trading rules, infrastructure, and runtime
  data must not be published here.

## Allowed Public Material

The following material may be added after a disclosure review:

- public proof specifications and schemas;
- independent reference verification code;
- synthetic, sanitized test fixtures clearly labelled as non-production;
- tests for canonicalization, hashing, and tamper detection;
- public API documentation that contains no private configuration;
- high-level architecture descriptions that do not reveal the intelligence
  edge or infrastructure details.

## Material That Must Never Be Published

Do not commit, paste into issues, attach to releases, or expose in CI output:

- passwords, tokens, API keys, SSH keys, credentials, or `.env` files,
  including production-derived example files;
- private SignalX/Syntalium engine or production source code;
- models, model artifacts, checkpoints, weights, or training data;
- exact feature formulas, feature weights, thresholds, or proprietary
  decision logic;
- entry, stop-loss, take-profit, execution, or other trading rules;
- server addresses, IP addresses, databases, private logs, deployment
  configuration, or runtime state;
- user data, unreleased exports, or any material not cleared for public
  disclosure.

The `.gitignore` file is a guardrail, not a substitute for review. Every
contributor remains responsible for inspecting staged changes before a commit.

## What Verification Proves

A successful verification proves only that:

1. the published `payload` has a deterministic canonical byte representation;
2. the SHA-256 fingerprint in its envelope matches those bytes; and
3. a later change to the payload is detectable when the original fingerprint
   is retained.

It does **not** prove model accuracy, forecast quality, profitability, complete
production-engine operation, publication time by itself, or future market
performance.

## Reporting a Security Concern

Do not include secrets or sensitive evidence in a public issue. Submit security
reports through this repository's **GitHub Security Advisories** private
reporting feature if it is available. If private reporting is unavailable, do
not disclose sensitive details publicly; repository maintainers should enable a
safe private reporting channel before requesting the material.
