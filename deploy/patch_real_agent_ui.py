from pathlib import Path
p=Path('web/src/App.tsx')
s=p.read_text(encoding='utf-8')
if 'AgentLabConnect' not in s:
 s=s.replace("from './ChamberExperience';","from './ChamberExperience';\nimport { AgentLabConnect, AgentLabCampaign } from './AgentLabExperience';")
s=s.replace("    if(path.endsWith('/evidence'))return 'evidence';","    if(path.endsWith('/campaign'))return 'campaign';\n    if(path.endsWith('/evidence'))return 'evidence';")
s=s.replace("    if(path.endsWith('/chambers/web'))return 'setup';\n    return 'chambers';","    if(path.endsWith('/chambers/web'))return 'setup';\n    if(path.endsWith('/demo'))return 'chambers';\n    return 'agent';")
s=s.replace("    const path=to==='chambers'?'/app':to==='setup'?'/app/chambers/web':'/app/'+to;","    const path=to==='agent'?'/app':to==='chambers'?'/app/demo':to==='setup'?'/app/chambers/web':'/app/'+to;")
if 'const [agentSession,setAgentSession]' not in s:
 s=s.replace("  const {section,navigate}=useSection();","""  const {section,navigate}=useSection();
  const [agentSession,setAgentSession]=useState<{
    session_id:string;join_token:string;expires_at:string;cases_total:number;
    source_type:string;connector:string
  }|null>(()=>{
    try{const old=sessionStorage.getItem('blastlab-agent-session');return old?JSON.parse(old):null;}
    catch{return null;}
  });
""")
if 'const connectAgent=' not in s:
 s=s.replace("  const select=(next:Section)=>{","""  const connectAgent=(created:NonNullable<typeof agentSession>)=>{
    setAgentSession(created);
    try{sessionStorage.setItem('blastlab-agent-session',JSON.stringify(created));}catch{}
    navigate('campaign');setMobileNav(false);
  };
  const newAgent=()=>{
    setAgentSession(null);
    try{sessionStorage.removeItem('blastlab-agent-session');}catch{}
    navigate('agent');setMobileNav(false);
  };
  const select=(next:Section)=>{""")
if "PRODUCT / CONNECT YOUR AGENT" not in s:
 s=s.replace('<div className="nav-cluster"><span className="rail-label">WORKSPACE</span>',"""
      <div className="nav-cluster"><span className="rail-label">PRODUCT / CONNECT YOUR AGENT</span>
        <button className={'rail-link '+(section==='agent'?'active':'')} onClick={()=>select('agent')}><Zap size={18}/> Connect your agent <span className="nav-key">01</span></button>
        <button className={'rail-link '+(section==='campaign'?'active':'')} onClick={()=>select('campaign')}><Activity size={18}/> Attack campaign <span className="nav-key">02</span></button>
        <span className="rail-label" style={{marginTop:19}}>DEMO / INTERNAL SUPPLIER CASE</span>""")
for old,new in [
 ('Chamber library <span className="nav-key">01</span>','Supplier demo <span className="nav-key">D1</span>'),
 ('The Web <span className="nav-key">02</span>','Demo setup <span className="nav-key">D2</span>'),
 ('Control room <span className="nav-key">03</span>','Demo replay <span className="nav-key">D3</span>'),
 ('Run results <span className="nav-key">04</span>','Demo results <span className="nav-key">D4</span>'),
 ('Evidence vault <span className="nav-key">05</span>','Demo evidence <span className="nav-key">D5</span>'),
 ('Architecture <span className="nav-key">06</span>','Architecture <span className="nav-key">D6</span>'),
]:
 s=s.replace(old,new)
s=s.replace("section==='chambers'?'CHAMBERS':section==='setup'?'WEB CHAMBER'",
  "section==='agent'?'CONNECT AGENT':section==='campaign'?'AGENT ATTACK CAMPAIGN':section==='chambers'?'SUPPLIER DEMO':section==='setup'?'DEMO SETUP'")
s=s.replace('<button className="top-run-btn" onClick={()=>select(\'setup\')}><Plus size={16}/> NEW TEST RUN</button>',
  '<button className="top-run-btn" onClick={newAgent}><Plus size={16}/> CONNECT AGENT</button>')
if "section==='agent'&&<AgentLabConnect" not in s:
 s=s.replace("      {section==='chambers'&&<ChamberLibrary", """      {section==='agent'&&<AgentLabConnect onCreated={connectAgent} onDemo={()=>select('chambers')}/>}
      {section==='campaign'&&<AgentLabCampaign created={agentSession} onNew={newAgent}/>}
      {section==='chambers'&&<ChamberLibrary""")
s=s.replace("Your agent read<br/>the attack.<br/><em>The boundary held.</em>","Bring your agent.<br/><em>We'll try to break it.</em>")
s=s.replace("INSTRUCTION OVERRIDE DETECTED IN PAGE","DEMO ATTACK PAYLOAD IN PAGE")
s=s.replace("UNTRUSTED AUTHORITY STOPPED","DEMO POLICY BOUNDARY")
s=s.replace("EXPLORE CHAMBERS","CONNECT YOUR AGENT")
s=s.replace("ENTER THE CHAMBERS","START AGENT TESTING")
s=s.replace("OPEN CHAMBER LIBRARY","OPEN AGENT LAB")
s=s.replace("FIG 01 / THE CONTAINMENT BOUNDARY","FIG 01 / INTERNAL DEMO CONTAINMENT")
p.write_text(s,encoding='utf-8')
print('APP_ROUTER_UPDATED_FOR_REAL_AGENT_PRODUCT')
