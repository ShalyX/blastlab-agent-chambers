const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const folder=path.resolve(__dirname,'../artifacts/phase23-same-agent-real-policy-20261107');
 const baseline=JSON.parse(fs.readFileSync(path.join(folder,'vulnerable-report.json'),'utf8'));
 const after=JSON.parse(fs.readFileSync(path.join(folder,'hardened-report.json'),'utf8'));
 assert.equal(baseline.breached,3);assert.equal(after.breached,0);
 assert.equal(baseline.attack_plan_sha256,after.attack_plan_sha256);
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const dir=path.resolve(__dirname,'qa-phase23-closure');fs.mkdirSync(dir,{recursive:true});
 try{
  for(const width of [1440,390]){
   const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
   const errors=[];page.on('pageerror',x=>errors.push(x.message));
   const created={
    session_id:after.session_id,join_token:'x'.repeat(44),
    expires_at:'2026-12-01T00:00:00Z',
    cases_total:after.tests_total,attack_source:after.attack_plan_source,
    attack_provider:after.attack_plan_provider,
    attack_model:after.attack_plan_model,
    attack_plan_sha256:after.attack_plan_sha256,
    source_type:after.source_type,connector:'/connect/blastlab_connector.py',
    baseline_report:baseline
   };
   await page.addInitScript(data=>sessionStorage.setItem('blastlab-agent-session',JSON.stringify(data)),created);
   await page.route('**/api/agent-lab/sessions/**',async route=>{
    const uri=new URL(route.request().url());
    if(uri.pathname.endsWith('/status'))return route.fulfill({status:200,contentType:'application/json',
     body:JSON.stringify({session_id:after.session_id,agent_name:after.agent_name,status:'complete',completed:6,total:6,expires_at:created.expires_at,source_type:after.source_type})});
    if(uri.pathname.endsWith('/report'))return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(after)});
    return route.fulfill({status:404,body:'{"error":"not mocked"}'});
   });
   await page.goto('http://127.0.0.1:4173/app/campaign',{waitUntil:'domcontentloaded',timeout:40000});
   await page.locator('.byoa-compare-proof.verified').waitFor({timeout:20000});
   const before=await page.locator('.byoa-compare-side.before strong').innerText();
   const fixed=await page.locator('.byoa-compare-side.after strong').innerText();
   assert.equal(before,'3');assert.equal(fixed,'0');
   assert.equal(await page.locator('.byoa-compare-case').count(),6);
   assert.match(await page.locator('.byoa-compare-proof').innerText(),/EXACT ATTACK REPLAY VERIFIED/);
   assert.deepEqual(errors,[]);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
   await page.screenshot({path:path.join(dir,'same-agent-retest-'+width+'.png'),fullPage:true});
   console.log('SAME_AGENT_EXACT_RETEST_BROWSER_QA_PASS',JSON.stringify({width,baseline:before,after:fixed,cases:6,errors}));
   await page.close();
  }
 }finally{await browser.close()}
})().catch(e=>{console.error('SAME_AGENT_EXACT_RETEST_BROWSER_QA_FAIL',String(e.stack||e));process.exitCode=2});
