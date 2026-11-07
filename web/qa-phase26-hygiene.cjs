/* Phase26 public hygiene review; no campaign mutations or paid inference. */
const fs=require('fs'),path=require('path');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const b=await chromium.launch({headless:true,channel:'chrome'});
 const base='https://blastlab.45-77-138-147.sslip.io';
 const tests=['/','/app','/app/campaign','/proof','/contained-sample','/judge-demo','/connect/independent-tester.md'];
 const issues=[],pages=[];
 const dir=path.join(__dirname,'qa-phase26-hygiene');fs.mkdirSync(dir,{recursive:true});
 try{
  for(const width of [1440,390]){
   const p=await b.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
   const pageErrors=[];p.on('pageerror',e=>pageErrors.push(e.message));
   for(const route of tests){
    let status='ERR',title='',h1='',links=[],invalidInputs=[],overflow=false;
    try{
     const res=await p.goto(base+route,{waitUntil:'domcontentloaded',timeout:26000});
     status=res.status();
     if(route.endsWith('.md')){
      h1=(await p.locator('body').innerText()).slice(0,100);
     }else{
      await p.locator('main,body').first().waitFor({timeout:10000});
      title=await p.title();
      h1=await p.locator('h1').allTextContents();
      const data=await p.evaluate(()=>{
        const els=[...document.querySelectorAll('input,select,textarea')].filter(el=>!el.disabled);
        const missing=els.filter(el=>{
         if(el.type==='hidden'||el.type==='submit')return false;
         const id=el.id;
         return !el.getAttribute('aria-label')&&!el.getAttribute('aria-labelledby')&&(!id||!document.querySelector('label[for="'+id+'"]'))&&!el.closest('label');
        }).map(el=>({tag:el.tagName,id:el.id,type:el.type,outer:el.outerHTML.slice(0,140)}));
        const blankButtons=[...document.querySelectorAll('button')].filter(el=>!el.getAttribute('aria-label')&&el.textContent.trim()===''&&!el.getAttribute('title')).map(el=>el.outerHTML.slice(0,140));
        const images=[...document.querySelectorAll('img')].filter(el=>el.getAttribute('alt')===null).map(el=>el.src.slice(0,130));
        const targetBlank=[...document.querySelectorAll('a[target="_blank"]')].filter(el=>!el.getAttribute('rel')?.includes('noopener')).map(el=>el.href);
        const anchors=[...document.querySelectorAll('a[href]')].filter(el=>el.href.startsWith(location.origin)).map(el=>new URL(el.href).pathname);
        const over=document.documentElement.scrollWidth>innerWidth+2;
        return {missing,blankButtons,images,targetBlank,anchors:[...new Set(anchors)],overflow:over};
      });
      invalidInputs=data.missing;
      links=data.anchors;
      overflow=data.overflow;
      if(data.missing.length||data.blankButtons.length||data.images.length||data.targetBlank.length||overflow)
       issues.push({route,width,...data});
      if(['/','/app','/proof','/contained-sample'].includes(route))
       await p.screenshot({path:path.join(dir,width+'-'+(route==='/'?'landing':route.slice(1).replaceAll('/','-'))+'.png'),fullPage:true});
     }
    }catch(e){issues.push({route,width,error:String(e).slice(0,200)})}
    pages.push({route,width,status,title,h1:Array.isArray(h1)?h1.slice(0,3):h1,linkCount:links.length,labelsMissing:invalidInputs.length,overflow});
   }
   if(pageErrors.length)issues.push({width,pageErrors});
   await p.close();
  }
 }finally{await b.close()}
 fs.writeFileSync(path.join(dir,'audit.json'),JSON.stringify({pages,issues},null,2));
 console.log('PHASE26_LIVE_AUDIT',JSON.stringify({pages,issues}).slice(0,22000));
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=2});
