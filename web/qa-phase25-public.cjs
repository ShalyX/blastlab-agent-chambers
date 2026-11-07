/* Phase25: browser XSS/hostile-content/oversized Unicode safety — local only.
 * Results are deliberate runner-reported test strings, not genuine report evidence.
 */
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const reportPath=path.resolve(__dirname,'../artifacts/phase23-same-agent-real-policy-20261107/vulnerable-report.json');
 const report=JSON.parse(fs.readFileSync(reportPath,'utf8'));
 const injected="<img src=x onerror=window.__blastlabInjected='yes'>"+
    "<svg/onload=window.__blastlabInjected='yes'>"+
    "<script>window.__blastlabInjected='yes'</script>";
 const payload=injected+' — BIDI\u202e | '+ '𠜎'.repeat(50)+'LONG_URL_https://attacker.invalid/'+ 'A'.repeat(900);
 const evilResult=report.results[0];
 evilResult.agent_answer=payload;
 evilResult.reasons=[payload.slice(0,450)];
 evilResult.observations=[payload.slice(0,450)];
 evilResult.observed_tool_calls=[{name:'read_document',arguments:{html:payload,requested_url:'https://attacker.invalid/'+ 'A'.repeat(120)}}];
 report.agent_name=injected.slice(0,150);
 report.task=payload.slice(0,450);
 const firstMitigation=report.mitigations[0];
 if(firstMitigation){
  firstMitigation.action=payload.slice(0,450);
  firstMitigation.verify_fix=payload.slice(0,450);
  firstMitigation.trigger=[payload.slice(0,450)];
 }
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const dir=path.resolve(__dirname,'qa-phase25-public');fs.mkdirSync(dir,{recursive:true});
 try{
  for(const width of [1440,390]){
   const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
   const errors=[];const suspicious=[];
   page.on('pageerror',e=>errors.push(e.message));
   page.on('request',r=>{if(r.url().includes('attacker.invalid'))suspicious.push(r.url())});
   const created={
     session_id:report.session_id,join_token:'a'.repeat(44),
     expires_at:'2026-12-01T00:00:00Z',
     cases_total:report.tests_total,
     attack_source:report.attack_plan_source,
     attack_provider:report.attack_plan_provider,
     attack_model:report.attack_plan_model,
     attack_plan_sha256:report.attack_plan_sha256,
     source_type:report.source_type,
     connector:'/connect/blastlab_connector.py'
   };
   await page.addInitScript(data=>{
     window.__blastlabInjected='no';
     sessionStorage.setItem('blastlab-agent-session',JSON.stringify(data));
   },created);
   await page.route('**/api/agent-lab/sessions/**',async route=>{
     const uri=new URL(route.request().url());
     if(uri.pathname.endsWith('/status'))
       return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
         session_id:report.session_id,agent_name:report.agent_name,status:'complete',
         completed:6,total:6,expires_at:created.expires_at,source_type:report.source_type})});
     if(uri.pathname.endsWith('/report'))
       return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(report)});
     return route.fulfill({status:404,contentType:'application/json',body:'{"error":"not mocked"}'});
   });
   const resp=await page.goto('https://blastlab.45-77-138-147.sslip.io/app/campaign',{waitUntil:'domcontentloaded',timeout:45000});
   assert.equal(resp.status(),200);
   await page.locator('.byoa-finding').first().waitFor({timeout:28000});
   assert.equal(await page.locator('.byoa-finding').count(),6);
   const first=page.locator('.byoa-finding').first();
   assert((await first.locator('.byoa-observation').innerText()).includes('<img src=x onerror='),'payload shown as plain text');
   assert.equal(await page.evaluate(()=>window.__blastlabInjected),'no','no script evaluation');
   assert.equal(await page.locator('script[src*="attacker.invalid"],img[src*="attacker.invalid"],svg[onload],img[onerror]').count(),0,'no injected DOM nodes');
   assert.equal(suspicious.length,0,'no cross-origin attacker request');
   assert.equal(errors.length,0,'no JS crash');
   const offenders=await page.evaluate(()=>[...document.querySelectorAll('*')].map(x=>({name:x.tagName,cls:String(x.className||'').slice(0,70),right:Math.ceil(x.getBoundingClientRect().right),width:Math.ceil(x.getBoundingClientRect().width),scroll:x.scrollWidth})).filter(x=>x.right>innerWidth+2&&x.width>25).sort((a,b)=>b.right-a.right).slice(0,14));
   console.log('PHASE25_HORIZONTAL_OFFENDERS',width,JSON.stringify(offenders));
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true,'no overflow at '+width);
   await page.screenshot({path:path.join(dir,'hostile-report-'+width+'.png'),fullPage:true});
   console.log('PHASE25_PUBLIC_HOSTILE_REPORT_QA_PASS',JSON.stringify({
     width,escaped:true,external_requests:suspicious.length,errors,overflow:false,
     visible_cases:6
   }));
   await page.close();
  }
 }finally{await browser.close()}
})().catch(e=>{console.error('PHASE25_PUBLIC_HOSTILE_REPORT_QA_FAIL',e.stack||String(e));process.exitCode=2});
