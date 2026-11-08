import {ArrowRight,ArrowUpRight,Globe2,Code2,LockKeyhole,Server,Gauge,Lock} from 'lucide-react';
import './facility.css';

export const chambers = [
  {number:'01',name:'The Web',icon:Globe2,description:'Hostile webpages and indirect instructions while your agent completes a legitimate mission.'},
  {number:'02',name:'Toolchain',icon:Code2,description:'Compromised MCP and tool responses, documentation, APIs and excessive permissions.'},
  {number:'03',name:'The Vault',icon:LockKeyhole,description:'Decoy-secret access, credential boundaries and unauthorized disclosure.'},
  {number:'04',name:'The Machine',icon:Server,description:'Filesystem abuse, destructive execution and runaway processes.'},
  {number:'05',name:'Chaos',icon:Gauge,description:'Combined attacks, interruptions and recovery while the agent still has to finish its mission.'},
];

export function ChamberInventory(){
  return <div className="facility-inventory">{chambers.map(({icon:Icon,...chamber},index)=><article key={chamber.number} className={index===0?'facility-chamber available':'facility-chamber'}>
    <div className="facility-chamber-number"><span>{chamber.number} / CHAMBER</span><span>{index===0?'WEB MISSIONS':<><Lock size={12}/> PLANNED</>}</span></div>
    <Icon size={25} aria-hidden="true"/><h3>{chamber.name}</h3><p>{chamber.description}</p>
    {index===0?<a href="/app/chambers/web">SET UP YOUR AGENT <ArrowUpRight size={16}/></a>:<small>NOT BUILT · CANNOT BE LAUNCHED</small>}
  </article>)}</div>;
}

export default function FacilityExperience(){
  return <main className="ch-page facility-page">
    <div className="ch-page-top"><span className="ch-eyebrow">BLASTLAB / CHAMBER LIBRARY</span><span className="ch-tag">01 AVAILABLE / 04 PLANNED</span></div>
    <div className="ch-library-head"><div><h1>Your agent.<br/><em>Hostile environments.</em></h1><p>Bring the agent you built. Give it a legitimate mission, expose it to controlled attacks, then inspect what happened and replay after a change. Choose where to put it under pressure.</p></div><div className="ch-lab-counter"><span>THE FACILITY</span><strong>01<span>/05</span></strong><small>Chambers available in this release</small></div></div>
    <section className="facility-web-intro" aria-labelledby="facility-web-title"><div><span className="ch-subcap">START WITH CHAMBER 01</span><h2 id="facility-web-title">The Web is the first environment.</h2><p>Your source runs in a disposable Vultr worker. A separate, controlled Chromium browser reads a synthetic supplier page with real inventory and hostile content. Your agent must read that page and complete the selected mission.</p><a href="/app/chambers/web" className="ch-primary">ENTER THE WEB <ArrowRight size={18}/></a></div><div className="facility-flow" aria-label="Web Chamber workflow, explanatory diagram"><span>YOUR AGENT + MISSION</span><ArrowRight/><span>HOSTILE WEBPAGE</span><ArrowRight/><span>OBSERVE · FIX · REPLAY</span><small>Bounded synthetic pages. No public Internet browsing. Findings distinguish returned answers, declared tool intents and host-observed browser reads.</small></div></section>
    <ChamberInventory/>
    <section className="facility-support"><div><h2>One lab. Shared execution and evidence.</h2><p>Chambers define the hostile environments. Hosted execution runs your agent. Campaigns define the attacks. Reports retain findings and exact replay. Five attack families in a campaign do not mean five chambers are implemented.</p></div><div><h3>Keep the original experiment in view.</h3><p>The project-owned supplier browser test remains a separate demonstration of policy enforcement, reset and mission resume.</p><a href="/app/demo">OPEN SUPPLIER DEMO <ArrowUpRight size={15}/></a><a href="/app/connect">EXISTING CONTENT CAMPAIGNS &amp; REPORT RECOVERY <ArrowUpRight size={15}/></a></div></section>
  </main>;
}
