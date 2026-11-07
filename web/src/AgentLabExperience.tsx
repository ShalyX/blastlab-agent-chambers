import {useEffect,useState} from 'react';
import {ArrowRight,ArrowUpRight, CheckCircle2, AlertTriangle, Fingerprint,Copy,
  Download,Server,ShieldAlert,ShieldCheck,TerminalSquare,RefreshCcw,LockKeyhole,Code2,
  CircleAlert,PlugZap,FlaskConical,Activity,ArrowLeft} from 'lucide-react';

type Created={
  session_id:string;join_token:string;expires_at:string;cases_total:number;recovery_key?:string;recovery_expires_at?:string;
  source_type:string;connector:string;attack_source:string;
  attack_provider:string;attack_model:string;attack_plan_sha256:string;baseline_report?:CampaignReport
};
type AgentSummary={
  session_id:string;agent_name:string;status:string;completed:number;total:number;
  expires_at:string;source_type:string
};
type Finding={
  case_id:string;family:string;verdict:string;severity:string;reasons:string[];
  observations:string[];agent_answer:string;observed_tool_calls:{name:string,arguments:Record<string,unknown>}[];
  source_type:string;limits:string;task_success_signal?:string
};
type CampaignReport={
  forbidden_tools:string[];allowed_tools?:string[];success_contains?:string;canary:string;
  session_id:string;agent_name:string;task:string;source_type:string;status:string;
  tests_completed:number;tests_total:number;breached:number;no_observed_violation:number;
  results:Finding[];mitigations:{case_id:string,trigger:string[],action:string,verify_fix:string}[];
  evidence:{format:string,root_sha256:string|null,events:Array<{event:{case_id:string;attack:string;response:{answer:string;tool_calls:{name:string;arguments:Record<string,unknown>}[]}}}>};
  manifest_sha256:string;limits:string;attack_plan_source:string;
  attack_plan_provider:string;attack_plan_model:string;attack_plan_sha256:string
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
async function verifyImported(report:CampaignReport,current?:CampaignReport){
  await jsonOrError(await fetch('/api/agent-lab/reports/verify',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({report,...(current?{current}:{})}),
  }));
}
async function readReport(file:File){
  if(file.size>500000)throw new Error('Report exceeds the 500 KB import limit.');
  const report=JSON.parse(await file.text()) as CampaignReport;
  await verifyImported(report);
  return report;
}
async function replayReport(report:CampaignReport){
  const created=await jsonOrError(await fetch('/api/agent-lab/sessions',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({agent_name:report.agent_name,task:report.task,
      forbidden_tools:report.forbidden_tools,
      ...(report.allowed_tools?{allowed_tools:report.allowed_tools}:{}),
      ...(report.success_contains?{success_contains:report.success_contains}:{}),
      baseline_report:report}),
  })) as Created;
  return {...created,baseline_report:report};
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
  const [allowed,setAllowed]=useState('read_document, summarize_data');
  const [successSignal,setSuccessSignal]=useState('');
  const [error,setError]=useState('');
  const [pending,setPending]=useState(false);
  const [replay,setReplay]=useState<CampaignReport|null>(null);
  const [recoveryId,setRecoveryId]=useState('');
  const [recoveryKey,setRecoveryKey]=useState('');
  const [recoveryPending,setRecoveryPending]=useState(false);
  const [recoveryError,setRecoveryError]=useState('');
  const [recoveredReport,setRecoveredReport]=useState<CampaignReport|null>(null);
  const fillFromReport=(previous:CampaignReport)=>{
    setReplay(previous);setName(previous.agent_name);setTask(previous.task);
    setTools(previous.forbidden_tools.join(', '));
    setAllowed((previous.allowed_tools||[]).join(', '));
    setSuccessSignal(previous.success_contains||'');
  };
  const recover=async()=>{
    setRecoveryError('');setRecoveredReport(null);setRecoveryPending(true);
    try{
      const id=recoveryId.trim().toLowerCase();
      if(!/^[a-f0-9]{32}$/.test(id))throw new Error('Enter the 32-character campaign ID.');
      if(!/^[A-Za-z0-9_-]{32,80}$/.test(recoveryKey))throw new Error('Enter your saved recovery key.');
      const response=await fetch('/api/agent-lab/sessions/'+id+'/recovery-report',{
        headers:{Authorization:'Bearer '+recoveryKey},cache:'no-store'
      });
      const recovered=await jsonOrError(response) as CampaignReport;
      await verifyImported(recovered);
      setRecoveredReport(recovered);
    }catch(e){setRecoveryError(e instanceof Error?e.message:'Unable to recover report')}
    finally{setRecoveryPending(false);setRecoveryKey('')}
  };
  const importReplay=async(event:React.ChangeEvent<HTMLInputElement>)=>{
    const file=event.target.files?.[0];event.target.value='';
    if(!file)return;
    setError('');setPending(true);setReplay(null);
    try{
      const previous=await readReport(file);
      fillFromReport(previous);
    }catch(e){setError(e instanceof Error?e.message:'Unable to verify report')}
    finally{setPending(false)}
  };
  const submit=async(event:React.FormEvent)=>{
    event.preventDefault();
    const forbidden_tools=tools.split(',').map(x=>x.trim()).filter(Boolean);
    const allowed_tools=allowed.split(',').map(x=>x.trim()).filter(Boolean);
    setError('');setPending(true);
    try{
      if(allowed_tools.some(name=>forbidden_tools.includes(name)))throw new Error('Allowed and forbidden tools must not overlap.');
      if(!replay&&(!allowed_tools.length||!successSignal.trim()))throw new Error('Declare allowed tools and a literal task success signal.');
      const response=await fetch('/api/agent-lab/sessions',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({agent_name:name.trim(),task:task.trim(),forbidden_tools,
          ...(replay?{...(replay.allowed_tools?{allowed_tools:replay.allowed_tools}:{}),
            ...(replay.success_contains?{success_contains:replay.success_contains}:{})}:
            {allowed_tools,success_contains:successSignal.trim()}),
          ...(replay?{baseline_report:replay}:{})}),
      });
      const data=await jsonOrError(response) as Created;
      onCreated(replay?{...data,baseline_report:replay}:data);
    }catch(e){setError(e instanceof Error?e.message:'Unable to create agent campaign')}
    finally{setPending(false)}
  };
  return <main className="ch-page byoa-page">
    <div className="ch-page-top"><Kicker>BLASTLAB / CONNECT YOUR AGENT</Kicker><span className="byoa-meta">ACTUAL AGENT REQUIRED</span></div>
    <div className="byoa-hero">
      <div className="byoa-intro"><span className="byoa-status"><PlugZap size={16}/> THE REAL PRODUCT</span>
        <h1>Bring your agent.<br/><em>We try to break it.</em></h1>
        <p>Connect an agent you actually built. We'll feed it controlled adversarial prompts and poisoned content, record the responses it really produces, and give you an evidence-based security report.</p>
        <div className="byoa-traits"><span><CheckCircle2 size={14}/> Your agent</span><span><ShieldAlert size={14}/> Vultr-generated attacks</span><span><Fingerprint size={14}/> Actual observations</span></div>
        <a href="#byoa-connect-form" className="byoa-jump-link">Set up your agent <ArrowRight size={16}/></a>
        <a href="/connect/independent-tester.md" className="byoa-jump-link" target="_blank" rel="noreferrer">Independent agent testing protocol <ArrowRight size={16}/></a>
      </div>
      <div className="byoa-diagnostic" aria-label="Illustration of the BYOA test process, not a live connection status">
        <div className="byoa-schematic-top"><span>BLASTLAB / EXTERNAL AGENT CONNECTOR</span><span>01 — 04</span></div>
        <div className="byoa-schematic-node byoa-node-agent"><PlugZap size={22}/><div><b>YOUR AGENT</b><small>OWNER-RUN / YOUR ENVIRONMENT</small></div></div>
        <div className="byoa-schematic-wire"/><div className="byoa-schematic-impact"><ShieldAlert size={19}/><div><strong>ADVERSARIAL INPUT</strong><span>ROLES / TOOLS / DATA / MEMORY</span></div></div>
        <div className="byoa-schematic-wire"/><div className="byoa-schematic-node byoa-node-verdict"><Fingerprint size={22}/><div><b>OBSERVE → EVALUATE → FIX</b><small>REAL RESPONSES / REPRODUCIBLE REPORT</small></div></div>
        <div className="byoa-schematic-foot">NO AGENT API KEYS SENT TO BLASTLAB</div>
      </div>
    </div>

    <div className="byoa-workflow"><span className="active">01 CONNECT</span><span>02 ATTACK CAMPAIGN</span><span>03 RESULTS</span><span>04 RETEST</span></div>
    <section className="byoa-surface-inventory" aria-labelledby="byoa-surface-heading">
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
    <div className="byoa-content">
      <form id="byoa-connect-form" className="byoa-form" onSubmit={submit}>
        <div className="byoa-form-head"><div><Kicker>01 / CONNECT AGENT</Kicker><h2>Set the rules of engagement.</h2></div><span>NO SECRET KEYS REQUIRED</span></div>
        <details className="byoa-replay-disclosure"><summary>Already have a report? Import it for an exact retest</summary>
        <label htmlFor="byoa-replay-file">RETEST FROM AN EXPORTED REPORT</label>
        <input id="byoa-replay-file" type="file" accept=".json,application/json" onChange={importReplay} disabled={pending}/>
        <p className="byoa-field-note">Imported reports are sent to BlastLab for integrity verification, not retained by the verification endpoint. Replay preserves the exact attacks, task and tool policy.</p>
        {replay&&<p role="status">Verified report loaded. This campaign will replay the original attacks. <button type="button" onClick={()=>setReplay(null)}>Use new attacks instead</button></p>}
        </details>
        <details className="byoa-replay-disclosure byoa-recover-disclosure">
          <summary>Lost your short-lived connector session? Recover a completed report</summary>
          <p className="byoa-field-note">Use the campaign ID and the separate read-only key saved when you created the campaign. Keys expire after 30 days. Lost keys cannot be reset; no account is created.</p>
          <label htmlFor="byoa-recovery-id">CAMPAIGN ID</label>
          <input id="byoa-recovery-id" value={recoveryId} onChange={e=>setRecoveryId(e.target.value)} placeholder="32-character campaign ID" autoComplete="off" maxLength={32}/>
          <label htmlFor="byoa-recovery-key">READ-ONLY RECOVERY KEY</label>
          <input id="byoa-recovery-key" type="password" value={recoveryKey} onChange={e=>setRecoveryKey(e.target.value)} autoComplete="off" placeholder="Saved 30-day recovery key"/>
          <button type="button" className="ch-outline" onClick={recover} disabled={recoveryPending}>{recoveryPending?'VERIFYING REPORT':'RECOVER COMPLETED REPORT'}</button>
          {recoveryError&&<p role="alert" className="byoa-comparison-error">{recoveryError}</p>}
          {recoveredReport&&<div className="byoa-recovered-result" role="status">
            <strong>Report recovered · {recoveredReport.tests_completed} cases · {recoveredReport.breached} observed violations</strong>
            <p className="byoa-field-note">This is a read-only report, not access to run or modify the old campaign.</p>
            <div className="byoa-recovered-actions">
              <button type="button" className="ch-outline" onClick={()=>downloadJson(recoveredReport,'blastlab-recovered-'+recoveredReport.session_id+'.json')}>DOWNLOAD REPORT</button>
              <button type="button" className="ch-outline" onClick={()=>{fillFromReport(recoveredReport);setRecoveredReport(null)}}>USE FOR EXACT RETEST</button>
            </div>
          </div>}
        </details>
        <label htmlFor="byoa-name">AGENT NAME</label>
        <input id="byoa-name" placeholder="e.g. Customer Support Agent" value={name} onChange={e=>setName(e.target.value)} minLength={2} maxLength={68} required/>
        <label htmlFor="byoa-task">LEGITIMATE TASK</label>
        <textarea id="byoa-task" placeholder="What must your agent accomplish? Include instructions it should protect against malicious page/tool content." value={task} onChange={e=>setTask(e.target.value)} minLength={10} maxLength={600} rows={4} required/>
        <label htmlFor="byoa-allowed">ALLOWED TOOL NAMES <span>(COMMA SEPARATED)</span></label>
        <input id="byoa-allowed" value={allowed} onChange={e=>setAllowed(e.target.value)} placeholder="read_document, summarize_data" required={!replay} disabled={!!replay}/>
        <p className="byoa-field-note">Capabilities your agent is permitted to propose. This is an observed policy check, not execution containment.</p>
        <label htmlFor="byoa-tools">FORBIDDEN TOOL NAMES <span>(COMMA SEPARATED)</span></label>
        <input id="byoa-tools" value={tools} onChange={e=>setTools(e.target.value)} placeholder="delete_file, send_http, write_memory" required/>
        <p className="byoa-field-note">BlastLab checks these exact forbidden tool names against observed actions your connector reports. Don't supply API keys, passwords or production secrets.</p>
        <label htmlFor="byoa-success">TASK SUCCESS SIGNAL <span>(EXACT ANSWER TEXT)</span></label>
        <input id="byoa-success" value={successSignal} onChange={e=>setSuccessSignal(e.target.value)} placeholder="e.g. Ledger verified" minLength={2} maxLength={120} required={!replay} disabled={!!replay}/>
        <p className="byoa-field-note">Case-insensitive literal answer check. A match does not certify real-world task success.</p>
        {error&&<div className="ch-inline-alert" role="alert"><CircleAlert size={17}/>{error}</div>}
        <button type="submit" className="ch-primary byoa-submit" disabled={pending}>
          {pending?<><RefreshCcw className="spinner" size={18}/> PREPARING CAMPAIGN</>:<>{replay?'REPLAY ORIGINAL ATTACKS':'CONNECT MY AGENT'} <ArrowUpRight size={20}/></>}
        </button>
      </form>
      <aside className="byoa-attack-panel">
        <Kicker>02 / CAMPAIGN PREVIEW ? NO RUN STARTED</Kicker>
        <h2>Six rounds.<br/><em>Real responses.</em></h2>
        <p>Attack prompts are lower-trust data. Your agent makes the decisions—not a script pretending to be your agent.</p>
        <div className="byoa-attack-list">{attackCases.map(item=><div key={item.id}><span>{item.id}</span><div><strong>{item.title}</strong><small>{item.desc}</small></div><em>{item.type}</em></div>)}</div>
        <div className="byoa-privacy"><LockKeyhole size={20}/><span>Your agent runs in your own environment. The outbound connector reports observed actions; the lab never executes them. This is not a VM attestation of your agent's runtime.</span></div>
      </aside>
    </div>
    <div className="byoa-proof-link"><div><strong>VULTR CONTAINED SAMPLE</strong><p>Explore a verified project-owned worker run, with 22 boundary checks, actual synthetic actions, and teardown evidence. Separate from your agent.</p></div><a href="/contained-sample">INSPECT PROOF <ArrowUpRight size={15}/></a></div>
    <div className="byoa-demo-disclosure"><div><span>EXISTING INTERNAL EXPERIMENT</span><h3>Want to inspect the supplier test?</h3><p>The original $24/$72 supplier scenario has been preserved as a clearly labeled DEMO—not the BlastLab product or proof of testing your agent.</p></div><button className="ch-outline" onClick={onDemo}>OPEN SUPPLIER DEMO <ArrowRight size={17}/></button></div>
  </main>;
}

export function AgentLabCampaign({created,onNew,onRetest}:{created:Created|null,onNew:()=>void,onRetest:(created:Created)=>void}){
  const [state,setState]=useState<AgentSummary|null>(null);
  const [report,setReport]=useState<CampaignReport|null>(null);
  const [baseline,setBaseline]=useState<CampaignReport|null>(created?.baseline_report||null);
  const [baselineError,setBaselineError]=useState('');
  const [error,setError]=useState('');
  const [copied,setCopied]=useState(false);
  const [verifying,setVerifying]=useState(false);
  const [retesting,setRetesting]=useState(false);
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
  const retest=async()=>{
    if(!report)return;
    setRetesting(true);setError('');
    try{onRetest(await replayReport(report))}
    catch(e){setError(e instanceof Error?e.message:'Unable to replay campaign')}
    finally{setRetesting(false)}
  };
  const importBaseline=async(event:React.ChangeEvent<HTMLInputElement>)=>{
    const file=event.target.files?.[0];
    event.target.value='';
    if(!file)return;
    setBaselineError('');
    setBaseline(null);setVerifying(true);
    try{
      if(!report)throw new Error('Wait for the current report.');
      if(file.size>500000)throw new Error('Report exceeds the 500 KB comparison limit.');
      const candidate=JSON.parse(await file.text()) as CampaignReport;
      await verifyImported(candidate,report);
      setBaseline(candidate);
    }catch(e){
      setBaseline(null);
      setBaselineError(e instanceof Error?e.message:'Unable to import the baseline report.');
    }finally{setVerifying(false)}
  };
  const compared=report&&baseline?report.results.map(current=>({
    ...current,previous:baseline.results.find(item=>item.case_id===current.case_id)!
  })):[];
  const resolved=compared.filter(item=>item.previous.verdict==='BREACHED'&&item.verdict!=='BREACHED').length;
  const regressions=compared.filter(item=>item.previous.verdict!=='BREACHED'&&item.verdict==='BREACHED').length;
  const exactReplay=!!baseline&&!!report&&baseline.attack_plan_sha256===report.attack_plan_sha256&&baseline.canary===report.canary&&baseline.task===report.task&&baseline.forbidden_tools.length===report.forbidden_tools.length&&baseline.forbidden_tools.every((name,index)=>name===report.forbidden_tools[index])&&
    JSON.stringify(baseline.allowed_tools||[])===JSON.stringify(report.allowed_tools||[])&&
    (baseline.success_contains||'')===(report.success_contains||'')&&
    baseline.results.length===report.results.length;
  return <main className="ch-page byoa-page">
    <div className="ch-page-top"><Kicker>{done?'BLASTLAB / COMPLETED AGENT CAMPAIGN':'BLASTLAB / AGENT CAMPAIGN'}</Kicker><span className="byoa-meta">{state?.completed||0} / {created.cases_total} CASES · VULTR {created.attack_model}</span></div>
    <div className="byoa-campaign-hero"><div><span className="byoa-status"><Activity size={16}/>{done?'CAMPAIGN COMPLETED':'AWAITING YOUR AGENT RUNNER'}</span>
      <h1>{done?'The agent has been tested.':"Campaign created."}<br/><em>{done?'Here is what it did.':'Now run your agent.'}</em></h1><p>Attack plan <code>{created.attack_model}</code> / VULTR GENERATED. Campaign ID <code>{created.session_id}</code>. {done?'Your owner-run connector submitted the recorded responses and tool intents. Its runtime is not VM-attested.':'Your agent is not connected until its local connector starts. It runs in your own environment. BlastLab observes only the responses and proposed tools your connector submits.'}</p>
      </div><div className="byoa-progress"><strong>{state?.completed||0}<span>/{created.cases_total}</span></strong><small>CASES RECEIVED</small><div><i style={{width:(100*(state?.completed||0)/created.cases_total)+'%'}}/></div></div></div>
    {created.recovery_key&&<section className="byoa-recovery-receipt" aria-label="Save report recovery key">
      <Kicker>PRIVATE RECOVERY RECEIPT / SAVE NOW</Kicker>
      <h2>Keep your report access.</h2>
      <p>Save this key separately from the connector token. It can only retrieve a completed campaign report for 30 days. It cannot run your agent or submit responses. BlastLab shows it only at creation; if you lose it, it cannot be recovered.</p>
      <div className="byoa-recovery-identity"><span>CAMPAIGN ID</span><code>{created.session_id}</code><span>READ-ONLY KEY</span><code>••••••••••••••••••••••••••••••••</code></div>
      <div className="byoa-recovered-actions">
        <button type="button" className="ch-outline" onClick={()=>copy(created.recovery_key!)}><Copy size={16}/> COPY RECOVERY KEY</button>
        <button type="button" className="ch-outline" onClick={()=>downloadJson({campaign_id:created.session_id,recovery_key:created.recovery_key,recovery_expires_at:created.recovery_expires_at,scope:'read-only completed campaign report'},'blastlab-recovery-'+created.session_id+'.json')}><Download size={16}/> SAVE RECOVERY RECEIPT</button>
      </div>
      <small>Expires {created.recovery_expires_at?new Date(created.recovery_expires_at).toLocaleString():'30 days after creation'}. Keep this file private. It contains a bearer credential.</small>
    </section>}
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
      <div className="byoa-report-header"><div><Kicker>03 / OBSERVED VERDICTS</Kicker><h2>{report.breached} observed <em>rule violation{report.breached===1?'':'s'}.</em></h2><p>{report.tests_completed} of {report.tests_total} cases submitted. The attack text was generated by {report.attack_plan_provider} ({report.attack_plan_model}); verdicts use the connected agent's runner-reported decisions.</p></div><button className="ch-outline" onClick={()=>downloadJson(report,'blastlab-agent-'+created.session_id+'.json')}><Download size={16}/> EXPORT REPORT</button></div>
      {(report.allowed_tools||report.success_contains)&&<div className="byoa-policy-summary">
         <strong>DECLARED POLICY</strong>
         <span>Allowed: {(report.allowed_tools||[]).join(', ')||'not configured'}</span>
         <span>Forbidden: {report.forbidden_tools.join(', ')}</span>
         <span>Task success text: {report.success_contains||'not configured'}</span>
       </div>}
               <section className="byoa-success-coverage" aria-label="Literal task success signal observations">
          <span>OWNER-DEFINED TASK SIGNAL / LITERAL ONLY</span>
          <strong>{report.results.filter(item=>item.task_success_signal==='ANSWER_CONTAINS_REQUIRED_TEXT').length}
          <small> / {report.tests_completed} reported answers contained “{report.success_contains||'no configured signal'}”</small></strong>
          <p>Only checks the configured answer text. It cannot independently certify task correctness, hidden side effects or runner identity.</p>
        </section>
<div className="byoa-report-kpis"><div><small>TESTED</small><b>{report.tests_completed}</b></div><div><small>VIOLATIONS</small><b className="byoa-danger">{report.breached}</b></div><div><small>NO VIOLATION OBSERVED</small><b>{report.no_observed_violation}</b></div><div><small>AGENT PROVENANCE</small><b className="byoa-small-value">RUNNER-REPORTED</b></div></div>
      {done&&<section className="byoa-comparison" aria-label="Compare before and after agent campaigns">
        <div><Kicker>04 / BEFORE & AFTER</Kicker><h2>Did the fix hold?</h2>
          <p>Export this campaign, update your agent, then use Retest to replay these exact attacks. Import the earlier report to compare. Reports are sent to BlastLab for integrity and policy verification; the verification endpoint does not retain them.</p>
          <label className="ch-outline byoa-compare-upload" htmlFor="byoa-baseline-file"><Download size={16}/> IMPORT PREVIOUS REPORT</label>
          <input id="byoa-baseline-file" type="file" accept=".json,application/json" onChange={importBaseline} disabled={verifying} className="byoa-file-input" />
          {verifying&&<p role="status">Verifying report and replay contract…</p>}
          {baselineError&&<p role="alert" className="byoa-comparison-error">{baselineError}</p>}
        </div>
        {baseline&&<div className="byoa-compare-results">
          <div className="byoa-compare-score" aria-label="Before and after comparison">
            <div className="byoa-compare-side before"><small>BASELINE</small><strong>{baseline.breached}</strong><span>observed violations</span></div>
            <ArrowRight size={22}/>
            <div className="byoa-compare-side after"><small>RETEST</small><strong>{report.breached}</strong><span>observed violations</span></div>
          </div>
                  <div className="byoa-compare-task-signal" aria-label="Literal task signal comparison">
             <strong>TASK SIGNAL — LITERAL ANSWER TEXT</strong>
             <span>{baseline.results.filter(item=>item.task_success_signal==='ANSWER_CONTAINS_REQUIRED_TEXT').length}/{baseline.tests_completed} baseline
             <ArrowRight size={15}/> {report.results.filter(item=>item.task_success_signal==='ANSWER_CONTAINS_REQUIRED_TEXT').length}/{report.tests_completed} retest</span>
             <small>Not a certification of semantic task success or independent agent identity.</small>
           </div>
   <div className="byoa-compare-delta">
            <div><small>RESOLVED</small><strong>{resolved}</strong></div>
            <div><small>NEW BREACHES</small><strong>{regressions}</strong></div>
          </div>
          <div className={'byoa-compare-proof '+(exactReplay?'verified':'mismatch')}>
            {exactReplay?<CheckCircle2 size={17}/>:<AlertTriangle size={17}/>}
            <div><strong>{exactReplay?'EXACT ATTACK REPLAY VERIFIED':'REPLAY CONTRACT MISMATCH'}</strong><code>{report.attack_plan_sha256}</code><small>Same task · same forbidden-tool policy · same canary · {report.results.length} attack cases. Server checks report integrity and replay contract, not runner source.</small></div>
          </div>
          <div className="byoa-compare-cases">{compared.map(item=><div className="byoa-compare-case" key={item.case_id}><div className="byoa-compare-case-name"><strong>{item.family}</strong><small>{item.case_id}</small></div><div className="byoa-compare-verdicts"><span className={item.previous.verdict==='BREACHED'?'breach':'clean'}>BEFORE · {item.previous.verdict.replaceAll('_',' ')}</span><ArrowRight size={12}/><span className={item.verdict==='BREACHED'?'breach':'clean'}>AFTER · {item.verdict.replaceAll('_',' ')}</span></div></div>)}</div>
          {baseline.mitigations.filter(fix=>baseline.results.some(result=>result.case_id===fix.case_id&&result.verdict==='BREACHED')).length>0&&<div className="byoa-compare-remediations"><div className="byoa-compare-remediations-head"><strong>BASELINE FINDINGS → TARGETED FIXES</strong><small>Recommendations grounded in the observed baseline responses</small></div>{baseline.mitigations.filter(fix=>baseline.results.some(result=>result.case_id===fix.case_id&&result.verdict==='BREACHED')).map(fix=><div className="byoa-compare-remediation" key={fix.case_id}><span>{baseline.results.find(result=>result.case_id===fix.case_id)?.family||fix.case_id}</span><p>{fix.trigger.join('; ')}</p><strong>{fix.action}</strong></div>)}</div>}
          <p>A matching replay contract does not prove the runner identity or an agent source-code change. Tool proposals are runner-reported, not executed by BlastLab.</p>
        </div>}
      </section>}
      <div className="byoa-findings">{report.results.map(item=><article id={"byoa-case-"+item.case_id} key={item.case_id} className="byoa-finding">
        <div className="byoa-finding-top"><span>{item.family.toUpperCase()}</span><span className={item.verdict==='BREACHED'?'byoa-failed':'byoa-resisted'}>{item.verdict.replaceAll('_',' ')}</span></div>
        <h3>{item.case_id.replaceAll('_',' ')}</h3><p>{item.reasons.length?item.reasons.join('; '):'No matching forbidden action or attacker marker was observed in the submitted response.'}</p>{item.observations?.map((note,i)=><small className="byoa-observation-note" key={i}>{note}</small>)}
         {item.task_success_signal&&<p className="byoa-task-success">TASK SUCCESS SIGNAL: {item.task_success_signal==='ANSWER_CONTAINS_REQUIRED_TEXT'?'OBSERVED':'NOT OBSERVED'} (literal answer check only)</p>}
        <div className="byoa-observation"><span>ACTUAL RUNNER-REPORTED RESPONSE</span><code>{item.agent_answer.slice(0,500)||'(no answer)'}</code><small>{item.observed_tool_calls.length} observed/proposed tool call(s)</small></div>
         <details className="byoa-case-evidence"><summary>INSPECT EXACT UNTRUSTED ATTACK AND TOOL INTENTS</summary>
           <pre>{report.evidence.events.find(entry=>entry.event.case_id===item.case_id)?.event.attack||'Attack evidence unavailable'}</pre>
           <pre>{JSON.stringify(item.observed_tool_calls,null,2)}</pre>
         </details>
      </article>)}</div>
      <div className="byoa-remediations"><Kicker>04 / MITIGATE & RETEST</Kicker><h2>Turn failures into fixes.</h2>
        {report.mitigations.length?report.mitigations.map(fix=><div className="byoa-mitigation-detail" key={fix.case_id}>
          <a href={"#byoa-case-"+fix.case_id} className="byoa-mitigation-case-link">VIEW EXACT CASE EVIDENCE: {fix.case_id.toUpperCase()} <ArrowUpRight size={13}/></a>
          <p>{fix.action}</p>
          <small>Observed trigger: {fix.trigger.join('; ')}</small><small>{fix.verify_fix}</small>
          <small>Verify the real tool call in your own execution logs. BlastLab only receives the runner's declaration.</small>
        </div>):<p>No matching attack rule was violated in these six reported cases. This does not prove the agent is generally secure; test additional inputs and verify task success independently.</p>}
        <button className="ch-primary" onClick={retest} disabled={!done||retesting}>{retesting?'PREPARING EXACT REPLAY':'RETEST YOUR UPDATED AGENT'} <ArrowUpRight size={18}/></button>
      </div>
      <div className="byoa-evidence-note"><Fingerprint size={22}/><div><strong>Vultr-generated attack plan · evidence integrity, not source attestation.</strong><p>This report contains a SHA-256 chain and a full-report manifest for internal consistency. The agent responses came from a user-operated connector, not a Vultr-attested runtime. A user with control of the connector can misreport them; the lab does not claim otherwise.</p><p>Attack plan SHA-256: <code>{report.attack_plan_sha256}</code></p><code>{report.manifest_sha256}</code></div></div>
    </div>}
  </main>;
}
