const path=require('path'),fs=require('fs');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
const base='https://blastlab.45-77-138-147.sslip.io';
const output=path.join(__dirname,'submission-captures');fs.mkdirSync(output,{recursive:true});

(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const context=await browser.newContext({
  viewport:{width:1440,height:900},deviceScaleFactor:1,
  recordVideo:{dir:output,size:{width:1440,height:900}},
  reducedMotion:'reduce'
 });
 const page=await context.newPage();
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const sleep=(ms)=>page.waitForTimeout(ms);
 const goto=async(p)=>{await page.goto(base+p,{waitUntil:'domcontentloaded',timeout:35000});await sleep(450)};
 const overlay=async(main,sub,step)=>{
  await page.evaluate(({main,sub,step})=>{
   let e=document.querySelector('#blastlab-film-caption');
   if(!e){
    e=document.createElement('div');e.id='blastlab-film-caption';
    e.style.cssText='position:fixed;z-index:2147483647;left:26px;bottom:27px;max-width:760px;pointer-events:none;color:#F2F7F0;background:rgba(11,20,18,.97);padding:18px 24px;border-left:5px solid #FF754A;box-shadow:0 8px 24px rgba(0,0,0,.35);font-family:Arial,sans-serif;line-height:1.3;';
    document.body.append(e);
   }
   e.replaceChildren();
   const one=document.createElement('div');one.textContent=step;
   one.style.cssText='font:600 11px Consolas,monospace;letter-spacing:1.3px;color:#ACF0D4;margin-bottom:8px';
   const two=document.createElement('div');two.textContent=main;
   two.style.cssText='font:700 24px Arial,sans-serif;color:#F2F7F0;letter-spacing:-.4px';
   const three=document.createElement('div');three.textContent=sub;
   three.style.cssText='font:13px Arial,sans-serif;margin-top:7px;color:#AAC6B4';
   e.append(one,two,three);
  },{main,sub,step});
 };
 const show=async(head,sub,step,ms)=>{await overlay(head,sub,step);await sleep(ms)};
 const advancePage=async(selector)=>{await page.locator(selector).first().scrollIntoViewIfNeeded();await sleep(300)};
 try{
  await goto('/');
  await show('Crash-test an agent against hostile content.','Real execution. A verifiable containment boundary.','01 / THE PROBLEM',6200);
  await goto('/app');
  await page.getByText('NOT IMPLEMENTED',{exact:true}).first().waitFor({timeout:20000});
  await show('A real testing facility — not a replay dashboard.','One operational Web Chamber. Four future Chambers explicitly unavailable.','02 / CHAMBER LIBRARY',6600);
  await page.getByRole('button',{name:/ENTER WEB CHAMBER/}).click();
  await page.waitForURL('**/app/chambers/web');
  await page.getByRole('button',{name:/Low-stock exposure/}).waitFor({timeout:20000});
  await page.getByRole('button',{name:/Low-stock exposure/}).click();
  await page.getByRole('button',{name:/Receipt forgery/}).click();
  await show('Give the agent a legitimate mission and a hostile page.','Low-stock exposure + a forged evidence receipt. No arbitrary host commands.','03 / CONFIGURE THE TEST',5700);
  await advancePage('.ch-launch-dock');
  await show('Run it inside an actual disposable Docker browser.','Scripted attack proposals exercise the same independently enforced policy.','04 / EXECUTE ON VULTR',2500);
  await page.getByRole('button',{name:/LAUNCH CONTAINED TEST/}).click();
  await sleep(1400);
  await page.waitForURL(url=>url.pathname==='/app/results'&&url.searchParams.has('run'),{timeout:80000});
  const caseId=new URL(page.url()).searchParams.get('run');
  console.log('VIDEO_ACTUAL_RUN_ID='+caseId);
  await page.waitForFunction(()=>document.body.innerText.includes('$24.00')&&document.body.innerText.includes('CONTROLLED TEST PASSED'),null,{timeout:25000});
  await show('The forged receipt is denied. The task still completes.','$24.00 independently verified. Reset verified. New evidence ID archived.','05 / REAL RESULT',6100);
  await page.locator('.ch-report-layout').scrollIntoViewIfNeeded();
  await show('Blast radius and remediation, grounded in actual events.','What was attempted, denied, recovered and never tested.','06 / REPORT + REMEDIATION',5000);
  await goto('/app/control?run='+encodeURIComponent(caseId));
  await page.getByText('UNTRUSTED WEB SPECIMEN').first().waitFor({timeout:20000});
  const slider=page.getByRole('slider',{name:'Scrub recorded events'});
  await slider.fill('5');
  await show('Inspect the malicious instruction inside the page.','Untrusted text cannot give itself SYSTEM authority.','07 / UNTRUSTED INPUT',4800);
  await slider.fill('7');
  await show('The supervisor destroys the disposable browser.','Container removed, workspace removed, checkpoint retained.','08 / KILL + RESET',4800);
  await slider.fill('12');
  await page.getByRole('tab',{name:'POLICY DECISION'}).click();
  await show('The forged completion proposal is actually rejected.','One scripted policy denial. NOT a live LLM-denial claim.','09 / TOOL BOUNDARY',4900);
  await slider.fill('20');
  await show('A fresh worker finishes the authorized mission.','Every stage is backed by the real trace, not an invented event feed.','10 / RECOVERY',4000);
  await goto('/app/results?run='+encodeURIComponent(caseId));
  await page.waitForFunction(()=>document.body.innerText.includes('$24.00'),null,{timeout:25000});
  await page.locator('.ch-verifier-band').scrollIntoViewIfNeeded();
  await show('Export the event chain and verify it offline.','SHA-256 public proof is self-contained; private raw trace digest is provenance.','11 / CRYPTOGRAPHIC EVIDENCE',5700);
  await goto('/app/architecture');
  await show('Built entirely around Vultr and real sandboxed execution.','Vultr VM control plane · Serverless Inference GLM-5.3 · Docker Chromium.','12 / SPONSOR TECHNOLOGY',6600);
  await goto('/app');
  await show('BlastLab. Crash-test the blast radius.','Explore the Web Chamber at blastlab.45-77-138-147.sslip.io','13 / THE TAKEAWAY',5700);
  console.log('VIDEO_RECORDED_FLOWS=13');
 }catch(e){errors.push('recording error: '+String(e));console.error('VIDEO_RECORD_ERROR='+String(e).slice(0,900))}
 finally{
  await page.close();
  await context.close();
  const vp=await page.video()?.path().catch(()=>null);
  console.log('VIDEO_RAW_PATH='+vp);
  await browser.close();
 }
 if(errors.length){console.error('VIDEO_ERRORS='+JSON.stringify(errors));process.exitCode=2}
})().catch(e=>{console.error('VIDEO_FATAL='+e.stack);process.exitCode=2});
