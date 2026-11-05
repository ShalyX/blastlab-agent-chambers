const path=require('path');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});
 const issues=[];page.on('pageerror',e=>issues.push(String(e.message)));
 const base='https://blastlab.45-77-138-147.sslip.io';
 const headings=async()=>page.locator('h1,h2').allTextContents();
 const first=async()=>page.evaluate(()=>document.body.innerText.slice(0,1500));
 for(const target of ['/','/app','/app/chambers/web','/app/results?run=scripted-99bb851e7f39b5ba82','/app/results?run=live-fc49cc39d3fba372b5']){
   let result={target};
   try{
    const response=await page.goto(base+target,{waitUntil:'domcontentloaded',timeout:35000});
    await page.waitForTimeout(900);
    result.http=response.status();result.title=await page.title();
    result.h1=(await page.locator('h1').allTextContents()).slice(0,2);
    result.first_screen=await first();
    result.horizontal_overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth);
    result.console_errors=issues.splice(0);
   }catch(e){result.ERROR=String(e).slice(0,280)}
   console.log('BLIND_JUDGE_'+target+'='+JSON.stringify(result));
 }
 await page.goto(base+'/app/chambers/web',{waitUntil:'domcontentloaded'});
 await page.getByRole('button',{name:/Live Vultr GLM-5.3/}).click();
 const liveText=(await page.locator('body').innerText());
 console.log('JUDGE_LIVE_ACCESS='+JSON.stringify({requires_token:liveText.includes('OPERATOR ACCESS'),public_mode:liveText.includes('Scripted attack fixture'),selected_mode:liveText.slice(-950)}));
 const duration=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});
 await duration.goto(base+'/app',{waitUntil:'domcontentloaded'});
 const links=await duration.locator('a[href]').evaluateAll(nodes=>nodes.slice(0,25).map(n=>({text:n.textContent?.trim().slice(0,70),href:n.getAttribute('href')})));
 console.log('JUDGE_PUBLIC_LINKS='+JSON.stringify(links));
 await browser.close();
})().catch(e=>{console.log('JUDGE_BROWSER_FATAL='+e.stack);process.exitCode=2});
