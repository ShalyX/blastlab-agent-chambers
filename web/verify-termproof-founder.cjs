const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require(path.join(process.env.APPDATA,'npm','node_modules','@playwright','cli','node_modules','playwright'));
(async()=>{
 const b=await chromium.connectOverCDP('http://127.0.0.1:9347',{timeout:16000});
 const p=b.contexts().flatMap(c=>c.pages()).find(p=>p.url().includes('blastlab.45-77-138-147.sslip.io/app'));
 if(!p)throw Error('BlastLab owner campaign Chrome tab closed');
 const result=await p.evaluate(async()=>{
   const s=JSON.parse(sessionStorage.getItem('blastlab-agent-session')||'{}');
   const id=s.session_id,t=s.join_token;
   if(!/^[0-9a-f]{32}$/.test(id||'')||!t)throw Error('Missing campaign in this browser');
   const root='/api/agent-lab/sessions/'+id;
   const h={Authorization:'Bearer '+t};
   const resp=await fetch(root+'/report',{headers:h,cache:'no-store'});
   if(!resp.ok)throw Error('Report endpoint '+resp.status);
   const report=await resp.json();
   return {report,sessionId:id};
 });
 const report=result.report;
 const out=path.resolve(__dirname,'../artifacts/phase23-termproof-founder');
 fs.mkdirSync(out,{recursive:true});
 const saved=path.join(out,'completed-report.json');
 fs.writeFileSync(saved,JSON.stringify(report,null,2)+'\n',{mode:0o600});
 const cases=report.results||[];
 console.log('TERMPROOF_REPORT_FETCHED',JSON.stringify({
   status:report.status,source:report.source_type,
   tests_total:report.tests_total,tests_completed:report.tests_completed,
   breached:report.breached,plan_source:report.attack_plan_source,
   plan_sha256:report.attack_plan_sha256,
   manifest_sha256:report.manifest_sha256,
   case_summaries:cases.map(c=>({
     case_id:c.case_id||c.id,
     verdict:c.verdict||c.observed_verdict,
     answer_head:(c.agent_answer||c.answer||'').slice(0,110),
     reported_tools:(c.observed_tool_calls||c.tool_calls||[]).map(t=>t.name).slice(0,12)
   }))
 }));
 await p.reload({waitUntil:'domcontentloaded',timeout:45000});
 await p.bringToFront();
 const png=path.join(out,'real-termproof-owner-results.png');
 await p.screenshot({path:png,fullPage:true});
 console.log('REPORT_ON_DISK_PRIVATE',saved,'SCREENSHOT',png);
 process.exit(0)
})().catch(e=>{console.error('REPORT_VERIFY_ERROR',e.stack||String(e));process.exit(2)});
