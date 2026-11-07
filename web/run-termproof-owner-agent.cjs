/**
 * Run original TermProof (Vercel Gemini/DeepSeek + deterministic verifier)
 * through the real BlastLab outbound connector, using a session token
 * held in the owner's visible Chrome browser. No secret files.
 * Preflight-only makes no BlastLab writes.
 */
const path = require('path');
const cp = require('child_process');
const {chromium} = require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
const ROOT = path.resolve(__dirname, '..');
const BASE = 'https://blastlab.45-77-138-147.sslip.io';
const TERMPROOF = 'https://termproof-mauve.vercel.app/api/verify';

async function verifyRuntime(){
 const ctrl=new AbortController();
 const timer=setTimeout(()=>ctrl.abort(),120000);
 try{
  const r=await fetch(TERMPROOF,{
   method:'POST',signal:ctrl.signal,
   headers:{'Content-Type':'application/json','Accept':'application/json',
    'User-Agent':'BlastLab-TermProof-Owner-Acceptance/1.0'},
   body:JSON.stringify({
    milestone:'Public repository exists',
    githubRepository:'https://github.com/ShalyX/termproof'
   })
  });
  const v=await r.json().catch(()=>({}));
  if(!r.ok)throw Error('REAL_TERMPROOF_NOT_READY HTTP '+r.status+' '+(v.code||'unknown'));
  if(!v.verdict||!v.provenance?.planner?.provider||
      !Array.isArray(v.claims)||!Array.isArray(v.evidence))
   throw Error('TermProof returned no genuine model planning and deterministic verdict');
  console.log('REAL_TERMPROOF_PREFLIGHT_PASS',JSON.stringify({
   verdict:v.verdict,provider:v.provenance.planner.provider,
   claims:v.claims.length,evidence:v.evidence.length
  }));
 }finally{clearTimeout(timer)}
}
(async()=>{
 const only=process.argv.includes('--preflight-only');
 await verifyRuntime();
 if(only){console.log('NO_BLASTLAB_CASES_SUBMITTED');return}
 const browser=await chromium.connectOverCDP('http://127.0.0.1:9347',{timeout:12000});
 const page=browser.contexts().flatMap(c=>c.pages())
  .find(p=>p.url().startsWith(BASE+'/app/campaign'));
 if(!page)throw Error('Open the original BlastLab campaign in the Chrome window');
 const session=await page.evaluate(()=>JSON.parse(
  sessionStorage.getItem('blastlab-agent-session')||'{}'
 ));
 const id=session.session_id,token=session.join_token;
 if(!/^[0-9a-f]{32}$/.test(id||'')||!token||token.length<24)
  throw Error('Campaign or one-time token is no longer in the browser');
 if(session.expires_at&&Date.parse(session.expires_at)<Date.now())
  throw Error('Join token expired. Create a new campaign after fixing TermProof.');
 const args=['web/public/connect/blastlab_connector.py','--session',id,
             '--adapter','examples.termproof_live_agent:respond','--base',BASE];
 const child=cp.spawnSync('python',args,{
  cwd:ROOT,env:{...process.env,BLASTLAB_SESSION_TOKEN:token},
  stdio:'inherit',timeout:900000,windowsHide:false
 });
 if(child.error)throw child.error;
 if(child.status!==0)throw Error('TermProof connector failed; report is not complete');
 console.log('TERMPROOF_REAL_AGENT_CONNECTOR_COMPLETE',id);
 await page.reload({waitUntil:'domcontentloaded',timeout:45000});
 await page.bringToFront();
 process.exit(0);
})().catch(e=>{
 console.error('SAFE_ABORT',e instanceof Error?e.message:String(e));
 console.error('No fabricated BlastLab responses were submitted.');
 process.exit(2);
});
