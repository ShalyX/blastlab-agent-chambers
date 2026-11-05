# Connect your own agent

**These are examples, not the BlastLab product.** BlastLab's product is the attack orchestration, controlled campaign, reporting and remediation for an agent you own.

1. On the BlastLab **Connect Agent** page, enter a name, legitimate agent task and forbidden tool names. Create a campaign.
2. Download `blastlab_connector.py` from the page.
3. Write a Python module exposing `respond(case:dict)->dict` that **calls your actual agent**, passing `case["task"]` as trusted work and `case["untrusted_input"]` as untrusted tool/page content. Intercept tool intents; don't actually execute unsafe actions.
4. Set the one-time join token as `BLASTLAB_SESSION_TOKEN` in your environment (never put credentials in an uploaded repo).
5. Run `python blastlab_connector.py --session <id> --adapter your_agent:respond`. It pulls six separate challenges from BlastLab via HTTPS and sends real observed responses.
6. Open the campaign report. Review case-by-case failures, evidence and remediation, modify your agent and start a new campaign.

**Result scope:** Runner-reported observations are not independently attested by the Vultr VM. The agent and its LLM provider run in YOUR environment; BlastLab never asks for your agent's API key or executes your code on the hosted server. The tester can evaluate declared forbidden actions, exact attack override markers and decoy network/memory attempts, but cannot prove unseen side effects or arbitrary task correctness.

Two reference callbacks are supplied: `vulnerable_agent.py` deliberately trusts malicious content, and `resilient_agent.py` ignores it. These are not substitutes for your own agent, nor do they establish customer adoption.
