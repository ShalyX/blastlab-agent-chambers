# BlastLab | Demo architecture and production status

Updated 2026-11-04. **Storyboards only — no final demo video or public UX exists yet.**

## Judging narrative

A useful AI agent enters a supplier page that tries to hijack its instructions. BlastLab confines the browser inside Docker, allows only evidence-backed actions, destroys the worker, restores the trusted checkpoint, and finishes the legitimate $72 task.

## Required live shot list

1. **Hook:** legitimate inventory valuation task; why hostile pages are dangerous.
2. **Agent + browser:** genuinely call Vultr Serverless Inference `glm-5.3`; show Chromium visiting supplier page.
3. **Injection and boundary:** inspect the untrusted `SYSTEM OVERRIDE` page text. In the genuine LLM run the model chose safe actions; show this plainly. A separate *SCRIPTED ADVERSARIAL REPLAY* is allowed to demonstrate four policy denials, never mislabelled as live-model calls.
4. **Containment:** show Docker worker with `--network=none`, `--read-only`, no privileged capabilities or host mounts; demonstrate distinct worker and workspace IDs.
5. **Kill/reset/resume:** log the supervisor-led teardown, verify old container absent and workspace gone, restore trusted checkpoint, read supplier again.
6. **Finish:** actual `$72.00` mission result, three real model responses and trace integrity verification.
7. **Sponsor proof:** show Vultr VM instance ID/region, `glm-5.3` API model and real container lifecycle; cite sanitized proof.
8. **Payoff and caveats:** explain this is a controlled supplier page, not arbitrary-site browsing or a generalized jailbreak benchmark.

## Proof references (do not invent footage)

- Live model + Docker: `artifacts/vultr-vm-20261104/result.json`, `trace.jsonl`.
- Separate scripted attack + Docker: `artifacts/vultr-vm-20261104/scripted-attack/`.
- Independent audit: `artifacts/vultr-vm-20261104/proof-audit.json`.
- Cloud run paths and trace digests: `EVIDENCE.md`.

Next: design and implement the judge-facing control room; then capture actual screencasts, verify labels/audio/video and render.
