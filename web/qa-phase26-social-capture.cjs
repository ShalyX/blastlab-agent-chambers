const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  const p=await browser.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1,reducedMotion:'reduce'});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  const url='http://127.0.0.1:4173/app';
  const resp=await p.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(resp.status(),200);
  await p.getByRole('heading',{name:/Bring your agent/}).waitFor({timeout:20000});
  await p.evaluate(()=>document.fonts.ready);
  const title=await p.title(); assert(title.includes('Bring Your Own Agent'));
  const image=path.join(__dirname,'public/og-card.png');
  await p.screenshot({path:image,type:'png'});
  const stats=fs.statSync(image);
  console.log('PHASE26_NEW_REAL_PRODUCT_SOCIAL_SCREENSHOT',JSON.stringify({title,path:image,bytes:stats.size,width:1200,height:630}));
  assert.deepEqual(errors,[]);
  await p.close();
 }finally{await browser.close()}
})().catch(e=>{console.error('PHASE26_SOCIAL_CAPTURE_FAIL',e.stack||String(e));process.exitCode=2});
