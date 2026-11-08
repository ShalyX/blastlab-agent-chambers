# Testing an agent you own

Start at the [Chamber Library](https://blastlab.45-77-138-147.sslip.io/app).
The Web Chamber is available; the other four chambers are planned.

## Hosted Web flow

Select The Web and choose a legitimate mission. Configure the permitted and
forbidden capabilities, create the campaign, then upload an adapter that calls
your agent. Follow [the Web adapter guide](web-chamber.md). BlastLab runs the
source in a restricted worker while a separate Chromium worker reads the
synthetic supplier pages. Provider credentials stay on the trusted host.

Inspect policy findings, numeric mission results and the runtime receipt.
Export the completed report. After changing your agent, use exact retest to
preserve the mission, policy, canary and attacks while comparing revised source.
An unchanged or worse result is valid evidence and should remain visible.

## Existing local runtimes

For the external connector, use `/app/connect` and follow its generated command.
Your adapter exposes `respond(case)` and returns the actual answer and declared
tool calls. The connector runs in your environment; BlastLab does not enforce
isolation of that process. Keep the one-time campaign token outside source.

## Data and report boundaries

Use synthetic data and harmless capabilities. Upload only the source you intend
to test, without credentials, private customer data or production secrets.
Save the read-only report recovery key privately; it cannot execute an agent.

Reports distinguish host-observed execution from runner-reported results.
Declared tool intentions are not proof of executed side effects. Hashes verify
internal report consistency, not independent authorship or universal safety.
