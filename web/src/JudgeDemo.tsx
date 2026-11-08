import { useEffect, useMemo, useState } from 'react';
import { ArrowRight, ArrowUpRight, CheckCircle2, CircleAlert, Download, Fingerprint, ShieldCheck } from 'lucide-react';
import './judge-demo.css';

type Finding = {
  case_id: string;
  family: string;
  verdict: string;
  reasons: string[];
  observations?: string[];
};
type Mitigation = {
  case_id: string;
  trigger: string[];
  action: string;
  verify_fix: string;
};
type JudgeReport = {
  session_id: string;
  agent_name: string;
  task: string;
  source_type: string;
  status: string;
  forbidden_tools: string[];
  canary: string;
  retest_of?: string;
  tests_completed: number;
  tests_total: number;
  breached: number;
  no_observed_violation: number;
  results: Finding[];
  mitigations: Mitigation[];
  attack_plan_source: string;
  attack_plan_provider: string;
  attack_plan_model: string;
  attack_plan_sha256: string;
  limits: string;
  manifest_sha256: string;
};
type Compared = { before: Finding; after: Finding };

const statusLabel = (verdict: string) => {
  if (verdict === 'BREACHED') return 'BREACH OBSERVED';
  if (verdict === 'BASELINE_OBSERVED') return 'CONTROL';
  return 'NO VIOLATION OBSERVED';
};
const statusTone = (verdict: string) => verdict === 'BREACHED' ? 'breach' : verdict === 'BASELINE_OBSERVED' ? 'control' : 'clean';

export default function JudgeDemo() {
  const [baseline, setBaseline] = useState<JudgeReport | null>(null);
  const [hardened, setHardened] = useState<JudgeReport | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let alive = true;
    Promise.all([
      fetch('/judge-demo/vulnerable-report.json', { cache: 'no-store' }),
      fetch('/judge-demo/hardened-report.json', { cache: 'no-store' }),
    ]).then(async ([beforeResponse, afterResponse]) => {
      if (!beforeResponse.ok || !afterResponse.ok) throw new Error('The recorded proof files could not be loaded.');
      const [before, after] = await Promise.all([beforeResponse.json(), afterResponse.json()]);
      if (alive) { setBaseline(before as JudgeReport); setHardened(after as JudgeReport); }
    }).catch((reason: unknown) => {
      if (alive) setError(reason instanceof Error ? reason.message : 'Unable to load the recorded proof.');
    });
    return () => { alive = false; };
  }, []);

  const compared = useMemo<Compared[]>(() => {
    if (!baseline || !hardened) return [];
    return baseline.results.flatMap(before => {
      const after = hardened.results.find(item => item.case_id === before.case_id);
      return after ? [{ before, after }] : [];
    });
  }, [baseline, hardened]);

  const exactReplay = !!baseline && !!hardened
    && baseline.attack_plan_sha256 === hardened.attack_plan_sha256
    && baseline.canary === hardened.canary
    && baseline.task === hardened.task
    && baseline.forbidden_tools.length === hardened.forbidden_tools.length
    && baseline.forbidden_tools.every((tool, index) => tool === hardened.forbidden_tools[index])
    && baseline.tests_completed === hardened.tests_completed
    && baseline.tests_total === hardened.tests_total
    && baseline.tests_completed === baseline.tests_total
    && hardened.tests_completed === hardened.tests_total
    && baseline.results.length === hardened.results.length
    && baseline.results.every((item, index) => hardened.results[index]?.case_id === item.case_id)
    && baseline.agent_name === hardened.agent_name
    && baseline.source_type === hardened.source_type
    && baseline.status === 'complete' && hardened.status === 'complete'
    && hardened.retest_of === baseline.manifest_sha256
    && compared.length === baseline.results.length;
  const resolved = compared.filter(({ before, after }) => before.verdict === 'BREACHED' && after.verdict !== 'BREACHED').length;
  const regressions = compared.filter(({ before, after }) => before.verdict !== 'BREACHED' && after.verdict === 'BREACHED').length;

  return <main className="judge-demo">
    <header className="judge-nav">
      <a className="judge-wordmark" href="/" aria-label="BlastLab home">BLASTLAB<span> / AGENT SECURITY</span></a>
      <div className="judge-nav-right"><span className="judge-live-dot"/> RECORDED LIVE PROOF · 06 NOV 2026 <a href="/contained-sample">VULTR CONTAINED SAMPLE <ArrowUpRight size={14}/></a> <a href="/app">CONNECT AN AGENT <ArrowUpRight size={14}/></a></div>
    </header>

    <section className="judge-hero">
      <div className="judge-hero-copy">
        <div className="judge-eyebrow"><span>01</span> THE BEFORE / AFTER TEST</div>
        <h1>Same attack plan.<br/><em>A different outcome.</em></h1>
        <p>We replayed the same model-generated six-case plan against the same agent task before and after hardening. The vulnerable baseline exposed two findings. Neither appeared in the hardened retest.</p>
        <div className="judge-hero-meta"><span><ShieldCheck size={15}/> SIX MATCHED CASES</span><span><Fingerprint size={15}/> SAME PLAN FINGERPRINT</span><span>VULTR · GLM-5.3</span></div>
      </div>
      <div className="judge-scoreboard" aria-label="Vulnerable versus hardened result">
        <div className="judge-score-side judge-score-before"><div className="judge-score-label"><i/> VULNERABLE BASELINE</div><div className="judge-score-number">{baseline?.breached ?? '—'}</div><div className="judge-score-caption">OBSERVED BREACHES</div><div className="judge-score-foot">RUN 01 / BEFORE HARDENING</div></div>
        <div className="judge-score-divider"><ArrowRight size={22}/><span>RETEST</span></div>
        <div className="judge-score-side judge-score-after"><div className="judge-score-label"><i/> HARDENED RETEST</div><div className="judge-score-number">{hardened?.breached ?? '—'}</div><div className="judge-score-caption">OBSERVED BREACHES</div><div className="judge-score-foot">RUN 02 / SAME SIX-CASE PLAN</div></div>
        <div className="judge-score-bottom"><strong>{resolved}</strong><span>baseline findings not observed on retest</span><b>{regressions} regressions</b></div>
      </div>
    </section>

    {error && <div className="judge-error" role="alert"><CircleAlert size={18}/>{error}</div>}
    {!baseline || !hardened ? <div className="judge-loading">LOADING RECORDED REPORTS…</div> : <>
      <section className="judge-contract">
        <div className="judge-section-heading"><div><span>02 / TEST CONTRACT</span><h2>The test contract stayed the same across both runs.</h2></div><div className={'judge-contract-status '+(exactReplay ? 'verified' : 'mismatch')}>{exactReplay ? <CheckCircle2 size={16}/> : <CircleAlert size={16}/>} {exactReplay ? 'MATCHED REPLAY CONTRACT' : 'CONTRACT MISMATCH'}</div></div>
        <div className="judge-contract-grid">
          <div><small>ATTACK PLAN</small><strong>{baseline.attack_plan_provider} / {baseline.attack_plan_model}</strong><code>{baseline.attack_plan_sha256}</code></div>
          <div><small>TEST TASK</small><strong>{baseline.task}</strong></div>
          <div><small>FORBIDDEN CAPABILITIES</small><strong>{baseline.forbidden_tools.join(' · ')}</strong></div>
          <div><small>REPLAY LINEAGE</small><strong>{hardened.retest_of === baseline.manifest_sha256 ? 'Hardened run references baseline manifest' : 'Baseline lineage not matched'}</strong><code>BASELINE {baseline.manifest_sha256.slice(0, 20)}…</code></div>
        </div>
      </section>

      <section className="judge-cases">
        <div className="judge-section-heading"><div><span>03 / CASE-BY-CASE RESULTS</span><h2>Watch the two failures disappear.</h2></div><p>{compared.length} matched cases · {baseline.tests_completed}/{baseline.tests_total} completed in each run</p></div>
        <div className="judge-case-table">
          <div className="judge-case-head"><span>ATTACK FAMILY</span><span>VULNERABLE</span><span>HARDENED</span></div>
          {compared.map(({ before, after }) => <article className={'judge-case-row '+(before.verdict === 'BREACHED' ? 'judge-case-hit' : '')} key={before.case_id}>
            <div className="judge-case-name"><strong>{before.family}</strong><small>{before.case_id}</small></div>
            <div><span className={'judge-verdict '+statusTone(before.verdict)}>{statusLabel(before.verdict)}</span></div>
            <div><span className={'judge-verdict '+statusTone(after.verdict)}>{statusLabel(after.verdict)}</span></div>
            {before.verdict === 'BREACHED' && <div className="judge-case-detail"><strong>BASELINE OBSERVATION</strong><p>{before.reasons.join('; ')}</p></div>}
          </article>)}
        </div>
      </section>

      <section className="judge-findings">
        <div className="judge-section-heading"><div><span>04 / WHAT THE BASELINE EXPOSED</span><h2>Two concrete failure modes.</h2></div><p>Recommendations below come from the baseline report. They are not represented as independently audited code changes.</p></div>
        <div className="judge-finding-grid">
          {baseline.mitigations.filter(fix => baseline.results.some(result => result.case_id === fix.case_id && result.verdict === 'BREACHED')).map(fix => {
            const item = baseline.results.find(result => result.case_id === fix.case_id);
            return <article className="judge-finding" key={fix.case_id}>
              <div className="judge-finding-top"><span>BASELINE FINDING</span><span className="judge-finding-status">NOT OBSERVED ON RETEST</span></div>
              <h3>{item?.family || fix.case_id}</h3>
              <p>{fix.trigger.join('; ')}</p>
              <div><small>RECOMMENDED GUARDRAIL</small><strong>{fix.action}</strong></div>
            </article>;
          })}
        </div>
      </section>

      <section className="judge-proof">
        <div><span>05 / EVIDENCE & LIMITS</span><h2>Show the receipts. Keep the claims honest.</h2><p>{baseline.limits}</p><p>BlastLab verifies report consistency and the matching replay contract. These are independently connected runner-reported responses, not source-attested agent executions. The six-case result is not a general security certification, and no tool action was executed by BlastLab.</p></div>
        <div className="judge-proof-actions">
          <a href="/judge-demo/vulnerable-report.json" download="blastlab-vulnerable-baseline.json"><Download size={16}/> BASELINE JSON</a>
          <a href="/judge-demo/hardened-report.json" download="blastlab-hardened-retest.json"><Download size={16}/> HARDENED JSON</a>
          <a href="/app">RUN YOUR OWN AGENT <ArrowUpRight size={15}/></a>
        </div>
      </section>
    </>}

    <footer className="judge-footer"><a className="judge-wordmark" href="/">BLASTLAB<span> / AGENT SECURITY</span></a><span>CONTROLLED COMPARISON · NOT A UNIVERSAL SECURITY CLAIM</span><a href="/app">TEST YOUR AGENT <ArrowUpRight size={14}/></a></footer>
  </main>;
}
