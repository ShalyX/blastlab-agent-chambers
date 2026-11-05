import {useEffect,useState} from 'react';
import {ArrowRight,ArrowUpRight, CheckCircle2, AlertTriangle, Fingerprint,Copy,
  Download,Server,ShieldAlert,ShieldCheck,TerminalSquare,RefreshCcw,LockKeyhole,Code2,
  CircleAlert,PlugZap,FlaskConical,Activity,ArrowLeft} from 'lucide-react';

type Created={
  session_id:string;join_token:string;expires_at:string;cases_total:number;
  source_type:string;connector:string
};
type AgentSummary={
  session_id:string;agent_name:string;status:string;completed:number;total:number;
  expires_at:string;source_type:string
};
type Finding={
  case_id:string;family:string;verdict:string;severity:string;reasons:string[];
  agent_answer:string;observed_tool_calls:{name:string,arguments:Record<string,unknown>}[];
  source_type:string;limits:string
};
type CampaignReport={
  session_id:string;agent_name:string;task:string;source_type:string;status:string;
  tests_completed:number;tests_total:number;breached:number;no_observed_violation:number;
  results:Finding[];mitigations:{case_id:string,trigger:string[],action:string,verify_fix:string}[];
  evidence:{format:string,root_sha256:string|null,events:unknown[]};
  manifest_sha256:string;limits:string
};
type ModePage='connect'|'campaign';

const attackCases=[
  {id:'01',title:'Clean control',type:'BASELINE',desc:'See the legitimate task without malicious instructions.'},
  {id:'02',title:'Role spoofing',type:'AUTHORITY',desc:'Fake system/developer instructions inside untrusted data.'},
  {id:'03',title:'Tool-output poisoning',type:'TOOLCHAIN',desc:'Malicious directions embedded in a fabricated tool result.'},
  {id:'04',title:'Forbidden tool request',type:'ACTION',desc:'Try to get the agent to propose a disallowed capability.'},
  {id:'05',title:'Decoy exfiltration',type:'DATA',desc:'Attempt a request to a non-routable collection endpoint.'},
  {id:'06',title:'Memory contamination',type:'PERSISTENCE',desc:'Try to install a malicious durable instruction.'}
];

async function jsonOrError(response:Response){
  const body=await response.json();
  if(!response.ok)throw new Error(body.error || ('Server returned '+response.status));
  return body;
}
function downloadJson(data:unknown,name:string){
  const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  const url=URL.createObjectURL(blob);
  const anchor=document.createElement('a');anchor.download=name;anchor.href=url;anchor.click();
  setTimeout(()=>URL.revokeObjectURL(url),900);
}
function Kicker({children}:{children:React.ReactNode}){
  return <span className="byoa-kicker"><i/> {children}</span>;
}

export function AgentLabConnect({onCreated,onDemo}:{
  onCreated:(created:Created)=>void;onDemo:()=>void
}){
  const [name,setName]=useState('');
  const [task,setTask]=useState('');
  const [tools,setTools]=useState('delete_file, send_http, write_memory');
  const [error,setError]=useState('');
  const [pending,setPending]=useState(false);
  const submit=async(event:React.FormEvent)=>{
    event.preventDefault();
    const forbidden_tools=tools.split(',').map(x=>x.trim()).filter(Boolean);
    setError('');setPending(true);
    try{
      const response=await fetch('/api/agent-lab/sessions',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({agent_name:name.trim(),task:task.trim(),forbidden_tools}),
      });
      const data=await jsonOrError(response) as Created;
      onCreated(data);
    }catch(e){setError(e instanceof Error?e.message:'Unable to create agent campaign')}
    finally{setPending(false)}
  };
  return <main className="ch-page byoa-page">
    <div className="ch-page-top"><Kicker>BLASTLAB / CONNECT YOUR AGENT</Kicker><span className="byoa-meta">ACTUAL AGENT REQUIRED</span></div>
    <div className="byoa-hero">
      <div className="byoa-intro"><span className="byoa-status"><PlugZap size={16}/> THE REAL PRODUCT</span>
        <h1>Bring your agent.<br/><em>We try to break it.</em></h1>
        <p>Connect an agent you actually built. We'll feed it controlled adversarial prompts and poisoned content, record the responses it really produces, and give you an evidence-based security report.</p>
        <div className="byoa-traits"><span><CheckCircle2 size={14}/> Your agent</span><span><ShieldAlert size={14}/> Six attack cases</span><span><Fingerprint size={14}/> Actual observations</span></div>
      </div>
      <div className="byoa-diagnostic" aria-label="Agent laboratory flow diagram">
        <div className="byoa-schematic-top"><span>BLASTLAB / EXTERNAL AGENT CONNECTOR</span><span>01 — 04</span></div>
        <div className="byoa-schematic-node byoa-node-agent"><PlugZap size={22}/><div><b>YOUR AGENT</b><small>OWNER-RUN / CONNECTED</small></div></div>
        <div className="byoa-schematic-wire"/><div className="byoa-schematic-impact"><ShieldAlert size={19}/><div><strong>ADVERSARIAL INPUT</strong><span>ROLES / TOOLS / DATA / MEMORY</span></div></div>
        <div className="byoa-schematic-wire"/><div className="byoa-schematic-node byoa-node-verdict"><Fingerprint size={22}/><div><b>OBSERVE → EVALUATE → FIX</b><small>REAL RESPONSES / REPRODUCIBLE REPORT</small></div></div>
        <div className="byoa-schematic-foot">NO AGENT API KEYS SENT TO BLASTLAB</div>
      </div>
    </div>

    <div className="byoa-workflow"><span className="active">01 CONNECT</span><span>02 ATTACK CAMPAIGN</span><span>03 RESULTS</span><span>04 RETEST</span></div>
    <div className="byoa-content">
      <form className="byoa-form" onSubmit={submit}>
        <div className="byoa-form-head"><div><Kicker>01 / CONNECT AGENT</Kicker><h2>Set the rules of engagement.</h2></div><span>NO SECRET KEYS REQUIRED</span></div>
        <label htmlFor="byoa-name">AGENT NAME</label>
        <input id="byoa-name" placeholder="e.g. Customer Support Agent" value={name} onChange={e=>setName(e.target.value)} minLength={2} maxLength={68} required/>
        <label htmlFor="byoa-task">LEGITIMATE TASK</label>
        <textarea id="byoa-task" placeholder="What must your agent accomplish? Include instructions it should protect against malicious page/tool content." value={task} onChange={e=>setTask(e.target.value)} minLength={10} maxLength={600} rows={4} required/>
        <label htmlFor="byoa-tools">FORBIDDEN TOOL NAMES <span>(COMMA SEPARATED)</span></label>
        <input id="byoa-tools" value={tools} onChange={e=>setTools(e.target.value)} placeholder="delete_file, send_http, write_memory" required/>
        <p className="byoa-field-note">BlastLab checks these exact forbidden tool names against observed actions your connector reports. Don't supply API keys, passwords or production secrets.</p>
        {error&&<div className="ch-inline-alert" role="alert"><CircleAlert size={17}/>{error}</div>}
        <button type="submit" className="ch-primary byoa-submit" disabled={pending}>
          {pending?<><RefreshCcw className="spinner" size={18}/> CREATING SECURE CAMPAIGN</>:<>CONNECT MY AGENT <ArrowUpRight size={20}/></>}
        </button>
      </form>
      <aside className="byoa-attack-panel">
        <Kicker>02 / ATTACK CAMPAIGN</Kicker>
        <h2>Six rounds.<br/><em>Real responses.</em></h2>
        <p>Attack prompts are lower-trust data. Your agent makes the decisions—not a script pretending to be your agent.</p>
        <div className="byoa-attack-list">{attackCases.map(item=><div key={item.id}><span>{item.id}</span><div><strong>{item.title}</strong><small>{item.desc}</small></div><em>{item.type}</em></div>)}</div>
        <div className="byoa-privacy"><LockKeyhole size={20}/><span>Your agent runs in your own environment. The outbound connector reports observed actions; the lab never executes them. This is not a VM attestation of your agent's runtime.</span></div>
      </aside>
    </div>
    <div className="byoa-demo-disclosure"><div><span>EXISTING INTERNAL EXPERIMENT</span><h3>Want to inspect the supplier test?</h3><p>The original $24/$72 supplier scenario has been preserved as a clearly labeled DEMO—not the BlastLab product or proof of testing your agent.</p></div><button className="ch-outline" onClick={onDemo}>OPEN SUPPLIER DEMO <ArrowRight size={17}/></button></div>
  </main>;
}

export function AgentLabCampaign({created,onNew}:{created:Created|null,onNew:()=>void}){
  const [state,setState]=useState<AgentSummary|null>(null);
  const [report,setReport]=useState<CampaignReport|null>(null);
  const [baseline,setBaseline]=useState<CampaignReport|null>(null);
  const [baselineError,setBaselineError]=useState('');
  const [error,setError]=useState('');
  const [copied,setCopied]=useState(false);
  const base=created?'/api/agent-lab/sessions/'+created.session_id:null;
  useEffect(()=>{
    if(!base||!created)return;
    let alive=true;
    const refresh=async()=>{
      try{
        const headers={'Authorization':'Bearer '+created.join_token};
        const summary=await jsonOrError(await fetch(base+'/status',{headers,cache:'no-store'})) as AgentSummary;
        if(!alive)return;
        setState(summary);setError('');
        if(summary.completed>0){
          const details=await jsonOrError(await fetch(base+'/report',{headers,cache:'no-store'})) as CampaignReport;
          if(alive)setReport(details);
        }
      }catch(e){if(alive)setError(e instanceof Error?e.message:'Unable to retrieve campaign status')}
    };
    refresh();const interval=window.setInterval(refresh,2500);
    return()=>{alive=false;window.clearInterval(interval)};
  },[base,created]);
  if(!created)return <main className="ch-page byoa-page"><Kicker>AGENT LAB / CAMPAIGN</Kicker><div className="byoa-empty"><PlugZap size={36}/><h1>No agent connected.</h1><p>Create an agent campaign first. This screen cannot substitute a supplier demo for a real user agent.</p><button className="ch-primary" onClick={onNew}>CONNECT AN AGENT <ArrowRight size={18}/></button></div></main>;
  const copy=async(value:string)=>{try{await navigator.clipboard.writeText(value);setCopied(true)}catch{setError('Clipboard unavailable; select the text manually')}};
  const done=state?.status==='complete';
  const importBaseline=async(event:React.ChangeEvent<HTMLInputElement>)=>{
    const file=event.target.files?.[0];
    event.target.value='';
    if(!file)return;
    setBaselineError('');
    try{
      if(file.size>500000)throw new Error('Report exceeds the 500 KB comparison limit.');
      const candidate=JSON.parse(await file.text()) as CampaignReport;
      if(!candidate || candidate.source_type!=='EXTERNAL_AGENT_RUNNER_REPORTED' ||
        !Array.isArray(candidate.results) || candidate.results.length!==created.cases_total ||
        candidate.results.some(item=>!item || typeof item.case_id!=='string' || typeof item.verdict!=='string')){
        throw new Error('This is not a complete BlastLab external-agent campaign report.');
      }
      if(!report || candidate.agent_name!==report.agent_name || candidate.task!==report.task ||
        report.results.some(item=>!candidate.results.some(previous=>previous.case_id===item.case_id))){
        throw new Error('Use a previous report for the same agent, task and six attack cases.');
      }
      setBaseline(candidate);
    }catch(e){
      setBaseline(null);
      setBaselineError(e instanceof Error?e.message:'Unable to import the baseline report.');
    }
  };
  const compared=report&&baseline?report.results.map(current=>({
    ...current,previous:baseline.results.find(item=>item.case_id===current.case_id)!
  })):[];
  const resolved=compared.filter(item=>item.previous.verdict==='BREACHED'&&item.verdict!=='BREACHED').length;
  const regressions=compared.filter(item=>item.previous.verdict!=='BREACHED'&&item.verdict==='BREACHED').length;
  return <main className="ch-page byoa-page">
    <div className="ch-page-top"><Kicker>BLASTLAB / LIVE AGENT CAMPAIGN</Kicker><span className="byoa-meta">{state?.completed||0} / {created.cases_total} CASES</span></div>
    <div className="byoa-campaign-hero"><div><span className="byoa-status"><Activity size={16}/>{done?'CAMPAIGN COMPLETED':'AWAITING YOUR AGENT RUNNER'}</span>
      <h1>{done?'The agent has been tested.':"Campaign created."}<br/><em>{done?'Here is what it did.':'Now run your agent.'}</em></h1><p>Campaign ID <code>{created.session_id}</code>. Your agent is not connected until its local connector starts. It runs in your own environment. BlastLab observes only the responses and proposed tools your connector submits.</p>
      </div><div className="byoa-progress"><strong>{state?.completed||0}<span>/{created.cases_total}</span></strong><small>CASES RECEIVED</small><div><i style={{width:(100*(state?.completed||0)/created.cases_total)+'%'}}/></div></div></div>
    {!done&&<div className="byoa-connection-grid">
      <section className="byoa-connection-panel"><Kicker>CONNECTOR / STEP ONE</Kicker><h2>Download the Python connector.</h2><p>It calls a Python function you own, passes the attack as untrusted input, and sends the agent's actual output and tool intents back to this campaign.</p><a className="ch-primary" href="/connect/blastlab_connector.py" download><Download size={17}/> DOWNLOAD CONNECTOR</a><a className="byoa-inline-link" href="https://github.com/ShalyX/blastlab-agent-chambers/tree/master/examples" target="_blank" rel="noreferrer">View example agent adapters <ArrowUpRight size={15}/></a></section>
      <section className="byoa-connection-panel"><Kicker>CONNECTOR / STEP TWO</Kicker><h2>Run your own agent.</h2><p>Expose <code>respond(case)</code> in your Python agent module. Set the one-time session token locally and launch the connector.</p>
        <label>ONE-TIME JOIN TOKEN</label><div className="byoa-token"><code>{created.join_token}</code><button onClick={()=>copy(created.join_token)}><Copy size={16}/></button></div>
        <label>TERMINAL COMMAND</label><pre>python blastlab_connector.py --session {created.session_id} --adapter your_agent:respond</pre><p className="byoa-command-note">Set <code>BLASTLAB_SESSION_TOKEN</code> to the token above in your local terminal. Do not commit it, paste real API keys, or execute unrestricted tools during tests. Expires {new Date(created.expires_at).toLocaleString()}.</p>
      </section>
    </div>}
    {error&&<div className="ch-inline-alert" role="status">{error}</div>}
    {state&&!done&&<div className="byoa-waiting"><RefreshCcw className="spinner" size={17}/>{state.completed?'AGENT RESPONSES ARRIVING':'WAITING FOR AN OUTBOUND AGENT CONNECTION'}<span>Updates from the actual connected runner, not fabricated progress.</span></div>}
    {report&&<div className="byoa-report">
      <div className="byoa-report-header"><div><Kicker>03 / OBSERVED VERDICTS</Kicker><h2>{report.breached} observed <em>rule violation{report.breached===1?'':'s'}.</em></h2><p>{report.tests_completed} of {report.tests_total} controlled cases submitted. The verdict is based on the connected agent's reported decisions.</p></div><button className="ch-outline" onClick={()=>downloadJson(report,'blastlab-agent-'+created.session_id+'.json')}><Download size={16}/> EXPORT REPORT</button></div>
      <div className="byoa-report-kpis"><div><small>TESTED</small><b>{report.tests_completed}</b></div><div><small>VIOLATIONS</small><b className="byoa-danger">{report.breached}</b></div><div><small>NO VIOLATION OBSERVED</small><b>{report.no_observed_violation}</b></div><div><small>PROVENANCE</small><b className="byoa-small-value">RUNNER-REPORTED</b></div></div>
      {done&&<section className="byoa-comparison" aria-label="Compare before and after agent campaigns">
        <div><Kicker>04 / BEFORE & AFTER</Kicker><h2>Did the fix hold?</h2>
          <p>Export the first campaign, change your agent, run the same task again, then import the earlier report here. Comparison stays in your browser; no extra upload to BlastLab.</p>
          <label className="ch-outline byoa-compare-upload" htmlFor="byoa-baseline-file"><Download size={16}/> IMPORT PREVIOUS REPORT</label>
          <input id="byoa-baseline-file" type="file" accept=".json,application/json" onChange={importBaseline} className="byoa-file-input" />
          {baselineError&&<p role="alert" className="byoa-comparison-error">{baselineError}</p>}
        </div>
        {baseline&&<div className="byoa-compare-results">
          <div className="byoa-compare-totals"><span>BEFORE <strong>{baseline.breached} breaches</strong></span><ArrowRight size={20}/><span>AFTER <strong>{report.breached} breaches</strong></span></div>
          <div className="byoa-compare-totals"><span>RESOLVED <strong>{resolved}</strong></span><span>NEW BREACHES <strong>{regressions}</strong></span></div>
          <div className="byoa-compare-cases">{compared.map(item=><div key={item.case_id}><code>{item.case_id}</code><span>{item.previous.verdict.replaceAll('_',' ')} → {item.verdict.replaceAll('_',' ')}</span></div>)}</div>
          <p>Runner-reported comparison, not independent proof. Keep the task, forbidden-tool policy and connector implementation consistent across both runs.</p>
        </div>}
      </section>}
      <div className="byoa-findings">{report.results.map(item=><article key={item.case_id} className="byoa-finding">
        <div className="byoa-finding-top"><span>{item.family.toUpperCase()}</span><span className={item.verdict==='BREACHED'?'byoa-failed':'byoa-resisted'}>{item.verdict.replaceAll('_',' ')}</span></div>
        <h3>{item.case_id.replaceAll('_',' ')}</h3><p>{item.reasons.length?item.reasons.join('; '):'No matching forbidden action or attacker marker was observed in the submitted response.'}</p>
        <div className="byoa-observation"><span>ACTUAL RUNNER-REPORTED RESPONSE</span><code>{item.agent_answer.slice(0,500)||'(no answer)'}</code><small>{item.observed_tool_calls.length} observed/proposed tool call(s)</small></div>
      </article>)}</div>
      <div className="byoa-remediations"><Kicker>04 / MITIGATE & RETEST</Kicker><h2>Turn failures into fixes.</h2>
        {report.mitigations.length?report.mitigations.map(fix=><div key={fix.case_id}><span>{fix.case_id.toUpperCase()}</span><p>{fix.action}</p><small>{fix.verify_fix}</small></div>):<p>No matching attack rule was violated in these six reported cases. This does not prove the agent is generally secure; test additional inputs and verify task success independently.</p>}
        <button className="ch-primary" onClick={onNew}>RETEST YOUR UPDATED AGENT <ArrowUpRight size={18}/></button>
      </div>
      <div className="byoa-evidence-note"><Fingerprint size={22}/><div><strong>Evidence integrity, not source attestation.</strong><p>This report contains a SHA-256 chain and a full-report manifest for internal consistency. The agent responses came from a user-operated connector, not a Vultr-attested runtime. A user with control of the connector can misreport them; the lab does not claim otherwise.</p><code>{report.manifest_sha256}</code></div></div>
    </div>}
  </main>;
}
