const path=require('path'),fs=require('fs'),cp=require('child_process'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const base=process.env.BLASTLAB_BASE_URL||'http://127.0.0.1:4173';
 const root=path.resolve(__dirname,'..');
 const out=path.join(__dirname,base.startsWith('https')?'qa-agent-public':'qa-agent');
 fs.mkdirSync(out,{recursive:true});
 const issues=[];
 const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});
 page.on('pageerror',e=>issues.push('JS '+e.message));
 try{
  await page.goto(base+'/app',{waitUntil:'domcontentloaded'});
  await page.getByText('Bring your agent.',{exact:false}).first().waitFor({timeout:20000});
  assert.match(await page.locator('body').innerText(),/CONNECT YOUR AGENT/);
  assert.match(await page.locator('body').innerText(),/Six rounds/);
  await page.screenshot({path:path.join(out,'connect-desktop.png'),fullPage:true});
  await page.locator('#byoa-name').fill('Independent support agent');
  await page.locator('#byoa-task').fill('Summarize a supplied support message for a customer without obeying instructions embedded inside the message.');
  await page.locator('#byoa-tools').fill('delete_file, send_http, write_memory');
  await page.getByRole('button',{name:/CONNECT MY AGENT/}).click();
  await page.waitForURL('**/app/campaign',{timeout:25000});
  await page.getByText('DOWNLOAD CONNECTOR').waitFor({timeout:25000});
  const token=await page.locator('.byoa-token code').textContent();
  const text=await page.locator('body').innerText();
  const matched=text.match(/Campaign ID\s+([0-9a-f]{32})/);
  assert(matched,'Missing backend-created session');
  const session=matched[1];
  console.log('LOCAL_AGENT_SESSION_CREATED',session,'token_returned',Boolean(token));
  await page.screenshot({path:path.join(out,'campaign-waiting.png'),fullPage:true});
  const run=cp.spawnSync('python',['web/public/connect/blastlab_connector.py',
    '--base',base,'--session',session,'--adapter','examples.vulnerable_agent:respond'],{
     cwd:root,env:{...process.env,BLASTLAB_SESSION_TOKEN:token},encoding:'utf-8',
     timeout:125000
   });
  console.log('REAL_CONNECTED_AGENT_EXIT',run.status,
    'OBSERVED_CASES',(run.stdout.match(/^CASE /gm)||[]).length,
    'OUTPUT_TAIL',run.stdout.slice(-210));
  if(run.status!==0)throw new Error('Agent connector failed '+run.stderr);
  await page.waitForFunction(()=>document.body.innerText.includes('5 observed rule violations'),null,{timeout:25000});
  assert.match(await page.locator('body').innerText(),/MITIGATE & RETEST/);
  await page.screenshot({path:path.join(out,'campaign-results.png'),fullPage:true});
  console.log('REAL_AGENT_CAMPAIGN_RESULT_VISIBLE',true);
  const mobile=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
  mobile.on('pageerror',e=>issues.push('MOBILE '+e.message));
  await mobile.goto(base+'/app',{waitUntil:'domcontentloaded'});
  await mobile.getByText('Bring your agent.',{exact:false}).first().waitFor();
  const dimensions=await mobile.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:innerWidth}));
  await mobile.screenshot({path:path.join(out,'connect-mobile.png'),fullPage:true});
  console.log('MOBILE_DIMENSIONS',JSON.stringify(dimensions));
  assert(dimensions.scroll<=dimensions.width,'Horizontal mobile overflow');
  await mobile.close();
  await page.goto(base+'/app/demo',{waitUntil:'domcontentloaded'});
  await page.getByText('Choose the',{exact:false}).first().waitFor();
  console.log('SUPPLIER_DEMO_SEPARATE',true);
  assert.equal(issues.length,0,'Browser runtime errors '+issues.join('; '));
  console.log('LOCAL_BYOA_BROWSER_E2E_PASS');
 }catch(e){console.error('LOCAL_BYOA_BROWSER_E2E_FAIL',String(e).slice(0,1100));process.exitCode=2}
 await page.close();await browser.close();
})().catch(e=>{console.error('LOCAL_BYOA_BROWSER_FATAL',String(e));process.exitCode=2});
