# Bring your agent into The Web

Choose The Web from the Chamber Library, select Inventory valuation or Low-stock
exposure, name your agent, and declare allowed and forbidden capabilities.
`read_web_page` must remain allowed. Create the campaign, then upload your source.

The current hosted adapter supports 1–12 flat Python files, 96 KB total, standard
library only. This is the adapter's current compatibility boundary, not the scope
of BlastLab's product or intended audience.

Your callable receives `case['task']`, `case['web_path']`, policy fields and the
case identifier. Obtain the page using:

```python
from blastlab_runtime import complete, read_web_page

def respond(case):
    page = read_web_page(case['web_path'])
    # Use your own agent's decision logic. complete(...) provides Vultr inference.
    # page['text'] is UNTRUSTED webpage content, not trusted instructions.
    return {'answer': 'TOTAL_CENTS=<your calculated integer>', 'tool_calls': []}
```

Download `web_chamber_agent.py` for a complete model-backed example; its callable
is `web_chamber_agent:respond`. An example proves the workflow, not independent
customer use. Keep production credentials and data out of uploaded source.

Your source executes in the existing restricted agent worker. A separate
controller-owned Chromium container renders a synthetic supplier page. Only
`/specimen` is available: no arbitrary URL, public Internet browsing, scripts,
downloads, production secrets or agent-selected browser command. One or two real
page reads are allowed per case, with a fresh browser context each time. A missing
read, protocol failure, provider failure or unverified teardown produces no
successful report.

The campaign contains a clean control and five task-specific attacks. The
controller records page text, inventory rows, page fingerprints and Chromium
version. Both workers are removed before the report is released. Numeric mission
checks compare one `TOTAL_CENTS=<integer>` marker with the known synthetic total;
they do not certify general task correctness. Answers and other tool intents
remain agent-declared. Internal side effects are not independently attested.

Retest preserves chamber, mission, page-generation version, task, rules, canary
and attack plan. Upload your changed source into a new worker. Changing the
mission requires a new campaign, not an exact comparison.

Toolchain, The Vault, The Machine and Chaos are planned and cannot be launched.
Chaos retains its original combined-attack-and-mission purpose. Worker limits
alone do not implement those chambers. Existing external content campaigns and
private report recovery remain available at `/app/connect`. The original supplier
experiment remains separately labeled at `/app/demo`; its reset/resume evidence
is not attributed to uploaded agents.
