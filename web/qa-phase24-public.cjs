const path=require('path'),fs=require('fs'),crypto=require('crypto'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const base='https://blastlab.45-77-138-147.sslip.io';
 const dir=path.join(__dirname,'qa-phase24-public');
 fs.mkdirSync(dir,{recursive:true});
 const browser=await chromium.launch({headless:true,channel:'chrome',args:['--host-resolver-rules=MAP blastlab.45-77-138-147.sslip.io 45.77.138.147']});
 const expected=[
  {index:0,metric:'3 to 0',cases:6,label:'Same agent: real security mitigation'},
  {index:1,metric:'0 to 6',cases:6,label:'Preexisting agent: legitimate task recovery'},
  {index:2,metric:'22 / 22',cases:22,label:'Vultr worker: contained execution'},
  {index:3,metric:'0 to 0',cases:6,label:'Third-party runtime compatibility'}
 ];
 let completed=0;
 try{
  for(const width of [1440,390]){
   const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   const response=await page.goto(base+'/proof',{waitUntil:'domcontentloaded',timeout:45000});
   assert.equal(response.status(),200,'proof route response');
   await page.getByRole('heading',{name:/Show the work/}).waitFor({timeout:25000});
   await page.locator('.proof-lane').first().waitFor({timeout:25000});
   assert.equal(await page.locator('.proof-lane').count(),4);
   assert.equal(await page.getByText('NOT YET VERIFIED',{exact:false}).count()>0,true,'external provenance disclosure');
   for(const item of expected){
    const lane=page.locator('.proof-lane').nth(item.index);
    await lane.click();
    assert.equal(await lane.getAttribute('aria-pressed'),'true','activated proof lane');
    await page.locator('.proof-inspector').getByRole('heading',{name:item.label}).waitFor();
    assert((await lane.innerText()).includes(item.metric),'correct lane metric '+item.label);
    if(item.index===2){
     assert.equal(await page.locator('.proof-check-item').count(),22,'actual 22 checks');
     assert.equal(await page.locator('.proof-contain-summary>div').count(),4);
     assert.match(await page.locator('.proof-source-note').innerText(),/November 6 archived worker/);
    }else{
     assert.equal(await page.locator('.proof-case').count(),6,'six real cases');
     assert.equal(await page.locator('.proof-hash-row').count(),5,'five hashes');
     assert.match(await page.locator('.proof-source-note').innerText(),/RUNNER-REPORTED/);
     if(item.index===1){
      assert.equal(await page.locator('.proof-case-results .proof-negative').count(),6,'original all not verified');
      assert.equal(await page.locator('.proof-case-results .proof-positive').count(),6,'retest all verified');
     }
    }
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
    assert.equal(overflow,false,'no horizontal overflow for '+item.label+' at '+width);
    completed++;
    if(item.index===0 || item.index===2)await page.screenshot({path:path.join(dir,width+'-'+item.index+'-'+item.label.replaceAll(' ','-')+'.png'),fullPage:true});
   }
   assert.deepEqual(errors,[],'no JavaScript crashes');
   const download=page.waitForEvent('download',{timeout:15000});
   await page.locator('.proof-index-download a').click();
   const item=await download;
   const pathname=path.join(dir,width+'-downloaded-evidence.json');
   await item.saveAs(pathname);
   const v=JSON.parse(fs.readFileSync(pathname,'utf8'));
   assert.equal(v.schema,'blastlab.phase24.proof-index.v1');
   const want=crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'dist/proof/evidence.json'))).digest('hex');
   const got=crypto.createHash('sha256').update(fs.readFileSync(pathname)).digest('hex');
   assert.equal(got,want,'deployed evidence differs from independently checked index');
   assert.equal(v.claims.same_agent.evidence.before.observed_violations,3);
   assert.equal(v.claims.same_agent.evidence.after.observed_violations,0);
   assert.equal(v.proof_debts.length,6);
   assert.equal(v.regression.executed,240);
   await page.close();
  }
  console.log('PHASE24_PUBLIC_PROOF_BROWSER_QA_PASS',JSON.stringify({lane_checks:completed,desktop:1440,mobile:390,downloads:2,js_errors:0,overflow:false}));
 }finally{await browser.close()}
})().catch(e=>{console.error('PHASE24_PUBLIC_PROOF_BROWSER_QA_FAIL',e.stack||String(e));process.exitCode=2});
