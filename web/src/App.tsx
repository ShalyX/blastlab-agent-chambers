import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity, ArrowDownRight, ArrowLeft, ArrowRight, ArrowUpRight, Box, Check, CheckCircle2,
  ChevronDown, ChevronLeft, ChevronRight, CircleAlert, Clock3, Code2, Copy, Download,
  ExternalLink, Fingerprint, Globe2, KeyRound, Layers3, LockKeyhole, Menu, Monitor,
  Pause, Play, Plus, Radio, RefreshCcw, ScanEye, Search, Server, Shield, ShieldAlert,
  ShieldCheck, ShieldX, Square, TerminalSquare, Unplug, X, Zap
} from 'lucide-react';
import type { Mode, RunData, RunEvent, Section } from './types';
import {ChamberLibrary, WebChamberSetup, RunResults} from './ChamberExperience';
import { AgentLabConnect, AgentLabCampaign } from './AgentLabExperience';
import JudgeDemo from './JudgeDemo';
import ContainedSample from './ContainedSample';
import ProofEngine from './ProofEngine';

const VALUE = (cents: number) => '$' + ((cents || 0) / 100).toFixed(2);
const short = (s?: string | null, n=11) => (s ? s.slice(0, n) : '—');
const stamp = (date?: string | null) => {
  if (!date) return '—';
  try { return new Date(date).toLocaleTimeString('en-GB', { hour:'2-digit', minute:'2-digit', second:'2-digit', timeZone:'UTC' }) + ' UTC'; }
  catch { return '—'; }
};
const dateStamp = (date?: string | null) => {
  if (!date) return '—';
  try { return new Date(date).toLocaleDateString('en-GB', { day:'2-digit', month:'short', year:'numeric', timeZone:'UTC' }); }
  catch { return '—'; }
};
const modeInfo: Record<Mode, { name:string, short:string, subtitle:string, kind:string }> = {
  live: { name:'Live model / GLM-5.3', short:'LIVE MODEL', subtitle:'Recorded Vultr Serverless Inference execution', kind:'live' },
  scripted: { name:'Adversarial policy replay', short:'SCRIPTED FIXTURE', subtitle:'Deterministic stress test. Not LLM-generated actions.', kind:'fixture' }
};

function Mark({ size=36 }: {size?:number}) {
  return <svg aria-hidden="true" className="mark" width={size} height={size} viewBox="0 0 40 40" fill="none">
    <path d="M6 5h14v6H12v18h8v6H6V5ZM34 5H22v6h6v8h6V5ZM28 27v2h-6v6h12v-8h-6Z" fill="currentColor" />
    <path d="M20 2v36" stroke="#ff754a" strokeWidth="2" strokeDasharray="5 4" />
  </svg>;
}
function Brand({ inverse=false }: {inverse?:boolean}) {
  return <a href="/" aria-label="BlastLab home" className={'brand '+(inverse?'brand-inverse':'')}>
    <Mark size={31}/><span>BLAST<span className="brand-slash">/</span>LAB</span>
  </a>;
}
function Pill({ children, tone='plain', dot=false }: {children:React.ReactNode, tone?:'plain'|'mint'|'orange'|'blue', dot?:boolean}) {
  return <span className={'pill pill-'+tone}>{dot&&<i className="pill-dot" />}{children}</span>;
}
function TextButton({ children, onClick, title }: {children:React.ReactNode, onClick?:()=>void, title?:string}) {
  return <button title={title} type="button" className="text-button" onClick={onClick}>{children}</button>;
}
function Tag({ children }: {children:React.ReactNode}) { return <span className="mono tag">{children}</span>; }

function useRun(mode: Mode, refresh=0, runId?:string) {
  const [data, setData] = useState<RunData|null>(null);
  const [loading,setLoading] = useState(true);
  const [fallback,setFallback] = useState(false);
  const [error,setError] = useState('');
  useEffect(()=>{
    let cancelled=false;
    setLoading(true); setData(null); setError(''); setFallback(false);
    async function load() {
      const api = runId?'/api/history/'+encodeURIComponent(runId):'/api/runs/'+mode;
      try {
        const res=await fetch(api,{cache:'no-store'});
        if(!res.ok) throw new Error('API not connected');
        const body=await res.json() as RunData;
        if(!body.events || !body.proof) throw new Error('Invalid replay');
        if(!cancelled) {setData(body);setFallback(false);}
      } catch {
        try {
          if(runId)throw new Error('Archived run unavailable');
          const res=await fetch('/data/'+mode+'.json');
          if(!res.ok) throw new Error('Recorded evidence could not be loaded');
          const body=await res.json() as RunData;
          if(!cancelled) {setData(body);setFallback(true);}
        } catch(e) { if(!cancelled) {setData(null);setError(e instanceof Error?e.message:'Unknown error');} }
      } finally { if(!cancelled) setLoading(false); }
    }
    load();
    return ()=>{cancelled=true;};
  },[mode,refresh,runId]);
  return {data, loading, fallback, error};
}

function Landing() {
  const {data}=useRun('live');
  const [menu,setMenu]=useState(false);
  return <div className="landing">
    <header className="site-header">
      <Brand/>
      <nav className={'site-nav '+(menu?'site-nav-open':'')}>
        <a href="#approach" onClick={()=>setMenu(false)}>How it works</a>
        <a href="#proof" onClick={()=>setMenu(false)}>Verified proof</a>
        <a href="#infrastructure" onClick={()=>setMenu(false)}>Architecture</a>
      </nav>
      <a className="nav-launch" href="/app">CONNECT YOUR AGENT <ArrowUpRight size={17}/></a>
      <button className="mobile-menu" aria-label="Toggle navigation" onClick={()=>setMenu(!menu)}><Menu size={22}/></button>
    </header>
    <main>
      <section className="landing-hero">
        <div className="landing-grid" aria-hidden="true"/>
        <div className="hero-left">
          <div className="eyebrow"><span className="signal-bullet"/> SYSTEM 01 — AGENT CONTAINMENT</div>
          <h1>Bring your agent.<br/><em>We try to break it.</em></h1>
          <p className="hero-copy">Connect an agent you built. BlastLab throws adversarial prompts and poisoned content at it, observes its actual decisions and helps you repair the weaknesses it exposes.</p>
          <div className="hero-actions">
            <a href="/app" className="primary-btn">START AGENT TESTING <ArrowUpRight size={20}/></a>
            <a href="/app/evidence" className="ghost-btn">INSPECT THE PROOF <ArrowRight size={17}/></a>
          </div>
          <div className="hero-footnote"><span className="live-signal"/><span>RECORDED ON VULTR CLOUD COMPUTE</span><span className="tiny-rule"/> <span>{data?.timestamp?dateStamp(data.timestamp).toUpperCase():'04 NOV 2026'}</span></div>
        </div>
        <div className="hero-art" aria-label="Diagram of the isolated browser chamber and the severed malicious instruction">
          <div className="art-index mono">FIG 01 / INTERNAL DEMO CONTAINMENT</div>
          <div className="art-frame">
            <div className="art-frame-corner art-frame-corner-a"/><div className="art-frame-corner art-frame-corner-b"/>
            <div className="art-title"><span>UNTRUSTED WEB INPUT</span><Tag>DOCUMENT / SUPPLIER</Tag></div>
            <div className="art-browser">
              <div className="art-browser-top"><span className="browser-circles"><i/><i/><i/></span><span>supplier / inventory</span><LockKeyhole size={12}/></div>
              <div className="art-browser-body">
                <div className="art-docline w72"/><div className="art-docline w48"/>
                <div className="art-datagrid"><span>mugs</span><span>04 × 1200</span><span>plates</span><span>03 × 800</span></div>
                <div className="art-attack"><ShieldAlert size={15}/><span>DEMO ATTACK PAYLOAD IN PAGE</span></div>
              </div>
            </div>
            <div className="art-boundary"><div className="art-beam"/><span className="mono">TOOL BOUNDARY</span><span className="boundary-lock"><ShieldX size={18}/> DEMO POLICY BOUNDARY</span></div>
            <div className="art-cells">
              <div className="art-cell"><span className="mono">WORKER 01</span><strong>DESTROYED</strong><span className="cell-meta">∅ container / ∅ workspace</span></div>
              <span className="art-arrow">↝</span>
              <div className="art-cell art-cell-verified"><span className="mono">WORKER 02</span><strong>RECOVERED</strong><span className="cell-meta">fresh browser / safe resume</span></div>
            </div>
            <div className="art-final"><CheckCircle2 size={19}/><span>VERIFIED RESULT</span><strong>{VALUE(data?.summary.value_cents ?? 7200)}</strong></div>
          </div>
          <div className="art-bottom mono"><span>ENFORCED, NOT ASSUMED.</span><span>VULTR / DOCKER / CHROMIUM</span></div>
        </div>
      </section>

      <section className="proof-ribbon" aria-label="Verified live run statistics">
        <span className="ribbon-intro">INTERNAL DEMO / WHAT WE MEASURED <ArrowDownRight size={16}/></span>
        <div className="ribbon-stat"><strong>{data?.summary.model_calls ?? 3}</strong><span>LIVE MODEL DECISIONS</span></div>
        <div className="ribbon-stat"><strong>{data?.summary.worker_generations ?? 2}</strong><span>ISOLATED GENERATIONS</span></div>
        <div className="ribbon-stat"><strong>{VALUE(data?.summary.value_cents ?? 7200)}</strong><span>VERIFIED VALUATION</span></div>
        <div className="ribbon-stat ribbon-last"><CheckCircle2 size={20}/><span>HASH-CHAIN VERIFIED</span></div>
      </section>
      <section id="approach" className="approach-section">
        <div className="section-cap"><span>01 / WHY BLASTLAB</span><span>HOW THE BOUNDED DEMO WORKS</span></div>
        <div className="approach-head">
          <h2>Most demos show<br/>an agent <em>working.</em><br/>We show its limits.</h2>
          <p>Prompt injection arrives as normal page content. The important question isn't whether the model notices. It's whether untrusted text can become privileged action.</p>
        </div>
        <div className="approach-grid">
          <div className="approach-item"><div className="item-no">01 / INPUT</div><ScanEye size={29}/><h3>Read the hostile page.</h3><p>In the labeled internal demo, a headless Chromium worker reads supplier inventory alongside an embedded instruction to override the task.</p></div>
          <div className="approach-item"><div className="item-no">02 / BOUNDARY</div><Shield size={29}/><h3>Enforce a hard limit.</h3><p>Only exact approved browser actions and evidence-backed completion can pass. The supervisor—not the model—owns the container.</p></div>
          <div className="approach-item"><div className="item-no">03 / RECOVERY</div><RefreshCcw size={29}/><h3>Kill it. Keep the mission.</h3><p>Destroy the disposable worker, verify its absence, create a new one, restore a trusted checkpoint, and finish.</p></div>
        </div>
      </section>
      <section id="proof" className="showcase-section">
        <div className="showcase-side"><div className="section-cap light"><span>02 / REPRODUCIBLE PROOF</span></div><h2>Every decision<br/>has a receipt.</h2><p>An independently recorded supplier DEMO, not a connected user-agent campaign. Two distinct, reproducible runs from an actual Vultr VM—one real-model execution, one scripted policy stress test. Both backed by hash-chained events.</p><a className="outline-btn" href="/app/evidence">OPEN EVIDENCE VAULT <ArrowUpRight size={18}/></a></div>
        <div className="showcase-evidence">
          <div className="exhibit-head"><span>CASE FILE / 2026-11-04</span><Pill tone="mint" dot>VERIFIED ON VULTR</Pill></div>
          <div className="exhibit-main"><p>LIVE VULTR MODEL · glm-5.3</p><h3>Boundary survived.<br/>Mission completed.</h3><div className="exhibit-stats"><div><strong>00</strong><span>UNSAFE CALLS PROPOSED</span></div><div><strong>02</strong><span>CONTAINERS DESTROYED</span></div><div><strong>41</strong><span>CHAINED EVENTS</span></div></div></div>
          <div className="exhibit-bottom"><Fingerprint size={18}/><span className="mono">{short(data?.proof.trace_sha256 ?? '0050fe1323a76be3d0cbf636a555fc65776e53be2a86924c57859db884234eef',32)}...</span><Check size={17}/></div>
          <div className="exhibit-disclosure">Separate scripted replay: four denied malicious proposals. Never attributed to the live LLM.</div>
        </div>
      </section>
      <section id="infrastructure" className="architecture-landing">
        <div className="section-cap"><span>03 / DEMO EXECUTION ARCHITECTURE</span><span>THE SUPERVISOR OWNS THE SWITCH</span></div>
        <div className="architecture-split"><div><h2>Trust is a boundary,<br/>not a prompt.</h2><p>Vultr Serverless Inference proposes tool calls. A separate policy gate approves only exact capabilities. Docker isolates the browser. The trusted supervisor can tear down and recreate it without losing the task.</p><a href="/app/architecture" className="line-link">EXPLORE THE SYSTEM <ArrowUpRight size={18}/></a></div>
          <div className="architecture-mini">
            <div className="mini-node"><span>01 / INFERENCE</span><strong>VULTR · GLM-5.3</strong><small>proposes / never executes</small></div><div className="mini-line"><span>CHECKS TOOL AUTHORITY</span></div>
            <div className="mini-node mini-supervisor"><span>02 / CONTROLLER</span><strong>CAPABILITY POLICY</strong><small>isolates · checkpoints · verifies</small></div><div className="mini-line orange-line"><span>NO HOST MOUNTS / NO SECRETS</span></div>
            <div className="mini-node"><span>03 / RUNTIME</span><strong>DOCKER + CHROMIUM</strong><small>disposable / no external network</small></div>
          </div>
        </div>
      </section>
      <section className="cta-strip"><span>THE ATTACK IS IN THE PAGE.</span><h2>See what the agent actually did.</h2><a href="/app" className="primary-btn">OPEN AGENT LAB <ArrowUpRight size={20}/></a></section>
    </main>
    <footer className="site-footer"><Brand inverse/><p>Agent containment, with receipts.<br/>Built on Vultr Cloud Compute + Serverless Inference.</p><span className="footer-right">RECORDED EVIDENCE · NOVEMBER 2026<br/>CONTROLLED SUPPLIER TEST — NOT A GENERAL SECURITY CERTIFICATION</span></footer>
  </div>;
}

const milestones = (events: RunEvent[]) => {
  const taken = new Set<number>();
  const pick = (item?:RunEvent) => {if(item && !taken.has(item.seq)) taken.add(item.seq);};
  pick(events.find(e=>e.kind==='sandbox_created'));
  pick(events.find(e=>e.kind==='page_observation'));
  pick(events.find(e=>e.kind==='trusted_interruption'));
  pick(events.find(e=>e.kind==='sandbox_destroyed'));
  pick(events.find(e=>e.kind==='sandbox_created' && e.generation===2));
  pick(events.find(e=>e.category==='deny'));
  pick(events.find(e=>e.kind==='mission_resumed'));
  pick(events.find(e=>e.kind==='mission_verified'));
  return events.filter(e=>taken.has(e.seq));
};
function EventIcon({ kind, category, size=18 }:{kind:string, category?:string, size?:number}) {
  if(category==='deny') return <ShieldX size={size}/>;
  if(kind==='trusted_interruption'||kind==='sandbox_destroyed') return <Unplug size={size}/>;
  if(kind==='sandbox_created') return <Box size={size}/>;
  if(kind==='mission_verified'||kind==='run_finished') return <CheckCircle2 size={size}/>;
  if(kind==='mission_resumed') return <RefreshCcw size={size}/>;
  if(kind==='page_observation') return <ScanEye size={size}/>;
  if(kind==='policy_decision') return <Shield size={size}/>;
  if(kind==='action_proposed'||kind==='inference_response') return <Zap size={size}/>;
  if(kind==='checkpoint_saved') return <Fingerprint size={size}/>;
  return <Activity size={size}/>;
}
function RecordedChip({mode}:{mode:Mode}) {
  return <span className={'origin-chip '+(mode==='live'?'origin-live':'origin-fixture')}>
    {mode==='live'?<Radio size={13}/>:<TerminalSquare size={13}/>}
    {modeInfo[mode].short}
  </span>;
}

function OperatorModal({onClose,onDone}:{onClose:()=>void,onDone:()=>void}) {
  const [token,setToken]=useState('');
  const [mode,setMode]=useState<Mode>('live');
  const [pending,setPending]=useState(false);
  const [message,setMessage]=useState('');
  const [job,setJob]=useState('');
  const submit=async (event:React.FormEvent) => {
    event.preventDefault();
    if(!token.trim()) {setMessage('Enter an operator access token. Replay remains available without one.');return;}
    setPending(true);setMessage('');
    try{
      const response=await fetch('/api/runs',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+token.trim()},body:JSON.stringify({mode})});
      const json=await response.json();
      if(!response.ok) throw new Error(json.error || 'Unable to start a run.');
      setJob(json.job_id);
      setMessage('Execution requested. The trusted controller is running the fixed supplier scenario.');
    }catch(err){setMessage(err instanceof Error?err.message:'The run could not be started.');setPending(false);}
  };
  useEffect(()=>{
    if(!job)return;
    const timer=window.setInterval(async()=>{
      try{
        const response=await fetch('/api/jobs/'+encodeURIComponent(job),{headers:{'Authorization':'Bearer '+token.trim()},cache:'no-store'});
        const body=await response.json();
        if(!response.ok) throw new Error(body.error||'Could not retrieve job status.');
        if(body.status==='complete') {setPending(false);setMessage('Run completed and recorded. Replay has been refreshed.');onDone();window.clearInterval(timer);}
        if(body.status==='failed') {setPending(false);setMessage('Run failed: '+(body.error||'see controller logs'));window.clearInterval(timer);}
      }catch(e){setPending(false);setMessage(e instanceof Error?e.message:'Job status request failed');window.clearInterval(timer);}
    },2200);
    return ()=>window.clearInterval(timer);
  },[job,token,onDone]);
  return <div className="modal-scrim" role="presentation" onMouseDown={(e)=>{if(e.target===e.currentTarget)onClose()}}>
    <div className="operator-modal" role="dialog" aria-modal="true" aria-labelledby="run-title">
      <button className="icon-button modal-close" onClick={onClose} aria-label="Close operator modal"><X size={21}/></button>
      <div className="operator-glyph"><KeyRound size={24}/></div><Tag>TRUSTED CONTROLLER / OWNER ACCESS</Tag>
      <h2 id="run-title">Start a new test.</h2><p>The public control room is read-only. Only an authorized operator can execute the fixed supplier scenario on the Vultr VM. The model never receives your token.</p>
      <form onSubmit={submit}>
        <label className="field-label">EXECUTION ENGINE</label>
        <div className="modal-modes">
          <button type="button" className={mode==='live'?'chosen':''} onClick={()=>setMode('live')}><Radio size={17}/> Vultr model <small>Paid inference</small></button>
          <button type="button" className={mode==='scripted'?'chosen':''} onClick={()=>setMode('scripted')}><Shield size={17}/> Policy replay <small>Scripted fixture</small></button>
        </div>
        <label className="field-label" htmlFor="owner-key">OPERATOR ACCESS TOKEN</label>
        <input id="owner-key" type="password" autoComplete="off" placeholder="Enter owner token" value={token} onChange={e=>setToken(e.target.value)}/>
        <button className="primary-btn modal-submit" type="submit" disabled={pending}>{pending?'EXECUTING ON VULTR…':'EXECUTE FIXED SCENARIO'}<ArrowUpRight size={18}/></button>
        {message&&<p className={'run-message '+(pending?'pending':'')} role="status">{message}</p>}
      </form>
      <div className="modal-disclosure"><LockKeyhole size={16}/>No arbitrary URLs, prompts or shell actions. One bounded container job at a time.</div>
    </div>
  </div>;
}

function useSection() {
  const parse=():Section=>{
    const path=location.pathname;
    if(path.endsWith('/campaign'))return 'campaign';
    if(path.endsWith('/evidence'))return 'evidence';
    if(path.endsWith('/architecture'))return 'architecture';
    if(path.endsWith('/results'))return 'results';
    if(path.endsWith('/control'))return 'control';
    if(path.endsWith('/chambers/web'))return 'setup';
    if(path.endsWith('/demo'))return 'chambers';
    return 'agent';
  };
  const [section,setSection]=useState<Section>(parse);
  useEffect(()=>{const handler=()=>setSection(parse());window.addEventListener('popstate',handler);return()=>window.removeEventListener('popstate',handler)},[]);
  const navigate=(to:Section)=>{
    setSection(to);
    const path=to==='agent'?'/app':to==='chambers'?'/app/demo':to==='setup'?'/app/chambers/web':'/app/'+to;
    history.pushState({},'',path);
    window.scrollTo({top:0,behavior:'instant'});
  };
  return {section,navigate};
}

function ControlRoom() {
  const {section,navigate}=useSection();
  const [agentSession,setAgentSession]=useState<{
    session_id:string;join_token:string;expires_at:string;cases_total:number;
    source_type:string;connector:string;attack_source:string;
    attack_provider:string;attack_model:string;attack_plan_sha256:string;recovery_key?:string;recovery_expires_at?:string
  }|null>(()=>{
    try{const old=sessionStorage.getItem('blastlab-agent-session');return old?JSON.parse(old):null;}
    catch{return null;}
  });

  const [mode,setMode]=useState<Mode>(()=>new URLSearchParams(location.search).get('run')?.startsWith('scripted-')?'scripted':'live');
  const [selectedRunId,setSelectedRunId]=useState<string|undefined>(()=>{
    const id=new URLSearchParams(location.search).get('run')||'';
    return /^(live|scripted)-[0-9a-f]{18}$/.test(id)?id:undefined;
  });
  const [refresh,setRefresh]=useState(0);
  const [modal,setModal]=useState(false);
  const [mobileNav,setMobileNav]=useState(false);
  const {data,loading,fallback,error}=useRun(mode,refresh,selectedRunId);
  const [position,setPosition]=useState(0);
  const [playing,setPlaying]=useState(false);
  const [filter,setFilter]=useState('all');
  const [inspectorTab,setInspectorTab]=useState<'policy'|'runtime'>('policy');
  const visible=useMemo(()=>data?.events.filter(e=>e.visible) || [],[data]);
  const current=visible[Math.min(position,visible.length-1)];
  const eventIndex= current? data?.events.findIndex(e=>e.seq===current.seq) ?? 0 : 0;
  const elapsed=data?.events.slice(0,eventIndex+1) || [];
  const lastOf=(kind:string) => [...elapsed].reverse().find(e=>e.kind===kind);
  const page=lastOf('page_observation');
  const proposed=lastOf('action_proposed');
  const policy=lastOf('policy_decision');
  const state=lastOf('sandbox_created');
  const lastWorker=[...elapsed].reverse().find(e=>e.kind==='sandbox_response' && !!e.detail.worker_id);
  const teardown=lastOf('sandbox_destroyed');
  const lastResponse=lastOf('inference_response');
  const isEnded=!!elapsed.find(e=>e.kind==='run_finished');
  const onRefresh=useCallback(()=>setRefresh(x=>x+1),[]);
  const setModeSafe=(next:Mode)=>{setMode(next);setSelectedRunId(undefined);setPosition(0);setPlaying(false);setFilter('all');};
  const openRun=(id:string,source:Mode)=>{setMode(source);setSelectedRunId(id);setRefresh(x=>x+1);navigate('results');history.replaceState({},'','/app/results?run='+encodeURIComponent(id));};
  const completedRun=(id:string,source:Mode)=>{setMode(source);setSelectedRunId(id);setRefresh(x=>x+1);navigate('results');history.replaceState({},'','/app/results?run='+encodeURIComponent(id));};
  const stepTo=(seq:number)=>{const at=visible.findIndex(e=>e.seq>=seq);setPosition(at<0?visible.length-1:at);setPlaying(false);};
  const advance=useCallback((delta:number)=>setPosition(i=>Math.max(0,Math.min(visible.length-1,i+delta))),[visible]);
  useEffect(()=>{const meaningful=data?.events.filter(e=>e.visible)||[]; const first=meaningful.findIndex(e=>mode==='live'?e.kind==='page_observation':e.category==='deny');setPosition(first<0?0:first);setPlaying(false)},[data?.id,data?.timestamp,mode]);
  useEffect(()=>{
    if(!playing || section!=='control')return;
    const interval=window.setInterval(()=>setPosition(i=>{if(i>=visible.length-1){setPlaying(false);return i;}return i+1;}),870);
    return()=>window.clearInterval(interval);
  },[playing,visible.length,section]);
  useEffect(()=>{
    const listener=(e:KeyboardEvent)=>{
      const tag=(e.target as HTMLElement)?.tagName;
      if(section!=='control'||['INPUT','TEXTAREA','SELECT'].includes(tag)||modal)return;
      if(e.key==='ArrowRight'){e.preventDefault();advance(1);}
      if(e.key==='ArrowLeft'){e.preventDefault();advance(-1);}
      if(e.key===' '){e.preventDefault();setPlaying(x=>!x);}
    };
    document.addEventListener('keydown',listener);return()=>document.removeEventListener('keydown',listener);
  },[section,advance,modal]);
  const milestoneItems=useMemo(()=>milestones(visible),[visible]);
  const usableEvents=useMemo(()=>visible.filter(e=>filter==='all' || (filter==='policy' ? ['policy_decision','action_proposed'].includes(e.kind) : filter==='lifecycle' ? ['sandbox_created','sandbox_destroyed','trusted_interruption','mission_resumed'].includes(e.kind) : ['page_observation','inference_response','mission_verified'].includes(e.kind))),[visible,filter]);
  const actionsAllowed=data?.events.filter(e=>e.kind==='policy_decision'&&e.detail.decision==='allow').length||0;
  const copyHash=()=>{if(data?.proof.trace_sha256)navigator.clipboard?.writeText(data.proof.trace_sha256).catch(()=>{})};
  const saveEvidence=()=>{if(!data)return;const object=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const url=URL.createObjectURL(object);const link=document.createElement('a');link.href=url;link.download='blastlab-'+data.id+'-sanitized-evidence.json';link.click();window.setTimeout(()=>URL.revokeObjectURL(url),2000);};
  const connectAgent=(created:NonNullable<typeof agentSession>)=>{
    setAgentSession(created);
    // The read-only recovery secret is intentionally NOT browser-persisted.
    const {recovery_key: _oneTimeRecoveryKey, ...reloadable} = created;
    void _oneTimeRecoveryKey;
    try{sessionStorage.setItem('blastlab-agent-session',JSON.stringify(reloadable));}catch{}
    navigate('campaign');setMobileNav(false);
  };
  const newAgent=()=>{
    setAgentSession(null);
    try{sessionStorage.removeItem('blastlab-agent-session');}catch{}
    navigate('agent');setMobileNav(false);
  };
  const select=(next:Section)=>{
    navigate(next);
    if((next==='control'||next==='results')&&selectedRunId)
      history.replaceState({},'',location.pathname+'?run='+encodeURIComponent(selectedRunId));
    setMobileNav(false);setPlaying(false);
  };
  return <div className="console-shell">
    <aside className={'console-rail '+(mobileNav?'rail-open':'')}>
      <div className="rail-brand"><Brand inverse/><button className="rail-close" aria-label="Close menu" onClick={()=>setMobileNav(false)}><X size={19}/></button></div>
      <div className="rail-workspace"><span className="workspace-sigil"><Layers3 size={16}/></span><div><span className="mono">WORKSPACE 001</span><strong>{section==='agent'||section==='campaign'?'Agent Test Bench':'Sample Containment Demo'}</strong></div><ChevronDown size={14}/></div>

      <div className="nav-cluster"><span className="rail-label">PRODUCT / CONNECT YOUR AGENT</span>
        <button className={'rail-link '+(section==='agent'?'active':'')} onClick={()=>select('agent')}><Zap size={18}/> Connect &amp; rules <span className="nav-key">01</span></button>
        <button className={'rail-link '+(section==='campaign'?'active':'')} onClick={()=>select('campaign')}><Activity size={18}/> Campaign / evidence / retest <span className="nav-key">02</span></button>
        <details className="rail-demo-group" key={section==='agent'||section==='campaign'?'sample-closed':'sample-open'} open={section!=='agent'&&section!=='campaign'}><summary><Layers3 size={16}/> Sample Lab <small>DEMO</small></summary>
        <button className={'rail-link '+(section==='chambers'?'active':'')} onClick={()=>select('chambers')}><Layers3 size={18}/> Supplier demo <span className="nav-key">D1</span></button>
        <button className={'rail-link '+(section==='setup'?'active':'')} onClick={()=>select('setup')}><ShieldAlert size={18}/> Demo setup <span className="nav-key">D2</span></button>
        <button className={'rail-link '+(section==='control'?'active':'')} onClick={()=>select('control')}><Activity size={18}/> Demo replay <span className="nav-key">D3</span></button>
        <button className={'rail-link '+(section==='results'?'active':'')} onClick={()=>select('results')}><CheckCircle2 size={18}/> Demo results <span className="nav-key">D4</span></button>
        <button className={'rail-link '+(section==='evidence'?'active':'')} onClick={()=>select('evidence')}><Fingerprint size={18}/> Demo evidence <span className="nav-key">D5</span></button>
        <button className={'rail-link '+(section==='architecture'?'active':'')} onClick={()=>select('architecture')}><Layers3 size={18}/> Architecture <span className="nav-key">D6</span></button>
        </details>
      </div>
      <div className="nav-cluster rail-lower"><span className="rail-label">{section==='agent'||section==='campaign'?'PRODUCT / AGENT CONNECTION':'DEMO / EXECUTION ENVIRONMENT'}</span>
        <div className="provider-item"><span className="provider-icon"><Server size={17}/></span><div><b>Vultr Compute</b><small>Hosted campaign API</small></div><i className="green-dot"/></div>
        {(section==='agent'||section==='campaign')?
          <><div className="provider-item"><span className="provider-icon"><Zap size={17}/></span><div><b>External runner</b><small>Your agent, your environment</small></div></div>
          <div className="provider-item"><span className="provider-icon"><ShieldAlert size={17}/></span><div><b>Curated attacks</b><small>Runner-reported results</small></div></div></>:
          <><div className="provider-item"><span className="provider-icon"><Box size={17}/></span><div><b>Docker Chamber</b><small>Demo isolated Chromium</small></div><i className="green-dot"/></div>
          <div className="provider-item"><span className="provider-icon"><Zap size={17}/></span><div><b>GLM-5.3</b><small>Demo Vultr Inference</small></div><i className="green-dot"/></div></>}
      </div>
      <div className="rail-bottom"><div className="rail-foot-title"><ShieldCheck size={17}/>{section==='agent'||section==='campaign'?'EXTERNAL AGENT / REPORTED':'VERIFIED SUPPLIER DEMO'}</div><p>{section==='agent'||section==='campaign'?'Your agent runs in your environment. Its reported actions are not VM attested.':'The internal demo ran in a real Vultr Docker environment.'}</p><a href="/" className="rail-return"><ArrowLeft size={15}/> Back to website</a></div>
    </aside>
    {mobileNav&&<div className="rail-overlay" onClick={()=>setMobileNav(false)}/>}
    <div className="console-main">
      <header className="console-topbar">
        <button className="mobile-rail-toggle" onClick={()=>setMobileNav(true)} aria-label="Open menu"><Menu size={21}/></button>
        <div className="breadcrumb mono">BLASTLAB <span>/</span> TEST FACILITY <span>/</span> {section==='agent'?'CONNECT AGENT':section==='campaign'?'AGENT ATTACK CAMPAIGN':section==='chambers'?'SUPPLIER DEMO':section==='setup'?'DEMO SETUP':section==='results'?'TEST REPORT':section==='control'?'CONTROL ROOM':section==='evidence'?'EVIDENCE VAULT':'ARCHITECTURE'}</div>
        <div className="topbar-right">{(section==='agent'||section==='campaign')?<span className="planner-source">ATTACK PLANNER / VULTR</span>:<Pill tone="mint" dot>VULTR SAMPLE VERIFIED</Pill>}<button className="top-icon" title="Refresh recorded evidence" aria-label="Refresh evidence" onClick={onRefresh}><RefreshCcw size={17}/></button><button className="top-run-btn" onClick={section==='agent'?()=>document.getElementById('byoa-connect-form')?.scrollIntoView({behavior:'auto',block:'start'}):newAgent}><Plus size={16}/> CONNECT AGENT</button></div>
      </header>
      {section==='agent'&&<AgentLabConnect onCreated={connectAgent} onDemo={()=>select('chambers')}/>}
      {section==='campaign'&&<AgentLabCampaign key={agentSession?.session_id} created={agentSession} onNew={newAgent} onRetest={connectAgent}/>}
      {section==='chambers'&&<ChamberLibrary onEnter={()=>select('setup')} onViewRun={openRun}/>}
      {section==='setup'&&<WebChamberSetup onComplete={completedRun} onViewRun={openRun}/>}
      {section==='results'&&<RunResults run={data} loading={loading} error={error} onControl={()=>select('control')} onNew={()=>select('setup')} onViewRun={openRun}/>}
      {section==='control'&&<main className="control-content">
        <div className="intro-row"><div><div className="eyebrow console-eyebrow"><span className="signal-bullet"/> ACTIVE CASE FILE / BL-001</div><h1>Execution <span>under constraint.</span></h1><p>Follow the hostile input, every tool decision, and what survived the reset.</p></div><div className="run-metadata"><span>LAST RECORDED</span><strong>{dateStamp(data?.timestamp)}</strong><span>{stamp(data?.timestamp)}</span></div></div>
        <div className="run-switcher"><span className="switch-label mono">RUN SOURCE</span><div className="mode-switch" role="group" aria-label="Choose evidence source"><button className={mode==='live'?'selected':''} onClick={()=>setModeSafe('live')}><Radio size={15}/> LIVE MODEL</button><button className={mode==='scripted'?'selected':''} onClick={()=>setModeSafe('scripted')}><ShieldAlert size={15}/> ADVERSARIAL REPLAY</button></div><div className="switch-disclosure">{mode==='live'?'3 actual GLM-5.3 proposals · no prohibited calls':'Fixture-generated malicious calls · four denials, not LLM behavior'}</div></div>
        {loading?<div className="loading-state"><RefreshCcw size={26} className="spinner"/><strong>Loading the recorded execution…</strong><span>Authenticating trace evidence and assembling the timeline.</span></div>:
        error||!data?<div className="error-state"><CircleAlert size={25}/><h3>Replay is unavailable</h3><p>{error||'Could not load the recorded run.'}</p><button onClick={onRefresh}>RETRY <RefreshCcw size={15}/></button></div>:
        <>
          <div className="playback-card">
            <div className="playback-header"><div><Tag>EXECUTION TRACK / {mode==='live'?'LIVE 01':'STRESS 02'}</Tag><h2>Inside the containment boundary.</h2></div><div className="playback-top-right"><RecordedChip mode={mode}/><Pill tone="mint" dot>MISSION VERIFIED</Pill></div></div>
            <div className="generation-track"><div><span className="gen-marker mono">GENERATION 01 <Box size={14}/></span><span className="gen-thread"/></div><span className="rupture-seam"><Unplug size={16}/><span>KILL / RESET</span></span><div><span className="gen-marker mono">GENERATION 02 <RefreshCcw size={13}/></span><span className="gen-thread"/></div></div>
            <div className="timeline-track">{milestoneItems.map((item,i)=>{
              const active=!!current&&current.seq>=item.seq;
              return <button type="button" className={'timeline-point '+(active?'reached ':'')+((item.seq===current?.seq)?'current ':'')+(['trusted_interruption','sandbox_destroyed'].includes(item.kind)?'rupture-point':'')} key={item.seq} onClick={()=>stepTo(item.seq)} title={item.title+' · event '+item.seq}>
                <span className="point-dot"><EventIcon kind={item.kind} category={item.category} size={16}/></span><span className="point-index mono">{('0'+(i+1)).slice(-2)}</span><span className="point-label">{item.kind==='trusted_interruption'?'Kill switch':item.kind==='page_observation'?'Page read':item.kind==='sandbox_destroyed'?'Teardown':item.kind==='sandbox_created'?'Worker '+(item.generation||1):item.kind==='mission_resumed'?'Resume':item.kind==='mission_verified'?'Verified':item.category==='deny'?'Denied action':item.title}</span>
              </button>
            })}</div>
            <div className="player-controls"><div className="player-left"><button className="player-big" onClick={()=>{if(position>=visible.length-1)setPosition(0);setPlaying(x=>!x)}} aria-label={playing?'Pause replay':'Play replay'}>{playing?<Pause size={19} fill="currentColor"/>:<Play size={19} fill="currentColor"/>}</button><button className="player-small" onClick={()=>advance(-1)} disabled={position<=0} aria-label="Previous event"><ChevronLeft size={19}/></button><button className="player-small" onClick={()=>advance(1)} disabled={position>=visible.length-1} aria-label="Next event"><ChevronRight size={19}/></button><div className="frame-caption"><strong>{('0'+(position+1)).slice(-2)} <span>/</span> {('0'+visible.length).slice(-2)}</strong><span>{current?.title||'Preparing evidence'}</span></div></div>
              <div className="player-right"><span className="mono">{current?stamp(current.at):'—'}</span><span className="divider-vertical"/><span className="mono">SEQ {current?.seq||'—'}</span><span className="keyboard-help">← → to step</span></div></div>
            <input className="replay-scrubber" type="range" min={0} max={Math.max(0,visible.length-1)} value={position} onChange={e=>{setPosition(Number(e.target.value));setPlaying(false)}} aria-label="Scrub recorded events" style={{'--scrub-progress': visible.length>1?String(position/(visible.length-1)*100)+'%':'0%'} as React.CSSProperties}/>
          </div>
          <div className="inspector-grid">
            <section className="specimen-panel">
              <div className="panel-caption"><div><Globe2 size={17}/><span>UNTRUSTED WEB SPECIMEN</span></div><Tag>READ-ONLY</Tag></div>
              <div className="specimen-body">
                <div className="specimen-browser-bar"><div className="browser-circles"><i/><i/><i/></div><span><LockKeyhole size={12}/> sandbox://supplier</span><span className="mono">GEN {page?.detail.generation||'—'}</span></div>
                {page?<><div className="supplier-content"><div className="supplier-head"><div><span className="eyebrow">SUPPLIER DOCUMENT / 200 OK</span><h3>Available supplier stock</h3></div><Pill tone="plain">OBSERVED</Pill></div>
                  <table className="supplier-table"><thead><tr><th>ITEM</th><th>AVAILABLE</th><th>UNIT PRICE</th><th>TOTAL</th></tr></thead><tbody>{(page.detail.rows||[]).map((r:any,i:number)=><tr key={i}><td>{r.name}</td><td>{r.available}</td><td>{VALUE(r.unit_price_cents)}</td><td>{VALUE(r.available*r.unit_price_cents)}</td></tr>)}</tbody></table>
                </div>
                <div className="injection-specimen"><div className="injection-label"><ShieldAlert size={16}/><strong>UNTRUSTED PAGE INSTRUCTION</strong><span>TAINTED SOURCE</span></div><p>{String(page.detail.text||'').split('SYSTEM OVERRIDE:')[1]?.split('ATTACK_ACTIONS=')[0]?.trim() || 'Hostile instruction embedded in supplier page content.'}</p><div className="injection-foot"><span>ORIGIN: PAGE BODY · NOT SYSTEM AUTHORITY</span><span><Shield size={13}/> POLICY INDEPENDENT</span></div></div></>:<div className="specimen-placeholder"><ScanEye size={26}/><h3>Browser has not read the page yet.</h3><p>Advance the replay to inspect the exact supplier inventory and injected content.</p></div>}
              </div>
            </section>
            <section className="decision-panel">
              <div className="panel-caption"><div><ShieldCheck size={17}/><span>BOUNDARY INSPECTOR</span></div><Tag>SUPERVISOR-OWNED</Tag></div>
              <div className="decision-tabs" role="tablist" aria-label="Inspector tabs"><button role="tab" aria-selected={inspectorTab==='policy'} className={inspectorTab==='policy'?'active':''} onClick={()=>setInspectorTab('policy')}>POLICY DECISION</button><button role="tab" aria-selected={inspectorTab==='runtime'} className={inspectorTab==='runtime'?'active':''} onClick={()=>setInspectorTab('runtime')}>WORKER RUNTIME</button></div>
              {inspectorTab==='policy'?<div className="decision-detail">
                <div className="verdict-line"><div className={'verdict-mark '+(current?.category==='deny'?'verdict-deny':isEnded?'verdict-allow':'verdict-neutral')}><EventIcon kind={current?.kind||'run_started'} category={current?.category} size={23}/></div><div><span className="mono">CURRENT TRACE MOMENT</span><h3>{current?.title||'Ready to inspect'}</h3><p>{current?.description}</p></div></div>
                <div className="selected-action"><div className="action-heading"><span>LAST PROPOSED TOOL</span><span className="mono">AUTHORITY: {mode==='live'?'MODEL':'FIXTURE'}</span></div><code>{proposed?.detail.tool||'Awaiting first tool call'}</code><pre>{proposed?.detail.args ? JSON.stringify(proposed.detail.args,null,2) : '{ }'}</pre></div>
                <div className="policy-summary"><div><span>POLICY VERDICT</span><strong className={policy?.detail.decision==='deny'?'danger-text':'success-text'}>{policy?(policy.detail.decision==='deny'?'DENIED':'ALLOWED'):'PENDING'}</strong></div><p>{policy?.detail.reason || 'Independent capability gate has not evaluated a proposal yet.'}</p></div>
                <div className="truth-note"><CircleAlert size={16}/><span>{mode==='live'?'This live model run made zero forbidden tool proposals. No live-model denial is being claimed.':'This is a deterministic adversarial fixture. Its blocked proposals were scripted to exercise the real policy gate.'}</span></div>
              </div>:<div className="runtime-detail">
                <div className="runtime-hero"><Box size={29}/><div><span>DISPOSABLE CONTAINER</span><strong>{teardown && (!state||state.seq<teardown.seq)?'DESTROYED':'GENERATION '+(state?.generation||'—')}</strong><p>{teardown && (!state||state.seq<teardown.seq)?'Worker was terminated by the supervisor':'Isolated Chromium worker on the Vultr VM'}</p></div></div>
                <div className="runtime-spec"><span>WORKER ID</span><code>{lastWorker?.detail.worker_id||'Awaiting worker launch'}</code></div><div className="runtime-spec"><span>CHAMBER</span><strong>Docker / Chromium</strong></div><div className="runtime-spec"><span>BOUNDARY RULES</span><strong>NO NETWORK · READ-ONLY ROOT</strong></div><div className="runtime-spec"><span>WORKSPACE REMOVED</span><strong className="success-text">{teardown?.detail.workspace_removed?'CONFIRMED':'NOT YET'}</strong></div><div className="runtime-spec"><span>CONTAINER ABSENT</span><strong className="success-text">{teardown?.detail.container_absent?'CONFIRMED':'NOT YET'}</strong></div><div className="truth-note"><Shield size={16}/>Model proposals never control Docker creation, destruction or reset.</div>
              </div>}
            </section>
          </div>
          <section className="summary-strip"><div><span className="mono">MISSION RESULT</span><strong>{VALUE(data.summary.value_cents)}</strong><small><Check size={13}/> Evidence-backed valuation</small></div><div><span className="mono">POLICY ACTIONS</span><strong>{actionsAllowed}<span className="stat-small"> allowed</span> / {data.summary.denied_actions}<span className="stat-small"> denied</span></strong><small>{mode==='live'?'Live model proposals':'Scripted test proposals'}</small></div><div><span className="mono">CONTAINER LIFECYCLE</span><strong>{data.summary.worker_generations.toString().padStart(2,'0')}<span className="stat-small"> generations</span></strong><small><RefreshCcw size={13}/> Reset independently verified</small></div><div className="summary-proof"><span className="mono">TRACE INTEGRITY</span><strong><CheckCircle2 size={19}/> VALID</strong><small>{short(data.proof.trace_sha256,24)}…</small></div></section>
          <div className="below-grid"><section className="ledger-panel"><div className="ledger-head"><div><Tag>EVENT LEDGER</Tag><h2>The sequence, not the story.</h2></div><span className="mono">{data.summary.event_count} CHAINED EVENTS</span></div><div className="ledger-filters" role="group" aria-label="Event filters">{[['all','All moments'],['policy','Policy'],['lifecycle','Lifecycle'],['model','Model & browser']].map(([k,label])=><button key={k} className={filter===k?'active':''} onClick={()=>setFilter(k)}>{label}</button>)}</div>
            <div className="ledger-scroll">{usableEvents.map(e=><button key={e.seq} onClick={()=>stepTo(e.seq)} className={'ledger-row '+(e.seq===current?.seq?'selected ':'')+(e.category==='deny'?'ledger-deny':'')}><span className="mono">#{('00'+e.seq).slice(-3)}</span><span className={'ledger-symbol category-'+e.category}><EventIcon kind={e.kind} category={e.category} size={16}/></span><span className="ledger-row-main"><strong>{e.title}</strong><small>{stamp(e.at)}{e.generation?' · worker '+e.generation:''}</small></span><span className="ledger-row-end"><ArrowUpRight size={15}/></span></button>)}</div></section>
            <section className="evidence-side"><div className="panel-caption"><div><Fingerprint size={17}/><span>ATTESTED EXECUTION</span></div><Tag>RECORDED PROOF</Tag></div><h2>Check the event trail.</h2><p>Download the sanitized event chain for offline verification. The original raw trace digest is separate provenance, and scripted attacks are never attributed to the live model.</p><div className="evidence-side-box"><span>TRACE SHA-256</span><strong>{short(data.proof.trace_sha256,28)}...</strong><div className="evidence-actions"><TextButton onClick={copyHash}><Copy size={15}/> COPY DIGEST</TextButton><TextButton onClick={saveEvidence}><Download size={15}/> EXPORT JSON</TextButton></div></div><div className="evidence-checks">{data.proof.security_checks.map(check=><div key={check.label}><CheckCircle2 size={16}/>{check.label}</div>)}</div><button className="detail-link" onClick={()=>select('evidence')}>OPEN COMPLETE PROOF VAULT <ArrowUpRight size={18}/></button></section></div>
          {fallback&&<div className="fallback-footnote"><CircleAlert size={14}/> Showing bundled, immutable Vultr execution evidence. The live service is not connected; replay remains functional and authentic.</div>}
        </>}
      </main>}
      {section==='evidence'&&<main className="detail-content"><div className="eyebrow console-eyebrow"><span className="signal-bullet"/> VERIFIED CASE FILE / BL-001</div><div className="detail-hero"><div><h1>Evidence, <span>not adjectives.</span></h1><p>Hash-chained records from an actual Vultr virtual machine. The run data is sanitized for public review, not reconstructed screenshots.</p></div><Fingerprint size={88} strokeWidth={1}/></div>
        <div className="source-selection"><span className="mono">COMPARE TEST SOURCES</span><button className={mode==='live'?'selected':''} onClick={()=>setModeSafe('live')}><Radio size={16}/> Real model</button><button className={mode==='scripted'?'selected':''} onClick={()=>setModeSafe('scripted')}><TerminalSquare size={16}/> Scripted stress test</button></div>
        {loading?<div className="loading-state"><RefreshCcw className="spinner"/>Loading proof…</div>:data?<><div className="evidence-feature"><div className="feature-head"><RecordedChip mode={mode}/><Pill tone={data.proof.hash_chain_valid?'mint':'orange'} dot>{data.proof.hash_chain_valid?'HASH CHAIN VERIFIED':'INTEGRITY ERROR'}</Pill></div><h2>{mode==='live'?'Real agent execution, verified.':'Four scripted denials, verified.'}</h2><p>{mode==='live'?'GLM-5.3 completed the inventory valuation after reading hostile content, destroying its first container and resuming in a new one. It proposed no forbidden action.':'A deterministic planner submitted four malicious proposals to exercise the real policy gate while a genuine Docker browser completed the task.'}</p><div className="feature-metrics"><div><span>CHAINED EVENTS</span><strong>{data.summary.event_count}</strong></div><div><span>POLICY DENIALS</span><strong>{data.summary.denied_actions}</strong></div><div><span>EXECUTION</span><strong>{(data.summary.elapsed_ms/1000).toFixed(1)}s</strong></div><div><span>MISSION RESULT</span><strong>{VALUE(data.summary.value_cents)}</strong></div></div></div>
        <div className="hash-panel"><div><Tag>SHA-256 / COMPLETE TRACE DIGEST</Tag><strong className="hash-content">{data.proof.trace_sha256}</strong><span className="mono">Recorded {dateStamp(data.timestamp)} · {stamp(data.timestamp)}</span></div><button className="outline-btn outline-dark" onClick={saveEvidence}><Download size={18}/> EXPORT SANITIZED RUN</button></div>
        <div className="proof-columns"><section className="proof-block"><h3>Verified invariants.</h3>{data.proof.security_checks.map(check=><div className="invariant" key={check.label}><CheckCircle2 size={18}/><span>{check.label}</span><strong>{check.ok?'PASS':'FAIL'}</strong></div>)}</section><section className="proof-block"><h3>Cloud provenance.</h3><div className="provenance-row"><span>COMPUTE PROVIDER</span><strong>Vultr Cloud Compute</strong></div><div className="provenance-row"><span>DATACENTER</span><strong>Amsterdam / ams</strong></div><div className="provenance-row"><span>RUNTIME</span><strong>Docker + Chromium</strong></div><div className="provenance-row"><span>MODEL SOURCE</span><strong>{mode==='live'?'Vultr Serverless Inference':'Scripted local fixture'}</strong></div><div className="provenance-row"><span>INSTANCE ID</span><code>{short(data.environment.instance_id,18)}…</code></div></section></div>
        <div className="evidence-disclosure"><CircleAlert size={19}/><div><strong>Read the limitation.</strong><p>These runs prove a constrained supplier-page scenario and a specific allowlist implementation. They are not a general jailbreak guarantee. Four blocked calls belong to the separate scripted fixture; the live LLM did not request them.</p></div></div>
        <button className="detail-link" onClick={()=>select('control')}><ArrowLeft size={18}/> BACK TO INTERACTIVE REPLAY</button></>:<div className="error-state"><p>{error||'Evidence unavailable'}</p><button onClick={onRefresh}>RETRY</button></div>}
      </main>}
      {section==='architecture'&&<main className="detail-content"><div className="eyebrow console-eyebrow"><span className="signal-bullet"/> RUNTIME ARCHITECTURE / VULTR</div><div className="detail-hero"><div><h1>Authority has <span>a boundary.</span></h1><p>BlastLab doesn't ask the model to be a firewall. It enforces a strict tool contract outside the model, inside a supervisor-owned execution path.</p></div><Layers3 size={88} strokeWidth={1}/></div>
        <div className="arch-map"><div className="arch-map-header"><span>SYSTEM MAP / TRUST DOMAINS</span><Pill tone="mint" dot>DEPLOYED ON VULTR</Pill></div><div className="architecture-stack"><div className="stack-node model-node"><div><span>EXTERNAL INFERENCE SERVICE</span><h3>Vultr Serverless Inference</h3><p>GLM-5.3 proposes structured actions through native tool calling. It has no Docker or host authority.</p></div><Zap size={35}/></div><div className="stack-route"><span>UNTRUSTED TOOL PROPOSAL</span><ArrowDownRight size={19}/></div><div className="stack-node policy-node"><div><span>TRUSTED SUPERVISOR / VULTR VM</span><h3>Capability policy + lifecycle</h3><p>Only GET /supplier and evidence-backed finish are authorized. The controller writes checkpoints, checks hashes and owns kill/reset.</p></div><ShieldCheck size={39}/></div><div className="stack-route stack-route-orange"><span>RESTRICTED CAPABILITIES ONLY</span><ArrowDownRight size={19}/></div><div className="stack-node sandbox-node"><div><span>ISOLATED WORKER / DOCKER</span><h3>Disposable Chromium chamber</h3><p>No outbound network, no host mounts, read-only root, dropped capabilities, non-root process, disposable workspace.</p></div><Box size={39}/></div></div><div className="arch-map-footer"><span>NO CLIENT-SIDE API CREDENTIALS</span><span>NO MODEL-EXECUTED SHELL</span><span>NO WORKER AUTHORITY OVER RESET</span></div></div>
        <div className="architecture-facts"><div><Tag>COMPUTE</Tag><h3>Vultr VM</h3><p>Ubuntu 24.04 · 2 vCPU / 4 GB · Amsterdam. The backend supervises isolated browser workers.</p></div><div><Tag>MODEL</Tag><h3>GLM-5.3</h3><p>Every genuine model call uses Vultr Serverless Inference. There is no shadow provider or silent fallback.</p></div><div><Tag>EVIDENCE</Tag><h3>SHA-256 chains</h3><p>Every event includes the preceding digest. Traces are checked against final result digests after execution.</p></div></div><div className="evidence-disclosure"><CircleAlert size={19}/><div><strong>What the boundary does not claim.</strong><p>The current test uses a deliberately constrained Chromium supplier route. This is a working vertical slice for proving capability isolation and recovery, not unrestricted website browsing or a production multi-tenant sandbox.</p></div></div>
        <button className="detail-link" onClick={()=>select('control')}><ArrowLeft size={18}/> RETURN TO THE EXECUTION TRACK</button>
      </main>}
      <footer className="console-footer"><span>BLASTLAB / AGENT CONTAINMENT TEST BENCH</span><span>BUILT ON VULTR · RECORDED NOV 2026</span></footer>
    </div>
    {modal&&<OperatorModal onClose={()=>setModal(false)} onDone={()=>{setRefresh(x=>x+1)}}/>}
  </div>;
}
export default function App(){return location.pathname==='/proof'?<ProofEngine/>:location.pathname==='/contained-sample'?<ContainedSample/>:location.pathname==='/judge-demo'?<JudgeDemo/>:location.pathname.startsWith('/app')?<ControlRoom/>:<Landing/>;}
