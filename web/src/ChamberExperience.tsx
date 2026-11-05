import {useEffect, useMemo, useState} from 'react';
import {
  ArrowDownRight, ArrowRight, ArrowUpRight, Box, Check, CheckCircle2, ChevronRight,
  CircleAlert, Code2, Copy, Download, ExternalLink, Fingerprint, FlaskConical, Gauge,
  Globe2, Layers3, Lock, LockKeyhole, Play, Radio, RefreshCcw, ScanEye,
  Server, Shield, ShieldAlert, ShieldCheck, ShieldX, Sparkles, TerminalSquare,
  Timer, TriangleAlert, Unplug, WandSparkles, X
} from 'lucide-react';
import type {Mode, RunData} from './types';

type Chamber = {id:string,number:string,name:string,state:string,description:string,surfaces:string[]};
type Mission = {id:string,name:string,short:string,description:string,instruction:string,metric:string,difficulty:string};
type Scenario = {id:string,name:string,family:string,description:string,attempts:string[]};
type Catalog = {
  version:string,chambers:Chamber[],missions:Mission[],scenarios:Scenario[],
  engines:{id:string,name:string,public:boolean,note:string}[],
  limits:{public:string,owner:string}
};
type Entry = {id:string,origin:string,is_scripted:boolean,mission_id:string,scenario:string,timestamp:string,provider:string,completed:boolean,value_cents:number,policy_denials:number,public_digest:string};

function useCatalog(){
  const [catalog,setCatalog]=useState<Catalog|null>(null);
  const [error,setError]=useState('');
  useEffect(()=>{let live=true;(async()=>{
    try{
      let response=await fetch('/api/catalog');
      if(!response.ok) response=await fetch('/data/catalog.json');
      if(!response.ok) throw new Error('Chamber catalogue is unavailable');
      const next=await response.json() as Catalog;
      if(live)setCatalog(next);
    }catch(e){if(live)setError(e instanceof Error?e.message:'Catalogue unavailable')}
  })();return()=>{live=false};},[]);
  return {catalog,error};
}
const date=(value?:string)=>{try{return value?new Date(value).toLocaleString('en-GB',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',timeZone:'UTC'})+' UTC':'—'}catch{return '—'}};
const money=(n?:number)=>'$'+((n||0)/100).toFixed(2);
const icons={
  web:<Globe2 size={30}/>,toolchain:<Code2 size={28}/>,vault:<LockKeyhole size={28}/>,
  machine:<Server size={28}/>,chaos:<Gauge size={28}/>
};
const icon=(id:string)=>(icons as Record<string,React.ReactNode>)[id] || <Box size={28}/>;

function SectionOverline({children}:{children:React.ReactNode}){
  return <span className="ch-eyebrow"><span className="ch-amber-point"/> {children}</span>;
}
function MiniTag({children,live=false}:{children:React.ReactNode,live?:boolean}){
  return <span className={'ch-tag '+(live?'ch-tag-live':'')}>{children}</span>;
}
function useHistory(){
  const [items,setItems]=useState<Entry[]>([]);
  const [refresh,setRefresh]=useState(0);
  useEffect(()=>{let active=true;fetch('/api/history',{cache:'no-store'}).then(x=>x.ok?x.json():Promise.reject())
    .then(data=>{if(active)setItems(Array.isArray(data.runs)?data.runs:[])})
    .catch(()=>{if(active)setItems([])});
    return()=>{active=false};
  },[refresh]);
  return {items,refresh:()=>setRefresh(x=>x+1)};
}
export function ChamberLibrary({onEnter,onViewRun}:{onEnter:()=>void,onViewRun:(id:string,mode:Mode)=>void}){
  const {catalog,error}=useCatalog();
  const {items}=useHistory();
  const chambers=catalog?.chambers||[];
  return <main className="ch-page">
    <div className="ch-page-top"><SectionOverline>INTERNAL DEMO / CHAMBER LIBRARY</SectionOverline><MiniTag live>01 CHAMBER ONLINE</MiniTag></div>
    <div className="ch-library-head"><div><h1>Choose the<br/><em>attack surface.</em></h1><p>One agent. A legitimate task. A hostile environment. Every action accountable. Enter the Web Chamber to launch a real containment test.</p></div><div className="ch-lab-counter"><span>TEST FACILITY</span><strong>01<span>/05</span></strong><small>Chambers ready for execution</small></div></div>
    {error&&<div className="ch-inline-alert">{error}. The Chamber service may be temporarily unavailable.</div>}
    <div className="ch-active-chamber">
      <div className="ch-active-no"><span>01 / LIVE SUPPLIER DEMO</span><span className="ch-live-dot">READY FOR TESTING</span></div>
      <div className="ch-active-layout"><div className="ch-active-title"><Globe2 size={42} strokeWidth={1.5}/><h2>THE<br/>WEB<span>.</span></h2><p>Drop the agent into a malicious supplier page. Watch the model or scripted fixture propose tools, see the policy boundary respond, kill the browser and inspect the recovered result.</p><button className="ch-primary" onClick={onEnter}>ENTER WEB CHAMBER <ArrowUpRight size={19}/></button></div>
      <div className="ch-active-illustration" aria-label="Web chamber schematic showing hostile page contained by policy and Docker">
        <div className="ch-blueprint-grid"/>
        <div className="ch-blueprint-meta">LIVE CHAMBER / 01 — BROWSER</div>
        <div className="ch-doc-visual"><div><span>SUPPLIER / UNTRUSTED</span><Globe2 size={14}/></div><i/><i className="short"/><div className="ch-doc-threat"><ShieldAlert size={15}/> SYSTEM OVERRIDE</div></div>
        <div className="ch-guard-cross"><span>UNTRUSTED INSTRUCTION</span><i/><ShieldX size={24}/><b>DENY BY POLICY</b></div>
        <div className="ch-docker-visual"><Box size={27}/><div><b>DOCKER / CHROMIUM</b><small>ISOLATE · DESTROY · RESUME</small></div><span>02 GEN</span></div>
        <div className="ch-blueprint-foot">VULTR VM · GLM-5.3 · EVIDENCE CHAIN</div>
      </div></div>
      <div className="ch-active-bottom"><span>2 MISSION TEMPLATES</span><span>4 ATTACKS + BASELINE</span><span>REAL DOCKER RUNS</span><span><CheckCircle2 size={14}/> VERIFIED RESET</span></div>
    </div>
    <div className="ch-under-head"><div><span className="ch-subcap">IN THE FACILITY</span><h2>Other test surfaces.</h2></div><p>These are product directions, not deployed features. They cannot be launched until their own containment mechanisms are proven.</p></div>
    <div className="ch-planned-grid">
      {chambers.filter(x=>x.id!=='web').map(c=><article className="ch-planned-card" key={c.id}><div className="ch-planned-top"><span>{c.number} / MODULE</span><Lock size={14}/></div><div className="ch-planned-icon">{icon(c.id)}</div><h3>{c.name}</h3><p>{c.description}</p><div className="ch-planned-foot"><span>NOT IMPLEMENTED</span><span>PLANNED</span></div></article>)}
    </div>
    <div className="ch-history-head"><div><span className="ch-subcap">ACTUAL EXECUTION RECORDS</span><h2>Recent field tests.</h2></div><span>{items.length} ARCHIVED RUNS</span></div>
    {items.length?<div className="ch-history-list">{items.slice(0,5).map(e=><button key={e.id} className="ch-history-item" onClick={()=>onViewRun(e.id,e.is_scripted?'scripted':'live')}><span className="ch-history-symbol">{e.is_scripted?<TerminalSquare size={19}/>:<Radio size={19}/>}</span><span><b>{e.scenario.replaceAll('_',' ')} · {e.mission_id.replaceAll('_',' ')}</b><small>{e.is_scripted?'SCRIPTED FIXTURE':'LIVE VULTR MODEL'} · {date(e.timestamp)}</small></span><strong>{money(e.value_cents)}</strong><ArrowUpRight size={18}/></button>)}</div>:<div className="ch-history-empty">No indexed runs yet. The two original verified recordings are still accessible in the Control Room.</div>}
  </main>;
}

export function WebChamberSetup({onComplete,onViewRun}:{onComplete:(id:string,mode:Mode)=>void,onViewRun:(id:string,mode:Mode)=>void}){
  const {catalog,error}=useCatalog();
  const {items,refresh}=useHistory();
  const [mission,setMission]=useState('inventory_value');
  const [scenario,setScenario]=useState('role_spoof');
  const [engine,setEngine]=useState<Mode>('scripted');
  const [token,setToken]=useState('');
  const [job,setJob]=useState('');
  const [status,setStatus]=useState('');
  const [message,setMessage]=useState('');
  const [busy,setBusy]=useState(false);
  const missions=catalog?.missions||[];
  const scenarios=catalog?.scenarios||[];
  const selectedMission=missions.find(x=>x.id===mission);
  const selectedScenario=scenarios.find(x=>x.id===scenario);
  useEffect(()=>{
    if(!job||!busy)return;
    let stopped=false;
    const poll=async()=>{
      try{
        const path=(engine==='scripted'?'/api/demo-jobs/':'/api/jobs/')+job;
        const response=await fetch(path,{
          cache:'no-store',
          headers:engine==='live'?{'Authorization':'Bearer '+token}:{}
        });
        const data=await response.json();
        if(!response.ok)throw new Error(data.error||'Job status is unavailable.');
        if(stopped)return;
        setStatus(data.status);
        if(data.status==='complete'&&data.run_id){
          setBusy(false);setToken('');refresh();
          onComplete(data.run_id,engine);
        }else if(data.status==='failed'){
          setBusy(false);setMessage('Test failed: '+(data.error||'read server diagnostics'));
        }
      }catch(e){if(!stopped){setBusy(false);setMessage(e instanceof Error?e.message:'Job polling failed')}}
    };
    const timer=window.setInterval(poll,1700);poll();
    return()=>{stopped=true;window.clearInterval(timer)};
  },[job,busy,engine,token,onComplete]);
  const launch=async()=>{
    if(busy)return;
    setMessage('');setJob('');setStatus('preparing');
    if(!catalog){setMessage('The scenario catalogue has not loaded.');return}
    if(engine==='live'&&!token.trim()){setMessage('Owner access is required for real Vultr model inference. Select Scripted to run a public Docker test.');return}
    setBusy(true);
    try{
      const path=engine==='scripted'?'/api/demo-runs':'/api/runs';
      const body=engine==='scripted'?{mission,scenario}:{mode:'live',mission,scenario};
      const response=await fetch(path,{
        method:'POST',
        headers:{'Content-Type':'application/json',...(engine==='live'?{'Authorization':'Bearer '+token.trim()}:{})},
        body:JSON.stringify(body)
      });
      const data=await response.json();
      if(!response.ok)throw new Error(data.error||'Could not start the selected test');
      setJob(data.job_id);setStatus('queued');
    }catch(e){setBusy(false);setStatus('failed');setMessage(e instanceof Error?e.message:'Unable to launch test')}
  };
  return <main className="ch-page ch-setup-page">
    <div className="ch-page-top"><SectionOverline>DEMO / CHAMBER 01 CONFIGURATION</SectionOverline><MiniTag live>REAL DOCKER EXECUTION</MiniTag></div>
    <div className="ch-setup-heading"><div><span className="ch-step-marker">01 — THE WEB</span><h1>Configure the<br/><em>test conditions.</em></h1><p>Pick the authorized work, choose what the hostile page will attempt, then launch inside a disposable browser on Vultr.</p></div><div className="ch-workflow-stages"><span className="is-active">01 CONFIGURE</span><span>02 EXECUTE</span><span>03 INSPECT</span><span>04 REPORT</span></div></div>
    {error&&<div className="ch-inline-alert">{error}</div>}
    <section className="ch-config-section">
      <div className="ch-config-label"><span>01 / LEGITIMATE TASK</span><h2>What must the agent accomplish?</h2><p>Both missions use real supplier inventory. The final answer must match independently observed browser rows.</p></div>
      <div className="ch-mission-grid">{missions.map(m=><button type="button" aria-pressed={mission===m.id} key={m.id} disabled={busy} className={'ch-option-card '+(mission===m.id?'chosen':'')} onClick={()=>setMission(m.id)}>
        <div className="ch-option-top"><span>{m.id==='inventory_value'?'VALUATION':'EXPOSURE'}</span><span className="ch-selector-circle">{mission===m.id?<Check size={13}/>:null}</span></div>
        <h3>{m.name}</h3><p>{m.description}</p><small>{m.difficulty} / PROVEN CALCULATION</small>
      </button>)}</div>
    </section>
    <section className="ch-config-section">
      <div className="ch-config-label"><span>02 / HOSTILE ENVIRONMENT</span><h2>Choose the page attack.</h2><p>Each scenario serves different malicious text from the fixed supplier route. The selected test changes the attack presented to the browser.</p></div>
      <div className="ch-scenario-grid">{scenarios.map((s,i)=><button type="button" disabled={busy} aria-pressed={scenario===s.id} key={s.id} className={'ch-scenario-card '+(scenario===s.id?'selected':'')} onClick={()=>setScenario(s.id)}>
        <span className="ch-scenario-head"><span>{('0'+(i+1)).slice(-2)} / {s.family.toUpperCase()}</span><span className="ch-selector-circle">{scenario===s.id?<Check size={12}/>:null}</span></span>
        <strong>{s.name}</strong><small>{s.description}</small>
        <span className="ch-action-type">{s.attempts.length?s.attempts.map(x=>x.toUpperCase()).join(' · '):'NO ATTACK — BASELINE'}</span>
      </button>)}</div>
    </section>
    <section className="ch-config-section ch-engine-section">
      <div className="ch-config-label"><span>03 / EXECUTION SOURCE</span><h2>Choose your challenger.</h2><p>Both engines use a real Docker-isolated browser. Only the owner can spend Vultr inference credits; the public fixture is bounded and rate limited.</p></div>
      <div className="ch-engine-group">
        <button type="button" className={'ch-engine-card '+(engine==='scripted'?'active':'')} onClick={()=>{setEngine('scripted');setMessage('')}} disabled={busy}><TerminalSquare size={24}/><div><strong>Scripted attack fixture</strong><p>Actually submits the scenario's forbidden tool calls to the real policy gate. Public, rate limited.</p></div><span className="ch-selector-circle">{engine==='scripted'?<Check size={13}/>:null}</span></button>
        <button type="button" className={'ch-engine-card '+(engine==='live'?'active':'')} onClick={()=>{setEngine('live');setMessage('')}} disabled={busy}><Radio size={24}/><div><strong>Live Vultr GLM-5.3</strong><p>A genuine LLM decides what tools to propose. It may ignore the injection—zero denials can be a correct outcome.</p></div><span className="ch-selector-circle">{engine==='live'?<Check size={13}/>:null}</span></button>
        {engine==='live'&&<div className="ch-owner-field"><LockKeyhole size={17}/><label htmlFor="web-owner-key">OPERATOR ACCESS</label><input id="web-owner-key" type="password" autoComplete="off" placeholder="Owner token — never sent to the worker" value={token} disabled={busy} onChange={e=>setToken(e.target.value)}/></div>}
      </div>
    </section>
    <div className="ch-launch-dock"><div><span>YOUR TEST CHAMBER</span><h3>{selectedMission?.name||mission} <span>/</span> {selectedScenario?.name||scenario}</h3><p>{engine==='scripted'?'Scripted fixture · real Docker on Vultr':'Live GLM-5.3 · Vultr Serverless Inference'} · fixed local supplier route</p></div>
      <button type="button" onClick={launch} disabled={busy||!catalog} className="ch-primary ch-launch-btn">{busy?<><RefreshCcw size={17} className="spinner"/> {status.toUpperCase()} ON VULTR…</>:<>LAUNCH CONTAINED TEST <ArrowUpRight size={19}/></>}</button></div>
    {message&&<div className="ch-inline-alert" role="status"><CircleAlert size={17}/>{message}</div>}
    {busy&&<div className="ch-executing" role="status"><div className="ch-loading-line"/><span><Box size={18}/> Real Chromium container job {job.slice(0,8)||'initializing'} · {status.toUpperCase()}</span><p>This is a real sandbox test. No fake progress or manufactured tool results are shown.</p></div>}
    <div className="ch-proof-note"><ShieldCheck size={20}/><span>BOUNDARY RULES</span> No outbound network, no host mounts, read-only root, dropped capabilities, bounded memory/time and supervisor-owned reset. The configured payload is inert page text; any fixture action must pass the independent allowlist.</div>
    {items.length>0&&<section className="ch-setup-history"><div className="ch-history-head"><div><span className="ch-subcap">PREVIOUSLY EXECUTED</span><h2>Recent runs</h2></div><span>{items.length} ARCHIVED</span></div><div className="ch-history-list">{items.slice(0,4).map(i=><button className="ch-history-item" onClick={()=>onViewRun(i.id,i.is_scripted?'scripted':'live')} key={i.id}><span className="ch-history-symbol"><Fingerprint size={18}/></span><span><b>{i.mission_id.replaceAll('_',' ')} / {i.scenario.replaceAll('_',' ')}</b><small>{i.is_scripted?'SCRIPTED':'LIVE MODEL'} · {date(i.timestamp)}</small></span><strong>{money(i.value_cents)}</strong><ArrowUpRight size={18}/></button>)}</div></section>}
  </main>;
}

function exportRun(run:RunData){
  const blob=new Blob([JSON.stringify(run,null,2)],{type:'application/json'});
  const url=URL.createObjectURL(blob);
  const link=document.createElement('a');
  link.href=url;link.download='blastlab-'+run.id+'.json';link.click();
  setTimeout(()=>URL.revokeObjectURL(url),900);
}
export function RunResults({run,loading,error,onControl,onNew,onViewRun}:{run:RunData|null,loading:boolean,error:string,onControl:()=>void,onNew:()=>void,onViewRun:(id:string,mode:Mode)=>void}){
  const {items}=useHistory();
  const [comparison,setComparison]=useState('');
  const [compareRun,setCompareRun]=useState<RunData|null>(null);
  const [copied,setCopied]=useState(false);
  useEffect(()=>{
    if(!comparison){setCompareRun(null);return}
    let active=true;fetch('/api/history/'+encodeURIComponent(comparison)).then(r=>r.ok?r.json():Promise.reject()).then(r=>{if(active)setCompareRun(r)}).catch(()=>{if(active)setCompareRun(null)});
    return()=>{active=false};
  },[comparison]);
  if(loading)return <main className="ch-page"><div className="ch-loading-pane"><RefreshCcw className="spinner"/><p>Loading the verified case report…</p></div></main>;
  if(!run)return <main className="ch-page"><div className="ch-empty-results"><CircleAlert size={29}/><h1>No report selected.</h1><p>{error||'Enter a Chamber and run a test, or open a recorded case from history.'}</p><button onClick={onNew} className="ch-primary">OPEN WEB CHAMBER <ArrowRight size={18}/></button></div></main>;
  const report=run.report;
  const good=!!run.summary.acceptance_passed;
  const other=items.filter(x=>x.id!==run.id);
  return <main className="ch-page ch-results-page">
    <div className="ch-page-top"><SectionOverline>SUPPLIER DEMO / TEST REPORT</SectionOverline><MiniTag live={good}>{good?'ACCEPTANCE VERIFIED':'INCOMPLETE / INVESTIGATE'}</MiniTag></div>
    <div className="ch-result-hero"><div><span className="ch-step-marker">CASE {run.id.toUpperCase()}</span><h1>{good?'The boundary held.':'Evidence not complete.'}<br/><em>{good?'The mission survived.':'Review the failure.'}</em></h1><p>{report?.scope||'Controlled supplier-page test; not a general security certification.'}</p><div className="ch-result-actions"><button className="ch-primary" onClick={onControl}>INSPECT FULL EXECUTION <ArrowUpRight size={18}/></button><button className="ch-outline" onClick={()=>exportRun(run)}><Download size={16}/> EXPORT VERIFIABLE JSON</button><button className="ch-outline" onClick={onNew}>NEW TEST</button></div></div>
      <div className="ch-result-meter"><span>INDEPENDENT TASK VERIFICATION</span><strong>{money(run.summary.value_cents)}</strong><span>{run.mission_id?.replaceAll('_',' ').toUpperCase()}</span><div className="ch-meter-ticks"><i/><i/><i/><i/><i/><i/><i/><i/><i/></div><b><CheckCircle2 size={15}/> {run.summary.reset_verified?'WORKER RESET VERIFIED':'RESET NOT VERIFIED'}</b></div></div>
    <div className="ch-result-grid"><div><span>RUN PROVENANCE</span><strong>{run.is_scripted?'SCRIPTED ATTACK FIXTURE':'GENUINE VULTR MODEL'}</strong><small>{run.is_scripted?'Not LLM-generated malicious actions':'GLM-5.3 proposed actual tool calls'}</small></div><div><span>DENIED TOOL PROPOSALS</span><strong>{run.summary.denied_actions.toString().padStart(2,'0')}</strong><small>{run.is_scripted?'Deliberately submitted fixture proposals':'Real model decisions only'}</small></div><div><span>DISPOSABLE WORKERS</span><strong>{run.summary.worker_generations.toString().padStart(2,'0')}</strong><small>Generation reset verified</small></div><div><span>CHAINED EVENTS</span><strong>{run.summary.event_count.toString().padStart(2,'0')}</strong><small>Public chain exportable</small></div></div>
    <div className="ch-report-layout"><section className="ch-report-panel">
      <div className="ch-report-head"><SectionOverline>01 / BLAST RADIUS</SectionOverline><h2>What actually happened.</h2></div>
      <div className="ch-report-verdict"><span className="ch-report-status-icon"><ShieldCheck size={25}/></span><div><span>OBSERVED OUTCOME</span><h3>{report?.verdict||'Run completed'}</h3><p>{report?.observed_containment||'The allowed tool contract was verified in this constrained test.'}</p></div></div>
      <div className="ch-report-lines">
        <div><span><ScanEye size={16}/> HOSTILE PAGE EXPOSED</span><strong>{report?.threat_exposure_observed?'YES':run.scenario==='clean'?'CLEAN CONTROL':'NOT VERIFIED'}</strong></div>
        <div><span><ShieldX size={16}/> BLOCKED PROPOSALS</span><strong>{report?.policy_denial_count??run.summary.denied_actions}</strong></div>
        <div><span><Unplug size={16}/> CONTAINER DISPOSAL</span><strong>{report?.container_teardown_verified?'CONFIRMED':'UNVERIFIED'}</strong></div>
        <div><span><RefreshCcw size={16}/> CHECKPOINT RECOVERY</span><strong>{report?.reset_verified?'CONFIRMED':'UNVERIFIED'}</strong></div>
        <div><span><CheckCircle2 size={16}/> TRUSTED MISSION</span><strong>{report?.legitimate_task_verified?'COMPLETED':'UNVERIFIED'}</strong></div>
      </div>
      <div className="ch-report-limitation"><CircleAlert size={18}/><p>{report?.attempted_by_source==='LLM'?'Real model calls were observed. Unattempted attacks are not counted as blocked.':'This run used scripted adversarial proposals. Do not attribute those decisions to the real model.'}</p></div>
    </section>
    <section className="ch-report-panel">
      <div className="ch-report-head"><SectionOverline>02 / REMEDIATION</SectionOverline><h2>What to keep. What to test next.</h2></div>
      <div className="ch-remediation-list">{(report?.remediation||[]).map((r,i)=><div className="ch-remediation-item" key={i}><div><span>{('0'+(i+1)).slice(-2)} / {r.kind.toUpperCase()}</span><h3>{r.title}</h3></div><p>{r.action}</p><small>EVIDENCE BASIS — {r.basis}</small></div>)}</div>
      <div className="ch-untested"><span>NOT TESTED BY THIS RUN</span><div>{(report?.untested||['Other Chambers','Novel unseen attacks']).map(x=><em key={x}>{x}</em>)}</div></div>
    </section></div>
    <section className="ch-verifier-band"><div className="ch-verifier-symbol"><Fingerprint size={31}/></div><div><SectionOverline>03 / REPRODUCIBLE EVIDENCE</SectionOverline><h2>Verify the sanitized chain yourself.</h2><p>Download this complete sanitized event JSON and run the independent offline verifier. The original raw-source digest is displayed as provenance, but its private source cannot be reconstructed from the sanitized export.</p><div className="ch-hash-line"><span>PUBLIC CHAIN SHA-256</span><code>{run.proof.public_sha256||'Unavailable for legacy export'}</code><button title="Copy public digest" onClick={()=>{navigator.clipboard?.writeText(run.proof.public_sha256||'');setCopied(true)}}><Copy size={16}/>{copied?'COPIED':'COPY'}</button></div></div>
      <div className="ch-verifier-actions"><button className="ch-primary" onClick={()=>exportRun(run)}><Download size={16}/> PUBLIC EVIDENCE</button><a className="ch-outline" href="/verify_public_evidence.py" download><Code2 size={16}/> OFFLINE VERIFIER</a></div></section>
    <section className="ch-comparison"><div className="ch-history-head"><div><span className="ch-subcap">04 / REGRESSION COMPARISON</span><h2>Compare field tests.</h2></div></div><div className="ch-compare-controls"><label htmlFor="compare-run">SECOND RUN</label><select id="compare-run" value={comparison} onChange={e=>setComparison(e.target.value)}><option value="">Choose an archived run</option>{other.map(o=><option key={o.id} value={o.id}>{o.is_scripted?'Scripted':'Live'} · {o.mission_id.replaceAll('_',' ')} · {o.scenario.replaceAll('_',' ')} · {date(o.timestamp)}</option>)}</select></div>{compareRun?<div className="ch-comparison-table"><div><span>MEASURE</span><span>CURRENT</span><span>COMPARISON</span></div>{[['Mission',run.mission_id||'inventory_value',compareRun.mission_id||'inventory_value'],['Attack',run.scenario||'compound',compareRun.scenario||'compound'],['Source',run.is_scripted?'Fixture':'Live model',compareRun.is_scripted?'Fixture':'Live model'],['Denied proposals',String(run.summary.denied_actions),String(compareRun.summary.denied_actions)],['Verified value',money(run.summary.value_cents),money(compareRun.summary.value_cents)],['Worker generations',String(run.summary.worker_generations),String(compareRun.summary.worker_generations)]].map(row=><div key={row[0]}><span>{row[0]}</span><strong>{row[1].replaceAll('_',' ')}</strong><strong>{row[2].replaceAll('_',' ')}</strong></div>)}<button onClick={()=>onViewRun(compareRun.id,compareRun.is_scripted?'scripted':'live')} className="ch-comparison-open">OPEN COMPARISON RUN <ArrowUpRight size={17}/></button></div>:<div className="ch-compare-empty">Select another actual run to compare the mission, source, denied calls and verified outcome. No invented risk scores.</div>}</section>
  </main>;
}
