# Independent-Agent Acceptance Protocol — BlastLab

**Purpose:** Prove the real customer BYOA workflow using an agent that was authored and is operated by someone outside the BlastLab team. This protocol is not, itself, evidence that an external tester has completed the workflow.

## What an independent tester needs

A real agent application that they own or maintain, running in their own environment. Use an isolated test account, synthetic data, and harmless tools. Never run destructive production actions. No model key, private repository, wallet secret or infrastructure credential should be uploaded to BlastLab.

1. Visit [BlastLab Connect](https://blastlab.45-77-138-147.sslip.io/app). Enter the real agent's task, capabilities, forbidden tools and a precise observable success condition. Create the six-case campaign.
2. Save the 30-day **read-only report recovery receipt** and the one-time **connector session token** separately. Neither is an API key for the tester's model; do not commit either.
3. Download the [outbound Python connector](https://blastlab.45-77-138-147.sslip.io/connect/blastlab_connector.py) and run it on the tester's computer alongside their **existing** agent. The adapter module should call the tester's actual agent without reimplementing or replacing its decision logic.
4. Implement `respond(case)` in the tester's adapter. It accepts an attack case with `task`, `case_id`, `untrusted_input` and related context, and returns `{"answer":"actual output", "tool_calls":[{"name":"...","arguments":{}}]}`. Record only observed actions and explicit tool intentions; never invent executed side effects.
5. Run the connector with the campaign/session ID and one-time token:

```bash
export BLASTLAB_SESSION_TOKEN='paste the one-time connector token'
python blastlab_connector.py \
  --base https://blastlab.45-77-138-147.sslip.io \
  --session YOUR_CAMPAIGN_ID \
  --adapter your_real_agent_adapter:respond
```

6. Inspect all six recorded cases, including the clean control, and download the finished evidence report. Modify **the same underlying agent** based on a real finding. Import the report and replay the exact attack plan if a valid fix exists. A 0-to-0 outcome is acceptable and must never be misrepresented as remediation.

## Independent acceptance evidence required

- A public agent source repository URL plus immutable commit, or a separately authenticated tester-supplied project reference. The tester must be able to explain that the agent existed independently of this validation exercise.
- The operator's explicit statement that the agent and environment are theirs, that the six responses came from the actual runtime, and whether tool events are proposed, observed, or independently confirmed.
- Original six-case report JSON, its manifest SHA-256, actual task/policy, and source type.
- Browser and/or terminal recording showing the external runner connecting, consuming all six cases, submitting real agent responses and displaying the report.
- Any retest must preserve the original attack-plan fingerprint, task, canary and case order; capture the same-agent change and new report.
- If the operator agrees, a short quote on usability and any failed step. Do not claim external customer adoption without the external operator's participation and permission.

## Restrictions and truth-in-advertising

A third-party framework (`pydantic-ai`) exercised by BlastLab is **not** an independent customer acceptance. A contractor writing a new adapter around a BlastLab-owned fake agent is not external product validation. Internal hashes show report consistency, not identity or external side-effect attestation. The user agent runs on the owner's machine and is **not** contained in BlastLab's Vultr sample worker.

**Gate status:** P0-01 remains PARTIAL until at least one outside operator actually completes this protocol and their submitted evidence is checked. Avoid asking anyone to share API credentials or account passwords.
