const path=require('path'),fs=require('fs'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const base=process.env.BLASTLAB_BASE_URL||'http://127.0.0.1:4173';
 const folder=path.join(__dirname,'qa-chambers');fs.mkdirSync(folder,{recursive:true});
 const errs=[],checks=[];
 for(const [name,url,width,height] of [
 ['library-desktop','/app',1440,900],['setup-desktop','/app/chambers/web',1440,900],['results-desktop','/app/results',1440,900],
 ['control-desktop','/app/control',1440,900],['library-mobile','/app',390,844],['setup-mobile','/app/chambers/web',390,844],
 ['results-mobile','/app/results',390,844]
 ]){
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1,reducedMotion:'reduce'});
  page.on('pageerror',e=>errs.push(name+': '+e.message));
  try{
    await page.goto(base+url,{waitUntil:'domcontentloaded',timeout:25000});
    await page.waitForTimeout(750);
    if(name.startsWith('setup')) {
      await page.getByRole('button',{name:/Low-stock exposure/}).click();
      await page.getByRole('button',{name:/Receipt forgery/}).click();
    }
    await page.screenshot({path:path.join(folder,name+'.png'),fullPage:true,timeout:25000});
    const state=await page.evaluate(()=>({
      width:document.documentElement.scrollWidth,viewport:innerWidth,
      text:document.body.innerText.slice(0,220),
      title:document.title
    }));
    checks.push({name,overflow:state.width>state.viewport,...state});
    assert.equal(state.width,state.viewport,name+' x overflow');
    if(name==='library-desktop'){
      assert.match(await page.locator('body').innerText(),/Choose the/);
      assert.equal(await page.getByText('NOT IMPLEMENTED',{exact:true}).count(),4);
      await page.getByRole('button',{name:/ENTER WEB CHAMBER/}).click();
      await page.waitForURL('**/app/chambers/web');
      assert.match(await page.locator('body').innerText(),/Choose the page attack/);
    }
    if(name==='setup-desktop'){
      assert.equal(await page.getByRole('button',{name:/Low-stock exposure/}).getAttribute('aria-pressed'),'true');
      assert.equal(await page.getByRole('button',{name:/Receipt forgery/}).getAttribute('aria-pressed'),'true');
      assert.match(await page.locator('body').innerText(),/low-stock|Low-stock/);
    }
    if(name==='results-desktop'){
      assert.match(await page.locator('body').innerText(),/BLAST RADIUS|Blast Radius/i);
    }
  }catch(e){errs.push(name+' FAIL: '+String(e).slice(0,260))}
  await page.close();
 }
 await browser.close();
 console.log('CHAMBER_VISUAL='+JSON.stringify(checks));
 console.log('CHAMBER_ERRORS='+JSON.stringify(errs));
 process.exitCode=errs.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
