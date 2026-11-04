const fs=require('fs');
const path=require('path');
const playwrightPath=path.join(process.env.APPDATA||'','npm','node_modules','@playwright','cli','node_modules','playwright');
const {chromium}=require(playwrightPath);
async function capture(){
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const files=path.join(__dirname,'qa');
 fs.mkdirSync(files,{recursive:true});
 const errors=[];
 for(const [name,url,width,height] of [
 ['landing-desktop','/',1440,900],['control-desktop','/app',1440,900],
 ['evidence-desktop','/app/evidence',1440,900],['architecture-desktop','/app/architecture',1440,900],
 ['landing-mobile','/',390,844],['control-mobile','/app',390,844]]) {
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1,reducedMotion:'reduce'});
  page.on('pageerror',e=>errors.push(name+': '+e.message));
  page.on('console',e=>{if(e.type()==='error')errors.push(name+' console: '+e.text().slice(0,150))});
  try{
   await page.goto((process.env.BLASTLAB_BASE_URL||'http://127.0.0.1:4173')+url,{waitUntil:'networkidle',timeout:35000});
   await page.waitForTimeout(500);
   await page.screenshot({path:path.join(files,name+'.png'),fullPage:true});
   const info=await page.evaluate(()=>({title:document.title,scrollWidth:document.documentElement.scrollWidth,innerWidth:window.innerWidth,height:document.body.scrollHeight,rootLength:document.querySelector('#root')?.textContent?.length}));
   console.log(JSON.stringify({name,url,...info,horizontal_overflow:info.scrollWidth>info.innerWidth}));
   if(name==='control-desktop'){
    await page.getByRole('button',{name:/ADVERSARIAL REPLAY/}).click();
    await page.waitForTimeout(700);
    const fixtureText=await page.locator('body').innerText();
    console.log(JSON.stringify({action:'switch-to-scripted',hasScriptedTruth:fixtureText.includes('SCRIPTED FIXTURE'),hasDeniedCount:fixtureText.includes('4 denied')||fixtureText.includes('4 policy')||fixtureText.includes('4')}));
    const scrubber=page.getByRole('slider',{name:'Scrub recorded events'});
    await scrubber.fill('9');
    await page.waitForTimeout(250);
    await page.screenshot({path:path.join(files,'control-scripted-stage.png'),fullPage:true});
    await page.getByRole('button',{name:'Policy' ,exact:true}).first().click().catch(()=>{});
   }
  }catch(e){errors.push(name+' capture: '+e.message.slice(0,280))}
  await page.close();
 }
 await browser.close();
 console.log('QA_ERRORS='+JSON.stringify(errors));
}
capture().catch(e=>{console.error('QA_FATAL='+e.stack);process.exitCode=1});
