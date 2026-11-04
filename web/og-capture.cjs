const path=require('path');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1,reducedMotion:'reduce'});
 await page.goto('http://127.0.0.1:4173/',{waitUntil:'domcontentloaded',timeout:30000});
 await page.evaluate(()=>document.fonts.ready);
 await page.addStyleTag({content:`
 .site-header{height:60px}
 .landing-hero{min-height:570px;height:570px}
 .hero-left{padding:58px 12px 12px 60px}
 .hero-left h1{font-size:65px;line-height:.96;margin-bottom:22px}
 .hero-copy{font-size:14px;line-height:1.55;max-width:470px}
 .hero-left .eyebrow{margin-bottom:25px}
 .hero-actions,.hero-footnote{display:none}
 .hero-art{padding:7px 45px 11px 15px}
 .art-frame{padding:15px 17px 12px}
 .art-title{margin-bottom:10px}
 .art-browser-body{padding:10px 13px}
 .art-docline{margin-bottom:5px}
 .art-datagrid{margin-top:9px;padding:4px 0}
 .art-attack{margin-top:7px;padding:7px}
 .art-boundary{padding:10px 0 19px;margin:4px 0}
 .art-cells{margin-top:8px}
 .art-cell{padding:8px;gap:4px}
 .art-cell strong{font-size:14px}
 .art-final{margin-top:8px;padding:8px}
 .art-final strong{font-size:24px}
 .art-index{margin-bottom:7px}
 .art-bottom{margin-top:8px}
 `});

 await page.screenshot({path:path.join(__dirname,'public','og-card.png'),animations:'disabled'});
 console.log('OG_CARD_CREATED',path.join(__dirname,'public','og-card.png'));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
