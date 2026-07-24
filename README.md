<div align="center">

Syntalium

Verifiable AI crypto market intelligence

Market context, signal lifecycle, and cryptographic publication proof — built for independent verification.

Website ·Verify ·Telegram ·X ·Medium

</div>

What Syntalium is

Syntalium is an independent crypto market-intelligence project focused on a simple principle:

Open the proof layer. Protect the intelligence layer.

The system collects market data, evaluates multi-timeframe context, produces structured market decisions, and publishes a verifiable record of what was known at publication time.

Syntalium is not designed to hide changed predictions behind edited posts. Public records are tied to canonical payloads and SHA-256 fingerprints so that their integrity can be checked independently.

How the proof layer works

Market data
    ↓
Validation and closed-candle controls
    ↓
Feature and market-context analysis
    ↓
Model-assisted decision pipeline
    ↓
Publication and runtime safety gates
    ↓
Canonical SNAP payload
    ↓
SHA-256 fingerprint
    ↓
Website + Telegram publication
    ↓
Public verification

A SNAP record captures a structured decision state. Its canonical representation is hashed with SHA-256 and exposed through the public verification layer.

The proof layer is intended to answer:

What was recorded?

When was it published?

Has the published payload changed?

How did the record evolve through its lifecycle?

Verification proves record integrity and publication history. It does not guarantee predictive accuracy, profitability, or future market outcomes.

Public engineering principles

Closed-candle discipline — decisions are based on completed market intervals.

Canonical records — the same normalized payload produces the same fingerprint.

SHA-256 verification — public records can be checked independently.

Lifecycle transparency — records can move from open to management and close states.

Anti-repaint design — published history is preserved rather than silently rewritten.

Fail-closed behavior — unavailable or unhealthy inputs should block unsupported output instead of being replaced with fabricated data.

Public proof, private edge — verification contracts are public; sensitive model and execution logic remain private.

High-level architecture

flowchart LR
    A[Market Data Sources] --> B[Collection & Validation]
    B --> C[Market Context & Feature Layer]
    C --> D[Model-Assisted Decision Engine]
    D --> E[Safety & Publication Gates]
    E --> F[Canonical SNAP Record]
    F --> G[SHA-256 Fingerprint]
    G --> H[Website]
    G --> I[Telegram]
    H --> J[Public Verify Layer]
    I --> J

The diagram deliberately describes component boundaries without exposing credentials, model artifacts, private infrastructure, or proprietary decision formulas.

Technology currently represented

Python intelligence and publication services

Next.js and TypeScript public interface

Telegram alert and lifecycle-notification layer

REST-style public data and verification endpoints

Canonical JSON payloads and SHA-256 fingerprints

Sanitized verification examples and public research exports

Automated testing for proof, routing, and publication behavior

Disclosure boundary

Public

Described at a high level

Private

SNAP concepts and verification flow

Feature families and market-context pipeline

API keys, tokens, credentials, and .env files

Canonical payload examples

Model governance and champion/challenger process

Model artifacts, weights, and exact feature formulas

SHA-256 reference verification

Runtime health and publication safeguards

Exact thresholds and proprietary decision rules

Public API contracts

Multi-timeframe analysis architecture

Entry, stop-loss, take-profit, and execution logic

Signal lifecycle semantics

Data-quality and closed-candle controls

VPS, IP addresses, database contents, and deployment configuration

Sanitized test fixtures

Integration boundaries

Private logs, user data, and unreleased source code

Public interfaces

Product and public record: syntalium.com

SNAP verification: syntalium.com/verify

Alerts and lifecycle updates: Telegram @Syntalium

Project updates: X @Syntalium

Technical articles: Medium @Syntalium

What will be opened next

The public technology layer is being prepared in small, auditable releases:

SNAP format and canonicalization notes

Sanitized payload and verification examples

Machine-readable public schemas

Reference SHA-256 verifier

Public API contracts

Architecture and integration documentation

Reproducible verification tests

No private production source will be copied into this repository without a dedicated security and disclosure review.

Responsible use

Syntalium provides market intelligence and publication verification. It does not provide guaranteed returns, custody services, or individualized financial advice. Crypto markets involve substantial risk; users remain responsible for their own decisions.

<div align="center">

Syntalium — verify the record, then evaluate the intelligence.

</div>
