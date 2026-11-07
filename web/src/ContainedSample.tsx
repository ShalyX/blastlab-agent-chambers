import {useEffect,useState} from 'react';
import {ArrowLeft,ArrowRight,ArrowUpRight,CheckCircle2,Download,ShieldAlert,Server,LockKeyhole} from 'lucide-react';
import './contained-sample.css';

type Evidence={
  mode:string;recorded_at:string;agent_name:string;scope:string;provenance:string;limitations:string;
  report_manifest_sha256:string;plan_sha256:string;model:string;inference_provider:string;
  inference_calls:number;tests_completed:number;observed_violations:number;
  worker:{network_mode:string;read_only_rootfs:boolean;user:string;memory_limit_mb:number;
    worker_absent_after_teardown:boolean;proxy_socket_removed:boolean;direct_network_blocked:boolean};
  actions:{synthetic_actions_executed:number;forbidden_actions_denied:number};
  verification:{independent_checks_passed:number;independent_checks_total:number;checks:Record<string,boolean>;scope:string};
  cases:Array<{case_id:string;family:string;verdict:string;observed_answer:string;
    reported_tool_intents:string[];evidence_label:string}>;
};
type LiveSampleJob={
  job_id?:string;status:string;stage?:string;error?:string;available_public_runs_today?:number;
  summary?:{mode:string;cases_completed:number;checks_passed:number;checks_total:number;
    observed_violations:number;inference_calls:number;synthetic_actions_executed:number;
    forbidden_actions_denied:number;worker_absent_after_teardown:boolean;
    inference_socket_removed:boolean;report_manifest_sha256:string;
    origin:string;limitations:string;
    case_results:Array<{case_id:string;family:string;verdict:string}>}
};
const short=(v:string)=>v.slice(0,12)+'…'+v.slice(-8);
export default function ContainedSample(){
  const [data,setData]=useState<Evidence|null>(null);
  const [error,setError]=useState('');
  const [selected,setSelected]=useState('control');
  const [framework,setFramework]=useState<{baseline_violations:number;retest_violations:number;cases_per_run:number;runtime:string;framework_version:string;integration_scope:string;findings:string;}|null>(null);
  useEffect(()=>{
    let active=true;
    fetch('/contained-sample/proof.json',{cache:'no-store'})
      .then(async r=>{if(!r.ok)throw new Error('Archived proof unavailable');return r.json() as Promise<Evidence>})
      .then(v=>{
        if(v.mode!=='ARCHIVED_PROJECT_OWNED_VULTR_CONTAINED_SAMPLE' ||
           v.tests_completed!==6 || v.cases.length!==6 ||
           v.verification.independent_checks_passed!==22 || v.verification.independent_checks_total!==22)
          throw new Error('The evidence summary did not pass its expected contract');
        if(active)setData(v);
      }).catch(e=>{if(active)setError(e instanceof Error?e.message:'Proof unavailable')});
    return ()=>{active=false};
  },[]);
  useEffect(()=>{
    let active=true;
    fetch('/third-party-pydantic/proof.json',{cache:'no-store'})
      .then(async r=>{if(!r.ok)throw new Error('Interop evidence not available');return r.json()})
      .then(result=>{if(active&&result.mode==='ARCHIVED_PUBLIC_HTTPS_THIRD_PARTY_AGENT_FRAMEWORK_TEST'&&result.cases_per_run===6)setFramework(result)})
      .catch(()=>{});
    return ()=>{active=false};
  },[]);
  const [live,setLive]=useState<LiveSampleJob|null>(null);
  const [launching,setLaunching]=useState(false);
  const [launchError,setLaunchError]=useState('');
  useEffect(()=>{
    let alive=true;
    fetch('/api/contained-sample/latest',{cache:'no-store'})
      .then(async r=>{if(!r.ok)throw Error('status unavailable');return r.json() as Promise<LiveSampleJob>})
      .then(v=>{if(alive)setLive(v)}).catch(()=>{});
    return ()=>{alive=false};
  },[]);
  useEffect(()=>{
    if(!live?.job_id||!['queued','running'].includes(live.status))return;
    let active=true;
    const handle=setTimeout(async()=>{
      try{
        const r=await fetch('/api/contained-sample/jobs/'+live.job_id,{cache:'no-store'});
        if(!r.ok)throw Error('Status unavailable');
        const payload=await r.json() as LiveSampleJob;
        if(active)setLive(payload);
      }catch{if(active)setLaunchError('Status connection failed. Refresh to reload the persisted job.')}
    },3000);
    return ()=>{active=false;clearTimeout(handle)};
  },[live]);
  const launch=async()=>{
    if(launching)return;
    setLaunching(true);setLaunchError('');
    try{
      const r=await fetch('/api/contained-sample/jobs',{method:'POST',
        headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'fixed-project-sample'}),
        cache:'no-store'});
      const result=await r.json() as LiveSampleJob & {error?:string};
      if(!r.ok){setLaunchError(result.error||'The fixed run could not start.');return}
      if(!result.job_id)throw Error('No job ID returned');
      setLive(result);
    }catch(e){setLaunchError(e instanceof Error?e.message:'Unable to start sample')}
    finally{setLaunching(false)}
  };
  const checks=data?Object.entries(data.verification.checks):[];
  return <main className="contained-page">
    <header className="contained-nav">
      <a href="/" className="contained-wordmark">BLAST<span>/</span>LAB <small> / EVIDENCE 012</small></a>
      <div><span className="contained-recorded">ARCHIVED + FRESH SAMPLE EVIDENCE</span>
      <a href="/proof">ALL VERIFIED PROOFS <ArrowUpRight size={14}/></a><a href="/app"><ArrowLeft size={14}/> CONNECT YOUR AGENT</a></div>
    </header>
    {!data&&!error&&<p className="contained-loading">LOADING VERIFIED CONTAINMENT RECORD…</p>}
    {error&&<p className="contained-error" role="alert">{error}</p>}
    {data&&<>
      <section className="contained-hero">
        <div className="contained-eyebrow"><i/> VULTR VM / VERIFIED PROJECT-OWNED SAMPLE</div>
        <div className="contained-hero-grid"><div>
          <h1>See the boundary.<br/><em>Not just the verdict.</em></h1>
          <p>An archived November 6 agent run inside a disposable Docker worker on Vultr. We preserved the host-side inference, sandbox action, policy denial and teardown evidence.</p>
          <div className="contained-links"><a href="#cases">INSPECT SIX TEST CASES <ArrowUpRight size={15}/></a>
            <a href="/contained-sample/proof.json" download>DOWNLOAD SUMMARY <Download size={15}/></a></div>
        </div><div className="contained-score"><small>INDEPENDENT EVIDENCE CHECKS</small>
          <div><strong>{data.verification.independent_checks_passed}</strong><span> / {data.verification.independent_checks_total}</span></div>
          <p><CheckCircle2 size={16}/> All 22 recorded checks passed</p>
          <p><CheckCircle2 size={16}/> Worker removed after the run</p>
          <p><CheckCircle2 size={16}/> Inference socket removed</p>
        </div></div>
        <div className="contained-stats">
          <div><strong>{data.tests_completed}</strong><span>CASES COMPLETED</span></div>
          <div><strong>{data.inference_calls}</strong><span>LIVE MODEL REQUESTS</span></div>
          <div><strong>{data.actions.synthetic_actions_executed}</strong><span>SYNTHETIC ACTIONS EXECUTED</span></div>
          <div><strong>{data.actions.forbidden_actions_denied}</strong><span>ACTIONS DENIED</span></div>
        </div>
      </section>
      <section className="contained-section contained-launch" aria-label="Run fresh bounded contained sample">
        <div><span className="contained-eyebrow">ON DEMAND / ACTUAL VULTR EXECUTION</span>
          <h2>Run a fresh, fixed six-case sample.</h2>
          <p>This triggers the approved project-owned agent in a new disposable Vultr worker. No arbitrary code, no customer credentials. Outcomes appear only after host evidence and independent verification finish.</p>
          <button type="button" onClick={launch} disabled={launching||live?.status==='queued'||live?.status==='running'||live?.available_public_runs_today===0}>
            {launching?'REQUESTING RUN':live?.status==='queued'||live?.status==='running'?'SAMPLE RUN IN PROGRESS':live?.available_public_runs_today===0?'TODAY\'S PUBLIC RUN USED':'RUN FIXED VULTR SAMPLE'}
            <ArrowUpRight size={15}/>
          </button>
          <small>One public fixed-compute run per UTC day. The verified historical evidence remains available below.</small>
          {launchError&&<p role="alert" className="contained-launch-error">{launchError}</p>}
        </div>
        <div className="contained-launch-state" role="status" aria-live="polite">
          <span>FRESH WORKER / ACTUAL SERVER STATE</span>
          <strong>{live?.status==='complete'?'VERIFIED':live?.status==='blocked'?'BLOCKED':live?.status==='running'?'RUNNING':live?.status==='queued'?'QUEUED':'NO ACTIVE RUN'}</strong>
          {live?.job_id&&<code>JOB {short(live.job_id)}</code>}
          {live?.status==='complete'&&live.summary&&live.summary.checks_passed===live.summary.checks_total&&<>
            <p><CheckCircle2 size={15}/> {live.summary.checks_passed}/{live.summary.checks_total} independent checks passed</p>
            <div className="contained-live-numbers"><b>{live.summary.cases_completed}<small>cases</small></b>
              <b>{live.summary.observed_violations}<small>observed violations</small></b>
              <b>{live.summary.synthetic_actions_executed}<small>actions executed</small></b>
              <b>{live.summary.forbidden_actions_denied}<small>actions denied</small></b></div>
            <p>Worker removed: {live.summary.worker_absent_after_teardown?'YES':'NO'}. Inference socket removed: {live.summary.inference_socket_removed?'YES':'NO'}.</p>
            <small>HOST-OBSERVED, PROJECT-OWNED. Unsigned runtime evidence; not an independent customer.</small>
            <details className="contained-fresh-details">
              <summary>INSPECT FRESH CASE VERDICTS AND MANIFEST</summary>
              <p>Observed outcomes from this job only. Distinct from the archived sample below.</p>
              <div>{live.summary.case_results.map((item,i)=>
                <div className="contained-fresh-case" key={item.case_id}>
                  <span>{String(i+1).padStart(2,'0')}</span>
                  <strong>{item.family}</strong><small>{item.verdict}</small>
                </div>)}</div>
              <p className="contained-case-manifest">Report manifest: <code>{live.summary.report_manifest_sha256}</code></p>
              {live.job_id&&<a href={'/api/contained-sample/jobs/'+live.job_id} download>DOWNLOAD FRESH VERIFIED SUMMARY <Download size={13}/></a>}
            </details>
          </>}
          {live?.status==='blocked'&&<p>{live.error||'The worker did not pass verification. Archived proof remains available.'}</p>}
          {(live?.status==='queued'||live?.status==='running')&&<p>Vultr inference and the worker are processing actual cases. No outcome is presumed.</p>}
          {!live?.job_id&&<p>No fresh run started in this session. The independently checked archive remains below.</p>}
        </div>
      </section>
      <section className="contained-section">
        <div className="contained-heading"><span>01 / EXECUTION BOUNDARY</span><h2>The model could reason. The worker couldn't roam.</h2></div>
        <div className="contained-boundary">
          <article><Server size={21}/><small>TRUSTED VULTR HOST</small><h3>Inference supervisor</h3><p>Holds the model credential outside the worker, proxying bounded requests over a Unix-domain socket.</p><code>{data.inference_provider} · {data.model}</code></article>
          <div className="contained-connection"><span>HOST PROXY</span><b/></div>
          <article><LockKeyhole size={21}/><small>DISPOSABLE WORKER</small><h3>Networkless execution</h3><p>UID {data.worker.user}, {data.worker.memory_limit_mb} MB, read-only root filesystem, blocked internet and a removed container.</p><code>DOCKER / NETWORK {data.worker.network_mode.toUpperCase()}</code></article>
        </div>
        <p className="contained-caveat"><ShieldAlert size={17}/> This is a project-owned sample. Customer agents connect outbound from their own environment and are <strong>not</strong> contained by BlastLab's sample worker.</p>
      </section>
      <section id="cases" className="contained-section">
        <div className="contained-heading"><span>02 / SIX OBSERVED CASES</span><h2>Open the actual response.</h2>
        <p>Agent response and tool intentions are runner-reported. Separately, the host verified which harmless actions executed and which forbidden requests were denied.</p></div>
        <div className="contained-cases">{data.cases.map((item,i)=><article key={item.case_id}>
          <button type="button" aria-expanded={selected===item.case_id} onClick={()=>setSelected(selected===item.case_id?'':item.case_id)}>
            <span>{String(i+1).padStart(2,'0')}</span><b>{item.family}</b><small>{item.verdict==='BASELINE_OBSERVED'?'CONTROL':'NO VIOLATION OBSERVED'}</small></button>
          {selected===item.case_id&&<div className="contained-case-body">
            <span>REAL AGENT RESPONSE / RUNNER-REPORTED</span><p>{item.observed_answer}</p>
            <span>REPORTED TOOL INTENTS</span><div>{item.reported_tool_intents.length?item.reported_tool_intents.map((n,j)=><code key={n+j}>{n}</code>):<em>None observed</em>}</div>
          </div>}
        </article>)}</div>
      </section>
      <section className="contained-section">
        <div className="contained-heading"><span>03 / INDEPENDENT VERIFICATION</span><h2>{data.verification.independent_checks_passed} checks. Nothing hidden.</h2></div>
        <div className="contained-check-grid">{checks.map(([id,pass])=><div key={id}><CheckCircle2 size={14}/><span>{id.replace(/_/g,' ')}</span><small>{pass?'PASS':'FAIL'}</small></div>)}</div>
      </section>
      {framework&&<section className="contained-section contained-interop" aria-label="Third-party agent framework interoperability">
        <div><span className="contained-eyebrow">04 / THIRD-PARTY FRAMEWORK / DIFFERENT TEST</span>
          <h2>A real external agent runtime.<br/>Not a customer testimonial.</h2>
          <p>We connected the PydanticAI Agent framework to BlastLab over public HTTPS using Vultr GLM-5.3. This verifies the connector works beyond our native agent implementation; the wrapper and test account are still project-owned.</p>
          <a href="/third-party-pydantic/proof.json" target="_blank" rel="noreferrer">INSPECT FRAMEWORK EVIDENCE <ArrowUpRight size={15}/></a>
        </div>
        <div className="contained-interop-result"><span>EXACT SIX-CASE RETEST / SAME PLAN</span>
          <strong>{framework.baseline_violations}<i><ArrowRight size={32}/></i>{framework.retest_violations}</strong>
          <small>CONFIGURED VIOLATIONS OBSERVED ? {framework.cases_per_run} CASES EACH</small>
          <p>{framework.findings}</p><p>PYDANTICAI {framework.framework_version} ? RUNNER-REPORTED</p>
        </div>
      </section>}
      <section className="contained-section contained-last">
        <div><span className="contained-eyebrow">05 / PROVENANCE</span><h2>The scope matters.</h2>
          <p>{data.limitations}</p>
          <p>The run used a previously accepted Vultr-generated attack plan, replayed with a rotated synthetic canary. This historical case file is archived; the separate on-demand section above shows a newly executed run when independently verified.</p>
          <a href="/app">CONNECT YOUR OWN AGENT <ArrowUpRight size={15}/></a>
        </div><dl>
          <dt>RECORDED</dt><dd>{new Date(data.recorded_at).toISOString().slice(0,16).replace('T',' ')} UTC</dd>
          <dt>REPORT MANIFEST</dt><dd><code title={data.report_manifest_sha256}>{short(data.report_manifest_sha256)}</code></dd>
          <dt>ATTACK PLAN</dt><dd><code title={data.plan_sha256}>{short(data.plan_sha256)}</code></dd>
          <dt>PROOF TYPE</dt><dd>HOST-OBSERVED / UNSIGNED</dd>
        </dl>
      </section>
    </>}
  </main>;
}
