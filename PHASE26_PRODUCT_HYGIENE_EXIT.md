# BlastLab — Phase 26 PRODUCT_HYGIENE exit audit

**Date:** November 7, 2026
**Operator stage:** 26 / PRODUCT_HYGIENE
**Decision:** Engineering and public launch hygiene **PASS**, with independent outside-developer validation still deferred, not fabricated. Not a hackathon submission or universal accessibility certification.

## User-installed skills actually applied

Read and applied the installed Windows PC instructions directly, not just the skill names:

- C:/Users/USER/.codex/skills/public-project-launch-hygiene/SKILL.md — 15-point project identity, repository, public link, social card, evidence and submission integrity workflow.
- C:/Users/USER/.codex/skills/production-ready-web-apps/SKILL.md — real-path reliability, state/timeout/error bounds, source-of-truth and public production verification workflow.

Both skill manifests declare reconstructed installation metadata, not a verified original release version. This audit is the real-product BYOA update; old supplier/Docker Chamber Hygiene notes are preserved as historical material in HYGIENE.md.

## Launch hygiene checklist — verified and scoped

| Skill step | Status | What was actually checked or changed |
|---|---|---|
| 1. Canonical product identity | PASS | BlastLab — Bring Your Own Agent Security Testing, governed by PRODUCT.md revision 4 |
| 2. Canonical URL and repository | PASS | Public BYOA app /app, public proof /proof, repository ShalyX/blastlab-agent-chambers |
| 3. Naming in site/source/README | PASS | Corrected stale HTML title, description, Open Graph/Twitter text, shared UI footer and npm package name from old control-room demo to blastlab-agent-lab |
| 4. Secrets and private material | PASS scoped | No raw report bundles, recovery receipts, .env or SSH keys staged. Gitignore excludes local artifacts, raw output and environments. Git staging is scanned again before push |
| 5. Gitignore and history | PASS scoped | No .env secrets, generated dist, screenshot QA folders, or private raw test reports intentionally added. Public historical files remain clearly labeled |
| 6. Demo and obsolete content | PASS scoped | Supplier Web Chamber remains explicitly DEMO. Older README preserved as archived historical material; front-page README now describes actual BYOA task/attack/fix/retest |
| 7. Reproducible build/run instructions | PASS | Current README includes correct Python connector invocation, allowed/forbidden tool policy, recovery and exact replay; frontend npm build passed |
| 8. License/attribution | PASS | LICENSE exists; current README links to MIT license |
| 9. Favicon, logo and social preview | PASS | Existing BlastLab icon retained; stale supplier-containment Open Graph screenshot replaced with a real 1200×630 screenshot of the actual /app BYOA hero; public sha256 compared exactly with local build |
| 10. Domain quality | KNOWN LIMITATION | HTTPS sslip.io address is temporary, explicitly disclosed. No custom domain invented or claimed |
| 11. Fresh actual screenshots | PASS | Browser screenshots for seven public routes at desktop 1440 and mobile 390, plus a screenshot-derived current public social card |
| 12. Proof links and integration | PASS | Twelve public URLs returned HTTP 200, including the downloadable connector, tester instructions, proof JSON, social card and favicon. All nine current README relative links resolved locally |
| 13. Recorded/live provenance labels | PASS | Real owner-run BYOA, first-party contained worker, founder TermProof, PydanticAI framework and historical supplier DEMO still clearly differentiated; no unsigned hash turned into identity attestation |
| 14. Production verification | PASS | Static bundle built, deployed with immutable backups, validated page and OG hashes, API health; desktop/mobile logged-out route QA and independent mocked UI-flow checks passed |
| 15. Submission-form integrity | DEFERRED to submission phases | Not represented as a completed hackathon form, finished judge video, or submission receipt. The later Operator phases have separate gates |

## Production readiness and accessibility observations

- Public route audit: **14 checks** (seven URL routes at desktop/mobile), zero measured missing labels, horizontal overflow or unsafe target-blank attributes.
- Public UI workflow: **six checks**, covering user-visible quota error with retained form state, completed report after reload and pending connector/token-accessible control, each at 1440px and 390px.
- Exact report proof page previously passed eight live proof-lane desktop/mobile checks; the Phase25 Red Team confirmed malicious report HTML and Unicode rendered inert, without network exfiltration or script execution.
- Favicon/OG/public index and app route publicly reachable; OG screenshot is an actual current UI capture, not a simulated agent result.
- Accessibility changes: named one-time join-token copy button, non-form token/terminal labels corrected semantically, external target links given noopener + noreferrer.
- HTML content metadata now describes the actual BYOA product rather than prior supplier containment. The site footer also uses BYOA identity.
- Three intentionally skipped existing Python tests remain documented; **295 executable tests passed** in the immediately preceding completed Phase25 isolated regression. No Python controller or core grading logic was changed during this Phase26 web/docs pass.
- Scope limitation: browser DOM/keyboard/label and responsive checks do not constitute a certified WCAG conformance audit or broad assistive-technology study.
- Product limitations from the lock remain: external actions are runner-reported; unsigned report manifests do not authenticate runner identity; account-wide history and purge are not implemented; project-owned containment is not sandboxed customer agent execution.

## Deployment and preservation

- First guarded static release: deploy/phase26_hygiene_publish.py, deploy/phase26_hygiene_install.sh, remote backup /opt/blastlab/backups/20261107-phase26-hygiene.
- Final footer correction: deploy/phase26_hygiene_v2_publish.py, deploy/phase26_hygiene_v2_install.sh, remote backup /opt/blastlab/backups/20261107-phase26-hygiene-v2.
- Both releases returned PHASE26_PRODUCT_HYGIENE_RELEASE_PASS; controller endpoint remained healthy and no model API credentials/code were changed.
- Before replacing the historical uncommitted README, its exact original copy was saved locally at ignored artifacts/phase26-hygiene/README.before-phase26.md and as docs/legacy/README_supplier_demo_20261105.md with an archival warning.
- The new live social card is web/public/og-card.png, actual current product UI captured from local production build via Chrome Playwright. Public integrity SHA-256: ced16d352b325d87512707daf65606db150c278af2cc5bc924ca9fb868df6bfd.

## Gate handoff / what is not claimed

The technical Product Hygiene work is complete for the current locked BYOA product. **Phase 26 PASS does not mark Phase24 independent-customer adoption as verified.** The owner-directed outside developer deferral remains OPEN and mandatory before Submission Audit. We did not create a fake identity or a fake source signature.

**Next adjacent Operator phase:** 27 — DEMO_PRODUCTION. This needs a real demonstration of the shipped BYOA workflow and a high-quality captured walkthrough; old supplier demo clips are not evidence of a customer BYOA run. Judge Simulation, Feature Freeze and Submission Audit are separate later gates.

No submission is claimed or implied by the Product Hygiene exit.


## Final gate regression and checked production bundle

- Final full backend regression after Phase26 source/document changes: 20 executable test modules, **295 tests run, 3 skipped, zero failures**. Two zero-test support modules excluded.
- Final publicly served Chromium user-journey checks: six mocked error/recovery/connection states in desktop and mobile, 6/6 PASS. Browser route/accessibility/overflow audit: 14/14 PASS, zero issues.
- Public resource audit: 12 URLs return 200. HTML and loaded JS **exactly match** local Vite production build by SHA-256; corrected real-product footer is present.
- Final social preview matches deployed screenshot digest ced16d352b325d87512707daf65606db150c278af2cc5bc924ca9fb868df6bfd; temporary sslip.io hostname disclosed.
- Product Hygiene PASS does not waive external customer validation, signed external runner origin, full account history/purge, certified WCAG conformance, sponsor submission audit or final demo proof. Subsequent phases are separately gated.
