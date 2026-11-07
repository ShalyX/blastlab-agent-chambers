const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const base='http://127.0.0.1:4173';
 const proofDir=path.resolve(__dirname,'../artifacts/phase23-termproof-founder');
 const termproof=JSON.parse(fs.readFileSync(path.join(proofDir,'retest-report.json'),'utf8'));
 const vulnerable=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../artifacts/phase13-live-20261106/before-report.json'),'utf8'));
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const screenshots=path.resolve(__dirname,'qa-phase23-closure');fs.mkdirSync(screenshots,{recursive:true});
 const scenarios=[['termproof',termproof],['vulnerable-sample',vulnerable]];
 let checks=0;
 try{
  for(const [label,report] of scenarios){
   for(const width of [1440,390]){
    const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    const session={
     session_id:report.session_id,join_token:'a'.repeat(44),
     expires_at:'2026-12-01T00:00:00Z',cases_total:report.tests_total,
     attack_source:report.attack_plan_source,
     attack_provider:report.attack_plan_provider,
     attack_model:report.attack_plan_model,
     attack_plan_sha256:report.attack_plan_sha256,
     source_type:report.source_type,connector:'/connect/blastlab_connector.py'
    };
    await page.addInitScript(data=>sessionStorage.setItem('blastlab-agent-session',JSON.stringify(data)),session);
    await page.route('**/api/agent-lab/sessions/**',async route=>{
      const uri=new URL(route.request().url());
      if(uri.pathname.endsWith('/status')){
       return route.fulfill({status:200,contentType:'application/json',
        body:JSON.stringify({session_id:session.session_id,agent_name:report.agent_name,
         status:'complete',completed:6,total:6,expires_at:session.expires_at,
         source_type:report.source_type})});
      }
      if(uri.pathname.endsWith('/report')){
       return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(report)});
      }
      return route.fulfill({status:404,contentType:'application/json',body:'{"error":"not mocked"}'});
    });
    const resp=await page.goto(base+'/app',{waitUntil:'domcontentloaded',timeout:45000});
    assert.equal(resp.status(),200);
    await page.getByRole('heading',{name:'What this lab actually tests.'}).waitFor({timeout:20000});
    assert.equal(await page.locator('.byoa-surface-item').count(),8);
    assert.equal(await page.locator('.byoa-surface-item .byoa-surface-live').count(),5);
    assert.equal(await page.locator('.byoa-surface-item .byoa-surface-planned').count(),3);
    assert(await page.getByText('Customer runtime sandboxing',{exact:true}).isVisible());
    await page.screenshot({path:path.join(screenshots,label+'-'+width+'-coverage.png'),fullPage:true});
    await page.goto(base+'/app/campaign',{waitUntil:'domcontentloaded',timeout:45000});
    await page.locator('.byoa-success-coverage').waitFor({timeout:24000});
    const success=await page.locator('.byoa-success-coverage').innerText();
    assert(success.includes('LITERAL ONLY'),success);
    assert(success.includes('reported answers contained'),success);
    await page.locator('.byoa-findings .byoa-finding').first().waitFor();
    assert.equal(await page.locator('.byoa-finding').count(),6);
    const remedies=await page.locator('.byoa-mitigation-case-link').count();
    if(report.breached>0){
     assert(remedies>0,'Breaches have case-linked repair actions');
     const link=page.locator('.byoa-mitigation-case-link').first();
     const target=await link.getAttribute('href');
     assert(target.startsWith('#byoa-case-'));
     await link.click();
     assert.equal(new URL(page.url()).hash,target);
     assert.equal(await page.locator(target).count(),1);
    }else assert.equal(remedies,0);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,'no overflow '+width);
    assert.deepEqual(errors,[]);
    await page.screenshot({path:path.join(screenshots,label+'-'+width+'-report.png'),fullPage:true});
    console.log('PHASE23_LOCAL_UX_PASS',JSON.stringify({scenario:label,width,remedies,reportedBreaches:report.breached,errors}));
    await page.close();
    checks++;
   }
  }
  console.log('PHASE23_CLOSURE_BROWSER_QA_PASS',JSON.stringify({scenarios:scenarios.length,viewports:2,checks}));
 }finally{await browser.close()}
})().catch(e=>{console.error('PHASE23_CLOSURE_BROWSER_QA_FAIL',String(e.stack||e));process.exitCode=2});
