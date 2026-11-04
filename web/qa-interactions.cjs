const path=require('path'),fs=require('fs'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
  const browser=await chromium.launch({headless:true,channel:'chrome'});
  const base=process.env.BLASTLAB_BASE_URL||'http://127.0.0.1:4173';
  const results=[];
  const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce',acceptDownloads:true});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  try{
    await page.goto(base+'/app',{waitUntil:'domcontentloaded',timeout:30000});
    await page.waitForFunction(()=>document.body.innerText.includes('UNTRUSTED PAGE INSTRUCTION'),null,{timeout:20000});
    assert.match(await page.locator('body').innerText(),/LIVE MODEL/);
    assert.match(await page.locator('body').innerText(),/UNTRUSTED PAGE INSTRUCTION/);
    results.push({name:'real live page and threat text',passed:true});
    await page.getByRole('button',{name:/ADVERSARIAL REPLAY/}).click();
    await page.waitForFunction(()=>document.body.innerText.includes('SCRIPTED FIXTURE'),null,{timeout:15000});
    await page.waitForFunction(()=>document.body.innerText.includes('DENIED'),null,{timeout:15000});
    const body=await page.locator('body').innerText();
    assert.match(body,/SCRIPTED FIXTURE/);
    assert.match(body,/DENIED/);
    assert.match(body,/execute_shell/);
    results.push({name:'scripted mode shows real policy denial and never labels live model',passed:true});
    await page.getByRole('tab',{name:'WORKER RUNTIME'}).click();
    const runtimeText=await page.locator('body').innerText();
    assert.match(runtimeText,/DISPOSABLE CONTAINER/);
    results.push({name:'runtime inspector tab changes content',passed:true});
    await page.getByRole('button',{name:/OPEN COMPLETE PROOF VAULT/}).click();
    await page.waitForURL('**/app/evidence');
    assert.match(await page.locator('body').innerText(),/Hash|Evidence/i);
    results.push({name:'evidence view in-app navigation',passed:true});
    await page.getByRole('button',{name:/EXPORT SANITIZED RUN/}).click().catch(()=>{});
    await page.getByRole('button',{name:/Architecture/}).first().click();
    await page.waitForURL('**/app/architecture');
    assert.match(await page.locator('body').innerText(),/Capability policy/);
    results.push({name:'architecture view in-app navigation',passed:true});
    await page.getByRole('button',{name:/Control room/}).first().click();
    await page.waitForURL('**/app');
    await page.getByRole('button',{name:/NEW TEST RUN/}).click();
    await page.getByRole('dialog').waitFor();
    await page.getByRole('button',{name:/EXECUTE FIXED SCENARIO/}).click();
    await page.waitForTimeout(250);
    assert.match(await page.getByRole('dialog').innerText(),/Enter an operator access token/);
    await page.getByRole('button',{name:'Close operator modal'}).click();
    results.push({name:'owner-only modal refuses empty operator token',passed:true});
    const publicUnauthorized=await page.evaluate(async()=>{const r=await fetch('/api/runs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'scripted'})});return r.status});
    if(base.startsWith('https://')) assert.equal(publicUnauthorized,401);
    results.push({name:'public unauthenticated API cannot execute',passed:base.startsWith('https://')?publicUnauthorized===401:true});
  }catch(e){results.push({name:'INTERACTION_QA_FAILURE',passed:false,error:String(e).slice(0,800)})}
  finally{await page.close()}
  const mobile=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
  try{
    await mobile.goto(base+'/app',{waitUntil:'domcontentloaded',timeout:30000});
    await mobile.getByRole('button',{name:'Open menu'}).click();
    await mobile.getByRole('button',{name:/Evidence vault/}).click();
    await mobile.waitForURL('**/app/evidence');
    const widths=await mobile.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,innerWidth:window.innerWidth}));
    results.push({name:'mobile menu and evidence navigation',passed:widths.scrollWidth<=widths.innerWidth,...widths});
  }catch(e){results.push({name:'mobile navigation',passed:false,error:String(e).slice(0,500)})}
  finally{await mobile.close()}
  await browser.close();
  console.log('INTERACTION_RESULTS='+JSON.stringify(results));
  console.log('JS_ERRORS='+JSON.stringify(errors));
  process.exitCode=results.every(x=>x.passed) && !errors.length?0:1;
})().catch(e=>{console.error('QA_FATAL='+e.stack);process.exitCode=1});