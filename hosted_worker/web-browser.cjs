// Controller-owned browser sidecar. Never imports submitted agent source.
const http = require('node:http');
const readline = require('node:readline');
const crypto = require('node:crypto');
const {chromium} = require(process.env.BLASTLAB_PLAYWRIGHT_MODULE || 'playwright');
let browser, server;
async function main() {
  let html = '';
  server = http.createServer((req,res) => {
    if (req.method !== 'GET' || req.url !== '/specimen') {res.writeHead(404);res.end();return;}
    res.writeHead(200, {'Content-Type':'text/html; charset=utf-8',
      'Cache-Control':'no-store', 'Content-Security-Policy':"default-src 'none'; script-src 'none'; connect-src 'none'; frame-src 'none'"});
    res.end(html);
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const url = `http://127.0.0.1:${server.address().port}/specimen`;
  browser = await chromium.launch({headless:true,
    ...(process.env.BLASTLAB_CHROME_CHANNEL ? {channel:process.env.BLASTLAB_CHROME_CHANNEL} : {})});
  for await (const line of readline.createInterface({input:process.stdin,crlfDelay:Infinity})) {
    if (line.length>32000) throw new Error('Page too large');
    const command = JSON.parse(line);
    if (Object.keys(command).join(',')!=='html' || typeof command.html!=='string') throw new Error('Invalid page');
    html = command.html;
    const context = await browser.newContext({javaScriptEnabled:false,serviceWorkers:'block',acceptDownloads:false});
    try {
      await context.route('**/*',route=>route.request().url()===url && route.request().method()==='GET'
        ? route.continue() : route.abort('blockedbyclient'));
      const page = await context.newPage();
      const response = await page.goto(url,{waitUntil:'load',timeout:15000});
      const rows = await page.locator('tr[data-stock]').evaluateAll(elements=>elements.map(el=>{
        const cells=el.querySelectorAll('td');
        return {name:cells[0].textContent,available:Number(cells[1].textContent),unit_price_cents:Number(cells[2].textContent)};
      }));
      process.stdout.write(JSON.stringify({ok:true,text:await page.locator('body').innerText(),rows,
        html_sha256:crypto.createHash('sha256').update(await response.body()).digest('hex'),browser:browser.version()})+'\n');
    } finally {await context.close();}
  }
}
const lease = setTimeout(()=>process.exit(124),600000);lease.unref();
main().catch(()=>{process.exitCode=1;}).finally(async()=>{
  if(browser) await browser.close();
  if(server) await new Promise(resolve=>server.close(resolve));
});
