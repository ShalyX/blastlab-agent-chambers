# BlastLab — LabLab submission packet
**Event:** Vultr: Agent Rush Hackathon — Challenge 1: Blast Radius Zero
**Status:** READY TO ENTER. **NOT officially submitted until LabLab confirms receipt.**
**Date:** 5 November 2026

## Project information

### Submission title (max 50 characters)
BlastLab — Agent Containment Test Facility

### Short description (max 255 characters)
Crash-test browser agents against hostile web pages on Vultr. Choose an authorized mission and injection scenario, run a Docker-isolated agent, and receive verifiable containment, recovery, and remediation evidence.

### Long description (minimum 100 words)
BlastLab is a controlled crash-testing facility for autonomous browser agents. Instead of asking whether an agent is "safe," it puts a legitimate task next to a hostile data source and records what actually happens at the tool boundary.

The first operational Chamber, The Web, lets developers choose between inventory valuation and low-stock exposure missions, plus a clean baseline or four adversarial page scenarios: role spoofing, exfiltration bait, receipt forgery, and compound injection. Attack text is served as untrusted supplier content; public users cannot supply arbitrary URLs or executable commands.

A trusted supervisor running on a Vultr Cloud Compute VM orchestrates each run. Genuine GLM-5.3 agent decisions come through Vultr Serverless Inference and are checked by an independent, exact-capability policy before the agent accesses a Docker-isolated Chromium worker. The sandbox has no outbound network, host mounts or inherited secrets. A scheduled interruption destroys the first worker, verifies removal and resumes a trusted checkpoint in a fresh browser. The legitimate result must agree with freshly read browser evidence.

For public judges, rate-limited scripted policy challenges exercise the same Docker boundary without spending inference credits. Scripted forbidden proposals are explicitly distinguished from genuine model behavior. Reports show allowed and denied proposals, task completion, containment and recovery checks, untested coverage and evidence-based remediation.

Each exported run contains a standalone, independently verifiable sanitized SHA-256 event chain and offline Python verifier. Its public digest is expressly distinguished from the private raw trace hash. The Web Chamber works today; Toolchain, Vault, Machine and Chaos remain visibly unimplemented.

### Challenge / track
**Blast Radius Zero** — isolated browser agent execution and verifiable containment.

### Technologies / tags
Vultr Cloud Compute, Vultr Serverless Inference, GLM-5.3, Docker, Chromium, Playwright, Python, TypeScript, React, Agentic AI, AI Security, Prompt Injection, Browser Automation.

## Presentation and media
- **Cover image (1600×900, 16:9):** https://blastlab.45-77-138-147.sslip.io/media/BlastLab-Cover.png
- **Demo video (MP4, 80 seconds, ~4.3 MB, H.264 + AAC):** https://blastlab.45-77-138-147.sslip.io/media/BlastLab-Agent-Rush.mp4
- **Slide presentation (seven-slide PowerPoint):** https://blastlab.45-77-138-147.sslip.io/media/BlastLab-Vultr-Agent-Rush.pptx

## App and source
- **Public GitHub repository:** https://github.com/ShalyX/blastlab-agent-chambers
- **Demo application platform:** Vultr Cloud Compute VM; Docker/Chromium worker isolation; GLM-5.3 via Vultr Serverless Inference
- **Application URL (Chamber Library):** https://blastlab.45-77-138-147.sslip.io/app
- **Configure Web Chamber:** https://blastlab.45-77-138-147.sslip.io/app/chambers/web
- **Verified scripted Web run:** https://blastlab.45-77-138-147.sslip.io/app/results?run=scripted-99bb851e7f39b5ba82
- **Verified live GLM-5.3 Web run:** https://blastlab.45-77-138-147.sslip.io/app/results?run=live-fc49cc39d3fba372b5
- **Public offline chain verifier:** https://blastlab.45-77-138-147.sslip.io/verify_public_evidence.py

## Suggested additional information for reviewers
To evaluate the product, open the Web Chamber, choose "Low-stock exposure" and "Receipt forgery", keep "Scripted attack fixture" selected, then launch the contained test. The public service executes real Docker/Chromium on Vultr and returns a persistent report, trace, remediation and independently verifiable event chain. For genuine LLM-proposed actions, open the archived GLM-5.3 run separately. In that run, the model read a hostile page but proposed **zero forbidden actions**; the intentionally blocked receipt forgery came from a **scripted fixture**. The reset is a **supervisor-scheduled fault injection**, not automatic intrusion detection. All non-Web Chambers are planned, not runnable.

## Official submission checklist
- [x] Title under 50 characters
- [x] Short description under 255 characters
- [x] Long description over 100 words
- [x] Challenge/technology details
- [x] 16:9 cover image, publicly reachable
- [x] Video presentation under 5 minutes and under 300 MB, publicly reachable
- [x] Public slide presentation
- [x] Public GitHub source under MIT license
- [x] Live application URL, publicly reachable
- [ ] Verify LabLab event enrollment and team-admin submission access
- [ ] Paste project information and submit on LabLab
- [ ] Capture LabLab confirmation and final submission URL

**Do not claim submitted until the last three boxes are checked.** Vultr Community sharing is optional and not the LabLab submission.
