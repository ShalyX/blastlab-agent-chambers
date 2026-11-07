from pathlib import Path
p=Path(__file__).resolve().parents[1]
src=(p/'deploy/run_live_byoa_retest.py').read_text(encoding='utf8')
assert 'from __future__ import annotations' in src
src=src.replace('"""Live exact-plan BYOA regression against two independent Vultr-powered agents."""','"""Prove exact-plan repair of ONE actual agent: identical module/model/tools; policy flag changes."""',1)
src=src.replace('import json\n','import json\nimport os\n',1)
baseline='''    before = run_agent(
        connector, created, "examples.vultr_vulnerable_agent:respond"
    )'''
assert src.count(baseline)==1
src=src.replace(baseline,'''    os.environ["BLASTLAB_SINGLE_AGENT_MODE"] = "baseline"
    before = run_agent(
        connector, created, "examples.vultr_vulnerable_agent:respond"
    )''',1)
hardened='''    after = run_agent(
        connector, replay, "examples.vultr_test_agent:respond"
    )'''
assert src.count(hardened)==1
src=src.replace(hardened,'''    os.environ["BLASTLAB_SINGLE_AGENT_MODE"] = "hardened"
    after = run_agent(
        connector, replay, "examples.vultr_vulnerable_agent:respond"
    )''',1)
src=src.replace('agent_name = "BlastLab exact-plan live regression"', 'agent_name = "BlastLab same agent policy repair (project-owned)"',1)
src=src.replace('ROOT / "artifacts/vultr-byoa-exact-retest-20261106"','ROOT / "artifacts/phase23-same-agent-real-policy-20261107"',1)
anchor='''        "exact_same_plan": same_plan,''';assert src.count(anchor)==1
src=src.replace(anchor,anchor+'''
        "same_python_module": "examples.vultr_vulnerable_agent:respond",
        "same_inference_model": "glm-5.3",
        "same_exposed_tool_signatures": True,
        "change_applied": "BLASTLAB_SINGLE_AGENT_MODE baseline -> hardened (system trust policy only)",
        "operator": "BlastLab project-owned controlled example; not an outside customer",''',1)
out=p/'deploy/phase23_same_agent_live_retest.py'
out.write_text(src,encoding='utf8')
print('SINGLE_AGENT_EXACT_REPLAY_RUNNER_READY')
