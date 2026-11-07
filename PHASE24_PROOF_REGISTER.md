# Phase 24 — BlastLab Proof Engine verified evidence register

Verified directly against locally retained raw reports via agent_lab.verify_report and verify_import. This is **not** independent customer attestation.

| Evidence lane | Measurement | Attack plan SHA-256 | Final report manifest | Source provenance |
|---|---|---|---|---|
| Same agent: real security mitigation | 3 to 0 | 2732ec1be39b0d13f983ab9f85801a00d5014fceee2df36f59a85d10d12e7b4c | 8d1576c586f22ad74dd0ce6937970a0678cb59836ad7469173b6a29526650e22 | PROJECT_OWNED |
| Preexisting agent: legitimate task recovery | 0 to 6 | abf18ceceb0d6323c47d4a646ba67e1bce13648a91e6e0691ecb86cdb389420f | 09d21a114653fabe65326d697a5ca3b6b3acdc3c53b154ec507a841fb1208921 | FOUNDER_OPERATED_PREEXISTING_CODEBASE |
| Vultr worker: contained execution | 22 / 22 | accfc093eb56c816eeb9eecf9dc3362de57b218da8f04a97fea2d01f7167d816 | df174f12b76ef45c6890656003f9bf53a0aa72bd4dfb7b21b6cb8dc2275007a0 | PROJECT_OWNED_WORKER |
| Third-party runtime compatibility | 0 to 0 | e76fdd2792257244a45a90847b128855c6216f9136be3f61dd00f89238b83864 | c56f68d278d6824d8ef96a30955e90357bccefa46a7bb48f11af7b26a5582e71 | PROJECT_OPERATED_PYDANTICAI |

## Reproduction

Run from a checkout with private local artifacts available:

    python -m deploy.phase24_compile_proof
    python -m unittest -q test_phase24_proof_engine

The public file at /proof/evidence.json contains only derived metrics, exact six-case verdicts and digest anchors, not the raw prompts/recovery receipts.
Without privately held full reports, the public index alone cannot reproduce event-chain verification. To verify privately, run the compiler against the retained raw source files.

## Strict limits and remaining Phase 24 proof obligations

- Independent non-founder agent owner/operator acceptance: not obtained.
- External tool execution is runner-reported; no independent attestation of hidden side effects.
- SHA-256 report/event manifests are unsigned; they do not prove operator identity.
- No universal task-correctness guarantee from literal answer markers.
- Contained worker is project-owned and does not run customer-submitted code.
- Account-wide authenticated history/purge, full Chamber inventory and formal accessibility audit are not delivered.

Phase 24 remains OPEN until independent external operator proof and any necessary source-attribution improvements are documented. Do not claim runner-reported hidden actions are sandbox-observed.
