const path=require('path'),fs=require('fs'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const b=await chromium.connectOverCDP('http://127.0.0.1:9347',{timeout:16000});
 const p=b.contexts().flatMap(c=>c.pages()).find(p=>p.url().includes('blastlab.45-77-138-147.sslip.io/app'));
 if(!p)throw Error('Original owner browser unavailable');
 const root=path.resolve(__dirname,'../artifacts/phase23-termproof-founder');
 const report=JSON.parse(fs.readFileSync(path.join(root,'completed-report.json'),'utf8'));
 assert.equal(report.status,'complete');
 assert.equal(report.tests_completed,6);
 await p.goto('https://blastlab.45-77-138-147.sslip.io/app',{waitUntil:'domcontentloaded',timeout:45000});
 await p.locator('#byoa-connect-form').waitFor({state:'visible',timeout:30000});
 const disclosure=p.locator('.byoa-replay-disclosure').first();
 await disclosure.locator('summary').click();
 await p.locator('#byoa-replay-file').setInputFiles(path.join(root,'completed-report.json'));
 await p.getByText('Verified report loaded.',{exact:false}).waitFor({timeout:35000});
 assert.equal(await p.locator('#byoa-name').inputValue(),report.agent_name);
 assert.equal(await p.locator('#byoa-task').inputValue(),report.task);
 assert.equal(await p.locator('#byoa-success').inputValue(),report.success_contains);
 const created=p.waitForResponse(r=>r.url().endsWith('/api/agent-lab/sessions')&&r.request().method()==='POST',{timeout:60000});
 await p.getByRole('button',{name:/REPLAY ORIGINAL ATTACKS/}).click();
 const answer=await created;
 if(answer.status()!==201)throw Error('Retest campaign creation rejected HTTP '+answer.status());
 const createdJson=await answer.json();
 assert.equal(createdJson.attack_plan_sha256,report.attack_plan_sha256,'Retest plan does not match baseline');
 assert.equal(createdJson.cases_total,6);
 await p.waitForURL(/\/app\/campaign/,{timeout:30000});
 const id=createdJson.session_id;
 assert.match(id,/^[a-f0-9]{32}$/);
 let receiptPath=null;
 const download=p.waitForEvent('download',{timeout:15000});
 await p.getByRole('button',{name:/SAVE RECOVERY RECEIPT/}).click();
 const item=await download;
 receiptPath=path.join(root,'retest-recovery-receipt.private.json');
 await item.saveAs(receiptPath);
 const d=JSON.parse(fs.readFileSync(receiptPath,'utf8'));
 assert(d.recovery_key||d.recoveryKey,'Receipt key missing');
 // Do not print or commit one-time credentials.
 console.log('REAL_TERMPROOF_EXACT_RETEST_CREATED',JSON.stringify({
  retest_campaign_id:id,baseline_campaign_id:report.session_id,
  same_attack_plan:true,attack_plan_sha256:createdJson.attack_plan_sha256,
  report_recovery_receipt_saved_locally:true,cases_total:createdJson.cases_total
 }));
 await p.bringToFront();
 process.exit(0)
})().catch(e=>{console.error('RETEST_PREPARATION_FAILED',e.stack||String(e));process.exit(2)});
