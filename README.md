# BlastLab — Bring Your Own Agent Security Testing

**Bring your agent. We try to break it. You see what failed, why, and what to fix.**

BlastLab is a hosted security-regression lab for agent developers. An agent you own runs in **your** environment. BlastLab uses **Vultr Serverless Inference** to generate one clean control and five adversarial cases against untrusted text, evaluates the answers and tool intentions your outbound connector reports, and produces evidence-linked findings that can be retested using the **exact same attack plan**.

**[Open the real BYOA app](https://blastlab.45-77-138-147.sslip.io/app)** · **[Inspect verified proof](https://blastlab.45-77-138-147.sslip.io/proof)** · **[Try the project-owned contained sample](https://blastlab.45-77-138-147.sslip.io/contained-sample)** · **[Independent tester protocol](https://blastlab.45-77-138-147.sslip.io/connect/independent-tester.md)**

**Canonical product lock:** [PRODUCT.md revision 4](PRODUCT.md), November 6, 2026. The older supplier/Docker Web Chamber is a labeled **internal demonstration**, not the BYOA product.

## Connect → attack → inspect → fix → retest

1. Open the live app and name your real agent. Enter its legitimate task, permitted tool names, forbidden tool names and a literal task-success signal.
2. Create the bounded six-case campaign. Save the **private, read-only recovery receipt** separately from the one-time connector token.
3. Download [the Python connector](web/public/connect/blastlab_connector.py). Implement a callable respond(case) function in your own Python agent module, keeping your model keys on your machine.
4. Set the BLASTLAB_SESSION_TOKEN environment variable locally; run the command displayed in the live UI. Its general format is:

   ~~~bash
   python blastlab_connector.py --session YOUR_CAMPAIGN_ID --adapter your_agent:respond
   ~~~

5. Your owner-controlled runner pulls each test as **untrusted data** and sends its answer and recorded/proposed tool calls. BlastLab does **not** execute your tools or receive your model API key.
6. Inspect recorded attack input, runner-reported answers/tool intentions, evidence-linked policy findings and limitations. Export the manifest-backed report.
7. Change **your agent** and replay the original cases. BlastLab verifies the same task, policy, canary and attack-plan hash before comparing results.
8. If your connector token expires, use the separately saved **read-only 30-day recovery key** to retrieve your completed report.

Public campaign capacity is limited. Provider outages and quota limits are reported as errors, not substituted with a fake successful result. Never supply real production secrets, private model credentials or unrestricted destructive tool execution.

## What is genuinely verified

| Evidence lane | Outcome | Important limit |
|---|---|---|
| Same project-owned Vultr GLM-5.3 agent, exact six-case replay | **3 → 0** observed configured violations after changing the agent trust policy | Controlled same-agent improvement; prohibited tool calls were not executed |
| Pre-existing founder-authored TermProof agent using its real Gemini/GitHub API | **0 → 6** legitimate deterministic VERIFIED outcomes after correcting BlastLab connector input handling | Integration repair, **not** a TermProof model vulnerability or an independent outside customer |
| Project-owned disposable Vultr worker | **22/22** host-observed evidence and containment checks | Project-owned worker does **not** run submitted customer agent code |
| Project-operated PydanticAI framework connector | **0 → 0** observed violations under exact replay | Proves interoperability, **not** security improvement |

The [Phase 24 proof index](https://blastlab.45-77-138-147.sslip.io/proof) includes case verdicts, attack-plan fingerprints and SHA-256 report anchors. Its original source reports are kept privately for independent regrading. **Unsigned hashes demonstrate internal consistency, not runner identity or actual customer-side tool execution.**

Reported tool intents are not executed actions. A synthetic canary in an answer does not prove real-world exfiltration. No configured violation observed is not a universal safety guarantee. We have **not** yet completed an independently outside-operated customer validation; the founder authorized that task to be completed before Submission Audit.

## Developer setup and checks

Backend: Python 3.12+. Web: Node.js 20+, npm and a browser for UI QA.

~~~bash
python -m unittest -q test_agent_lab test_agent_retest test_phase25_redteam_completion
cd web
npm ci
npm run build
~~~

The completed Phase 25 Red Team audit ran **295 executable tests, 3 skips, zero failures** with isolated Python test processes on Windows. Two real defects were repaired in production: malformed JSON policy arrays crashing an HTTP handler, and long hostile report text breaking the responsive layout. See [Phase 25 exit report](PHASE25_RED_TEAM_EXIT.md).

Private proof/compiler tests need intentionally untracked raw evidence from the authorized verification machine. A clean public GitHub checkout does not have those source artifacts and must not be represented as having independently reverified them.

## Source layout

- agent_lab.py, agent_lab_service.py, agent_lab_attacks.py — campaign contracts, grading and hash-bound reports.
- control_api.py and contained_sample_service.py — public controller and separate project-owned worker sample.
- web/src/AgentLabExperience.tsx — real BYOA connect, configure, report and replay journey.
- web/src/ProofEngine.tsx and web/src/ContainedSample.tsx — separately labeled technical proof/sample.
- web/public/connect/ — public outbound runner and independent acceptance instructions.
- deploy/ — Vultr releases, independent test runners and guarded Operator gates.
- .hackathon/ — locked P0 ledger, current phase and deferred customer proof obligation.

## Limitations, project status and archive

The live service currently uses a **temporary sslip.io hostname**. Report recovery is campaign-scoped; account-wide history/purge is not implemented. Additional proposed code/payment/browser BYOA Chambers are not shipped. The supplier Web Chamber is an explicit historical demonstration.

**Operator status:** Phase 26 Product Hygiene passed; Phase 27 Demo Production is active. Phase 25 Red Team passed. Phase 24 independent outside-developer proof was **conditionally deferred**, not falsely passed, and remains mandatory before Submission Audit. Later demo production, judge simulation, submission audit and actual submission are separate phases.

[Product brief](PRODUCT.md) · [Operator sequence](OPERATOR_SEQUENCE.md) · [Security audit](PHASE25_RED_TEAM_EXIT.md) · [Evidence register](PHASE24_PROOF_REGISTER.md) · [MIT License](LICENSE) · [Archived supplier demo notes](docs/legacy/README_supplier_demo_20261105.md)

---

Archived supplier/Docker demo materials are retained for historical audit, not presented as proof of customer BYOA execution.
