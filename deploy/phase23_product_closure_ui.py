from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=root/'web/src/AgentLabExperience.tsx'
s=p.read_text(encoding='utf8')
assert "byoa-surface-inventory" not in s
anchor='    <div className="byoa-content">'
assert s.count(anchor)==1
inventory='''    <section className="byoa-surface-inventory" aria-labelledby="byoa-surface-heading">
      <div className="byoa-surface-top"><div><Kicker>CAPABILITY MAP / ACTUAL COVERAGE</Kicker>
        <h2 id="byoa-surface-heading">What this lab actually tests.</h2>
        <p>Attacks target the owner-hosted agent's text and reported tool intents. The connected agent stays in its own environment. This list is product capability, not a claim that every possible attack is covered.</p></div>
        <span className="byoa-surface-count">5 ATTACK FAMILIES + CLEAN CONTROL</span>
      </div>
      <div className="byoa-surface-grid">
        {[
          ['LIVE','Authority spoofing','Fake high-priority instructions in untrusted context'],
          ['LIVE','Tool-result injection','Hostile directions in reported tool/page content'],
          ['LIVE','Unauthorized actions','Detect reported proposals outside declared tool policy'],
          ['LIVE','Synthetic exfiltration bait','Detect reported canary disclosures or outbound proposals'],
          ['LIVE','Memory-poisoning attempts','Detect attempts to induce forbidden memory-write tools'],
          ['NOT INCLUDED','Customer runtime sandboxing','Your external agent is not executed inside the Vultr sample container'],
          ['NOT INCLUDED','Hidden side-effect attestation','BlastLab cannot independently observe external tool execution'],
          ['NOT INCLUDED','Browser, code and payment Chambers','Supplier Web Chamber is a separate DEMO; other Chambers are not live BYOA tests'],
        ].map(([status,name,description])=><div className="byoa-surface-item" key={name}>
          <span className={status==='LIVE'?'byoa-surface-live':'byoa-surface-planned'}>{status}</span>
          <strong>{name}</strong><small>{description}</small>
        </div>)}
      </div>
    </section>
'''
s=s.replace(anchor,inventory+anchor,1)
# Also the report needs a clear contract outcome -- a marker alone isn't proof of correctness.
anchor='<div className="byoa-report-kpis">'
assert s.count(anchor)==1
status='''        <section className="byoa-success-coverage" aria-label="Literal task success signal observations">
          <span>OWNER-DEFINED TASK SIGNAL / LITERAL ONLY</span>
          <strong>{report.results.filter(item=>item.task_success_signal==='ANSWER_CONTAINS_REQUIRED_TEXT').length}
          <small> / {report.tests_completed} reported answers contained “{report.success_contains||'no configured signal'}”</small></strong>
          <p>Only checks the configured answer text. It cannot independently certify task correctness, hidden side effects or runner identity.</p>
        </section>
'''
s=s.replace(anchor,status+anchor,1)
anchor='<div className="byoa-findings">{report.results.map(item=><article key={item.case_id} className="byoa-finding">'
assert s.count(anchor)==1
s=s.replace(anchor,'<div className="byoa-findings">{report.results.map(item=><article id={"byoa-case-"+item.case_id} key={item.case_id} className="byoa-finding">',1)
anchor='report.mitigations.map(fix=><div key={fix.case_id}><span>{fix.case_id.toUpperCase()}</span><p>{fix.action}</p><small>{fix.verify_fix}</small></div>)'
assert s.count(anchor)==1
s=s.replace(anchor,'''report.mitigations.map(fix=><div className="byoa-mitigation-detail" key={fix.case_id}>
          <a href={"#byoa-case-"+fix.case_id} className="byoa-mitigation-case-link">VIEW EXACT CASE EVIDENCE: {fix.case_id.toUpperCase()} <ArrowUpRight size={13}/></a>
          <p>{fix.action}</p>
          <small>Observed trigger: {fix.trigger.join('; ')}</small><small>{fix.verify_fix}</small>
          <small>Verify the real tool call in your own execution logs. BlastLab only receives the runner's declaration.</small>
        </div>)''',1)
# case comparison show actual task marker deltas
anchor='   <div className="byoa-compare-delta">'
assert s.count(anchor)==1
delta='''           <div className="byoa-compare-task-signal" aria-label="Literal task signal comparison">
             <strong>TASK SIGNAL — LITERAL ANSWER TEXT</strong>
             <span>{baseline.results.filter(item=>item.task_success_signal==='ANSWER_CONTAINS_REQUIRED_TEXT').length}/{baseline.tests_completed} baseline
             <ArrowRight size={15}/> {report.results.filter(item=>item.task_success_signal==='ANSWER_CONTAINS_REQUIRED_TEXT').length}/{report.tests_completed} retest</span>
             <small>Not a certification of semantic task success or independent agent identity.</small>
           </div>
'''
s=s.replace(anchor,delta+anchor,1)
p.write_text(s,encoding='utf8')
css=root/'web/src/agent-lab.css'
with css.open('a',encoding='utf8') as f:f.write("""
/* Phase 23: explicit test coverage, provenance and evidence-linked remediation */
.byoa-surface-inventory{border:1px solid #385448;background:#131b18;padding:clamp(22px,3.5vw,43px);margin:18px 0 34px}
.byoa-surface-top{display:flex;justify-content:space-between;gap:25px;align-items:flex-start}
.byoa-surface-top h2{font:600 clamp(27px,3vw,40px)/1.08 'Space Grotesk',sans-serif;letter-spacing:-.035em;margin:12px 0}
.byoa-surface-top p{color:#b5c4b8;font-size:13px;max-width:650px;line-height:1.65}
.byoa-surface-count{font:600 10px 'IBM Plex Mono',monospace;color:#e6b88b;border:1px solid #7b5942;padding:10px;white-space:nowrap}
.byoa-surface-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:#324339;border:1px solid #324339;margin-top:22px}
.byoa-surface-item{background:#18231c;padding:18px;min-width:0;display:flex;flex-direction:column;align-items:flex-start;gap:9px}
.byoa-surface-item>span{font:700 9px 'IBM Plex Mono',monospace;letter-spacing:.04em}
.byoa-surface-live{color:#80d4a1}.byoa-surface-planned{color:#e9b28a}
.byoa-surface-item strong{font-size:13px;line-height:1.3}
.byoa-surface-item small{font-size:11px;line-height:1.55;color:#a7b9ad}
.byoa-success-coverage{border:1px solid #4c7056;background:#1b2920;padding:20px;margin:20px 0}
.byoa-success-coverage>span{color:#a4d8b4;font:600 10px 'IBM Plex Mono',monospace;display:block}
.byoa-success-coverage strong{display:flex;align-items:baseline;gap:10px;margin-top:12px;font:600 31px 'Space Grotesk',sans-serif}
.byoa-success-coverage strong small{color:#c2d2c4;font:500 12px/1.6 'IBM Plex Mono',monospace}
.byoa-success-coverage p{font-size:11px;color:#9db1a2;margin:9px 0 0}
.byoa-mitigation-detail{scroll-margin-top:24px}
.byoa-mitigation-case-link{display:inline-flex;align-items:center;gap:7px;color:#e6b997!important;font:600 10px 'IBM Plex Mono',monospace}
.byoa-mitigation-case-link:hover{text-decoration:underline}
.byoa-finding{scroll-margin-top:20px}
.byoa-compare-task-signal{padding:14px 18px;border:1px solid #54715c;display:grid;gap:7px;margin:16px 0}
.byoa-compare-task-signal>strong{color:#bedac3;font:600 10px 'IBM Plex Mono',monospace}
.byoa-compare-task-signal>span{display:flex;gap:9px;align-items:center;font:600 17px 'Space Grotesk',sans-serif}
.byoa-compare-task-signal small{color:#aebeb1;font-size:10px}
@media(max-width:1100px){.byoa-surface-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:690px){.byoa-surface-top{flex-direction:column;gap:12px}.byoa-surface-grid{grid-template-columns:1fr}.byoa-success-coverage strong{flex-direction:column;gap:0}.byoa-surface-count{white-space:normal}}
""")
print('PHASE23_BYOA_PRODUCT_UX_COVERAGE_AND_REMEDIATION_IMPLEMENTED')
