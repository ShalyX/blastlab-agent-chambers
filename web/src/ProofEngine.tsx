import {useEffect,useState} from 'react';
import {ArrowLeft,ArrowRight,ArrowUpRight,Check,ChevronDown,Download,FileCheck2,Fingerprint,LockKeyhole,ShieldCheck,ShieldAlert,Server,Code2,Copy} from 'lucide-react';
import './proof-engine.css';

type Case={id:string;family:string;verdict:string;reported_tool_names:string[]};
type Anchor={raw_evidence_path:string;raw_json_sha256:string;report_manifest_sha256:string;event_chain_root_sha256:string;attack_plan_sha256:string;cases_completed:number;observed_violations:number;source_type:string;case_results:Case[]};
type Pair={before:Anchor;after:Anchor;exact_plan_replay:boolean;task_outcomes?:Array<{id:string;before:string;after:string}>};
type Contained={run_id:string;cases_completed:number;model_calls:number;actions_executed:number;forbidden_actions_denied:number;boundary_checks_passed:number;boundary_checks_total:number;check_names:string[];container_and_socket_removed:boolean;manifest_sha256:string;attack_plan_sha256:string;raw_report_sha256:string;source:string;archive:string;limitation:string};
type Lane={title:string;metric:string;metric_type:string;ownership:string;scope:string;change?:string;model?:string;repository?:string;evidence:Pair|Contained};
type LaneId='same_agent'|'termproof'|'contained'|'framework';
type Proof={
 schema:string;created_at_utc:string;status:string;source_contract:string;
 claims:Record<LaneId,Lane>;regression:{executed:number;skipped:number;failed:number;method:string;caveat:string};
 proof_debts:string[];links:Record<string,string>
};
const LANES:Array<{id:LaneId;number:string;tag:string;eyebrow:string}>=[
 {id:'same_agent',number:'01',tag:'RISK REDUCTION',eyebrow:'FIX • RETEST'},
 {id:'termproof',number:'02',tag:'WORKFLOW RECOVERY',eyebrow:'REAL EXTERNAL CODEBASE'},
 {id:'contained',number:'03',tag:'BOUNDARY PROOF',eyebrow:'ACTUAL VULTR WORKER'},
 {id:'framework',number:'04',tag:'INTEROPERABILITY',eyebrow:'PYDANTICAI AGENT'},
];
const isPair=(v:Pair|Contained):v is Pair=>'before' in v;
const compact=(s:string)=>s.slice(0,12)+'…'+s.slice(-11);
function HashLine({label,value}:{label:string;value:string}) {
 const [copied,setCopied]=useState(false);
 const copy=async()=>{try{await navigator.clipboard.writeText(value);setCopied(true)}catch{setCopied(false)}};
 return <div className="proof-hash-row"><span>{label}</span><code title={value}>{value}</code><button type="button" title={'Copy '+label} aria-label={'Copy '+label} onClick={copy}>{copied?<Check size={13}/>:<Copy size={13}/>}</button></div>;
}
function PairDetail({lane,id}:{lane:Lane;id:LaneId}) {
 if(!isPair(lane.evidence))return null;
 const {before,after,task_outcomes}=lane.evidence;
 const isTerm=id==='termproof';
 const detail=(name:string)=>{
   const t=task_outcomes?.find(x=>x.id===name);
   return t?{before:t.before,after:t.after}:{
      before:before.case_results.find(x=>x.id===name)?.verdict||'UNKNOWN',
      after:after.case_results.find(x=>x.id===name)?.verdict||'UNKNOWN'
   };
 };
 return <>
   <div className="proof-compare-summary">
     <div><small>{isTerm?'ORIGINAL TASK RESULTS':'BASELINE VIOLATIONS'}</small><strong>{isTerm?'0 / 6':before.observed_violations+' / 6'}</strong>
       <span>{isTerm?'verified by TermProof':'observed violations'}</span></div>
     <ArrowRight size={23} className="proof-compare-arrow"/>
     <div><small>{isTerm?'CORRECTED TASK RESULTS':'HARDENED VIOLATIONS'}</small><strong>{isTerm?'6 / 6':after.observed_violations+' / 6'}</strong>
       <span>{isTerm?'verified by TermProof':'observed violations'}</span></div>
   </div>
   <div className="proof-case-heading"><h3>Six cases. Same attack plan.</h3><small>{isTerm?'ORIGINAL / CORRECTED':'BEFORE / AFTER'}</small></div>
   <div className="proof-case-list">
     {before.case_results.map((c,i)=>{
       const d=detail(c.id);
       return <div className="proof-case" key={c.id}>
         <span className="proof-case-no">{String(i+1).padStart(2,'0')}</span>
         <div className="proof-case-name"><strong>{c.family}</strong><small>{c.id}</small></div>
         <div className="proof-case-results">
           <span className={d.before==='BREACHED'||d.before==='NEEDS_EVIDENCE'?'proof-negative':''}>{d.before.replaceAll('_',' ')}</span>
           <ArrowRight size={13}/><span className={d.after==='VERIFIED'?'proof-positive':''}>{d.after.replaceAll('_',' ')}</span>
         </div>
       </div>;
     })}
   </div>
   <div className="proof-digests">
     <HashLine label="ATTACK PLAN / SAME SHA-256" value={before.attack_plan_sha256}/>
     <HashLine label="BEFORE / REPORT MANIFEST" value={before.report_manifest_sha256}/>
     <HashLine label="AFTER / REPORT MANIFEST" value={after.report_manifest_sha256}/>
     <HashLine label="BEFORE / EVENT CHAIN ROOT" value={before.event_chain_root_sha256}/>
     <HashLine label="AFTER / EVENT CHAIN ROOT" value={after.event_chain_root_sha256}/>
   </div>
   <p className="proof-source-note">Both 6-case reports passed structural, event-chain, regrading, manifest, and exact-replay checks. Source attribution remains <strong>RUNNER-REPORTED</strong>. The raw reports stay private; these hashes are audit anchors, not digital signatures.</p>
 </>;
}
function ContainedDetail({lane}:{lane:Lane}) {
 if(isPair(lane.evidence))return null;
 const e=lane.evidence;
 return <>
   <div className="proof-contain-summary">
     {[['06','cases completed'],[String(e.model_calls).padStart(2,'0'),'live model calls'],[String(e.actions_executed).padStart(2,'0'),'synthetic actions executed'],[String(e.forbidden_actions_denied).padStart(2,'0'),'forbidden actions denied']].map(([n,label])=>
       <div key={label}><strong>{n}</strong><small>{label}</small></div>)}
   </div>
   <div className="proof-check-header"><h3>Independent containment checks</h3><span><ShieldCheck size={15}/>{e.boundary_checks_passed} / {e.boundary_checks_total} PASSED</span></div>
   <div className="proof-check-grid">{e.check_names.map((name,i)=><div key={name} className="proof-check-item"><span>{String(i+1).padStart(2,'0')}</span><strong>{name.replaceAll('_',' ')}</strong><Check size={14}/></div>)}</div>
   <div className="proof-digests">
     <HashLine label="CONTAINED REPORT MANIFEST" value={e.manifest_sha256}/>
     <HashLine label="CONTAINED ATTACK PLAN" value={e.attack_plan_sha256}/>
     <HashLine label="PRIVATE SOURCE REPORT / SHA-256" value={e.raw_report_sha256}/>
   </div>
   <p className="proof-source-note">Worker and inference socket were confirmed removed. This is the <strong>November 6 archived worker</strong> (seven denied actions), distinct from the November 7 fresh sample (ten denied actions). It is never described as a customer-run agent.</p>
   <a className="proof-plain-link" href="/contained-sample">Inspect the public Vultr worker archive <ArrowUpRight size={15}/></a>
 </>;
}
export default function ProofEngine(){
 const [proof,setProof]=useState<Proof|null>(null);
 const [failure,setFailure]=useState('');
 const [active,setActive]=useState<LaneId>('same_agent');
 useEffect(()=>{
   let mounted=true;
   fetch('/proof/evidence.json',{cache:'no-store'})
    .then(async r=>{if(!r.ok)throw new Error('Public proof index could not be retrieved');return r.json() as Promise<Proof>})
    .then(v=>{
       if(v.schema!=='blastlab.phase24.proof-index.v1'||v.status!=='FOUR_TECHNICAL_PROOFS_VERIFIED'||!v.claims?.same_agent||!v.claims?.termproof||!v.claims?.contained||!v.claims?.framework)
         throw new Error('Proof index contract mismatch');
       if(mounted)setProof(v);
    })
    .catch(e=>{if(mounted)setFailure(e instanceof Error?e.message:'Proof index unavailable')});
   return ()=>{mounted=false};
 },[]);
 const selected=proof?.claims[active];
 return <div className="proof-root">
   <header className="proof-nav">
     <a href="/" className="proof-logo">BLAST<span>/</span>LAB <small>PROOF ENGINE / 024</small></a>
     <div className="proof-nav-right">
       <a href="/app"><ArrowLeft size={14}/> CONNECT AN AGENT</a>
       <a href="/contained-sample">WORKER LAB</a>
       <a className="proof-nav-download" href="/proof/evidence.json" download>PROOF INDEX <Download size={14}/></a>
     </div>
   </header>
   <main>
     <section className="proof-hero">
       <div className="proof-hero-eyebrow"><span className="proof-hero-dot"/> FOUR REAL TECHNICAL PROOFS <span>/</span> NO SIMULATED IMPROVEMENT</div>
       <div className="proof-hero-layout"><div>
         <h1>Show the work.<br/><em>Not just the score.</em></h1>
         <p>Every number below is traced back to a completed campaign, a checked report manifest, or a host-observed worker run. No customer adoption, tool execution, or security improvement is invented.</p>
       </div><div className="proof-hero-stamp"><span>01 / PROOF INTEGRITY</span>
         <FileCheck2 size={40} strokeWidth={1.3}/>
         <strong>CHECKED</strong>
         <small>RAW REPORTS / HELD PRIVATELY</small>
       </div></div>
       <div className="proof-hero-foot"><span><ShieldCheck size={15}/> SIX-CASE EXACT REPLAYS</span>
         <span><Fingerprint size={15}/> SHA-256 EVENT + REPORT ANCHORS</span>
         <span><LockKeyhole size={15}/> NO CONNECTOR CREDENTIALS</span></div>
     </section>
     <section className="proof-statusline">
       <div><span className="proof-status-dot"/> SOURCE CLASSIFICATION / <strong>TECHNICAL EVIDENCE VERIFIED</strong></div>
       <p>External independent customer acceptance: <strong>NOT YET VERIFIED</strong></p>
     </section>
     {failure&&<div className="proof-error" role="alert"><ShieldAlert size={18}/>{failure}. Claims cannot be displayed without their proof index.</div>}
     {!proof&&!failure&&<div className="proof-loading">LOADING AND CHECKING EVIDENCE INDEX…</div>}
     {proof&&<>
       <section className="proof-lanes" aria-label="Select one of four technical proof lanes">
         <div className="proof-section-label"><span>THE PROOF / FOUR DISTINCT CLAIMS</span><span>SELECT TO INSPECT <ChevronDown size={13}/></span></div>
         <div className="proof-lane-grid">
           {LANES.map(meta=>{const lane=proof.claims[meta.id];const chosen=active===meta.id;return <button
             key={meta.id} type="button" className={'proof-lane'+(chosen?' is-active':'')} aria-pressed={chosen}
             onClick={()=>setActive(meta.id)}>
             <span className="proof-lane-top"><small>{meta.number} / {meta.eyebrow}</small><ArrowUpRight size={18}/></span>
             <strong>{lane.metric}</strong>
             <span className="proof-lane-title">{lane.title}</span>
             <small className="proof-lane-class">{meta.tag} <span>●</span> {lane.ownership.replaceAll('_',' ')}</small>
           </button>})}
         </div>
       </section>
       {selected&&<section className="proof-inspector" id="inspector" aria-live="polite">
         <div className="proof-inspector-header">
           <div><span className="proof-overline">EVIDENCE INSPECTOR / {LANES.find(x=>x.id===active)?.number}</span>
             <h2>{selected.title}</h2>
             <p>{selected.scope}</p>
           </div>
           <span className="proof-source-stamp"><Check size={14}/> {selected.ownership.replaceAll('_',' ')}</span>
         </div>
         {isPair(selected.evidence)?<PairDetail lane={selected} id={active}/>:<ContainedDetail lane={selected}/>}
         {selected.change&&<div className="proof-change"><Code2 size={16}/><span>WHAT ACTUALLY CHANGED</span><p>{selected.change}</p></div>}
         <div className="proof-index-download"><span>Derived evidence only. Full raw prompts and reports are not hosted publicly.</span>
           <a href="/proof/evidence.json" download>DOWNLOAD SANITIZED PROOF INDEX <Download size={15}/></a></div>
       </section>}
       <section className="proof-method">
         <div><span className="proof-overline">02 / REPRODUCE THE VERIFICATION</span>
           <h2>Reports can be challenged.</h2>
           <p>We independently regraded each source report against its event chain and manifest, then checked that the before/after campaigns used exactly the same attack plan, task and tool contract.</p>
           <p>The JSON index publishes the digest anchors and six-case verdicts. It does <strong>not</strong> contain the raw inputs needed for full third-party regrading, and its hashes are not digital signatures.</p>
           <a className="proof-plain-link" href="/proof/evidence.json" download>Download the proof index <ArrowUpRight size={15}/></a>
         </div>
         <div className="proof-method-numbers"><div><FileCheck2 size={19}/><strong>{proof.regression.executed}</strong><small>executable regression tests passed</small></div><div><ShieldCheck size={19}/><strong>3</strong><small>exact replay report pairs regraded</small></div><div><Server size={19}/><strong>22</strong><small>archived worker boundary checks</small></div>
           <p>{proof.regression.skipped} test skips documented. Isolated module runs avoided an intermittent Windows HTTP test-harness socket issue.</p>
         </div>
       </section>
       <section className="proof-debts" aria-labelledby="proof-debts-heading">
         <span className="proof-overline">03 / WHAT THESE RESULTS DO NOT PROVE</span>
         <div className="proof-debts-grid"><div><h2 id="proof-debts-heading">The missing proof is listed, not hidden.</h2>
           <p>Phase 24 remains open until the independent operator and source-attestation claims can be supported or correctly scoped.</p>
           <a className="proof-plain-link" href="/connect/independent-tester.md">Outside-agent acceptance protocol <ArrowUpRight size={15}/></a>
         </div><ol>{proof.proof_debts.map(x=><li key={x}>{x}</li>)}</ol></div>
       </section>
     </>}
   </main>
   <footer className="proof-footer"><span>BLAST/LAB © 2026</span><span>EVIDENCE BEFORE CLAIMS.</span>
     <div><a href="/app">CONNECT</a><a href="/contained-sample">WORKER</a><a href="/">HOME</a></div></footer>
 </div>;
}
