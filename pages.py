"""Local demo pages. Untrusted text is rendered only with textContent."""

STYLE = '''<style>
*{box-sizing:border-box}body{font:17px/1.6 system-ui,sans-serif;background:#f4f3ed;color:#182c33;margin:0}
main{max-width:1060px;margin:50px auto;padding:0 28px}nav{display:flex;gap:24px;border-bottom:1px solid #c8cfca;padding-bottom:18px}
a{color:#13655e}h1{font-size:48px;line-height:1.1;letter-spacing:-2px;margin:36px 0 14px}h2{line-height:1.2}
.eyebrow{font-size:12px;letter-spacing:2px;text-transform:uppercase}.card{background:#fff;border:1px solid #d0d5ce;border-radius:12px;padding:24px;margin:20px 0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.grid .card{margin:0}label{display:block;font-weight:600}
input,textarea,button{font:inherit;padding:12px;border:1px solid #a6b9b0;border-radius:6px}textarea{display:block;width:100%;min-height:98px;margin:10px 0}
input{width:110px}button{background:#175f58;color:white;cursor:pointer}button:disabled{opacity:.6}output{display:block;margin-top:16px}
.amount{font-size:42px;font-weight:650;letter-spacing:-1px}.muted{color:#50656a}.pass{color:#086748;font-weight:650}.fail{color:#a23b25;font-weight:650}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;background:#eff2ed;padding:16px;border-radius:6px}
.event{padding:14px 0;border-bottom:1px solid #d8ded7}.event strong{display:block}.event p{margin:5px 0}
@media(max-width:700px){main{margin:24px auto}.grid{grid-template-columns:1fr}h1{font-size:38px}}
</style>'''


def page(route):
    head = ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>REPRO / BLASTLAB · Local spikes</title>' + STYLE + '<main>'
            '<nav><a href="/">Local spikes</a><a href="/repro">REPRO</a>'
            '<a href="/blastlab">BLASTLAB</a></nav>')
    if route == '/':
        return head + '''<p class="eyebrow">Two working feasibility spikes</p><h1>Watch the useful part happen.</h1>
<p>Local execution. No credentials. No model API.</p><div class="grid">
<section class="card"><h2>REPRO</h2><p>A bug report becomes an executed reproduction with expected-versus-actual evidence.</p><a href="/repro">Open the buggy mug shop →</a></section>
<section class="card"><h2>BLASTLAB</h2><p>A stock mission encounters hostile supplier text, survives a controlled interruption, and finishes after reset.</p><a href="/blastlab">Inspect the completed mission →</a></section></div>
<p class="muted">Both runners use deterministic adapters. These spikes demonstrate execution, not general autonomous reasoning.</p></main></html>'''
    if route == '/repro':
        return head + '''<p class="eyebrow">REPRO / report → execution → evidence</p><h1>Make the bug show itself.</h1>
<p>The local mug shop has an intentional total bug. Change the quantity and compare the displayed total.</p>
<section class="card"><h2>Mug shop</h2><p>Stoneware mug · $12.00 each</p>
<label for="qty">Quantity</label><input id="qty" type="number" min="1" max="10" value="1">
<button id="update" type="button">Update cart</button><output id="cart" aria-live="polite"></output></section>
<section class="card"><h2>Reproduce from a report</h2><label for="report">Bug report</label>
<textarea id="report">When I add two mugs to my cart, the total still shows the price of one.</textarea>
<button id="run" type="button">Run reproduction</button><output id="verdict" aria-live="polite"></output>
<details><summary>Executed HTTP evidence</summary><pre id="evidence">Run a reproduction to collect evidence.</pre></details></section>
<p class="muted">Supported: one quantity 2–10 next to “mugs” or after “quantity/qty”, plus a total, cost, or price issue. Ambiguous reports are rejected. No LLM.</p>
<script>
const $=id=>document.getElementById(id), money=c=>'$'+(c/100).toFixed(2);
async function cart(){try{const r=await fetch('/api/cart?quantity='+encodeURIComponent($('qty').value)),x=await r.json();if(!r.ok)throw Error(x.error);$('cart').textContent=x.quantity+' mug(s) · Total '+money(x.total_cents);}
catch(e){$('cart').textContent=e.message;}}
$('update').onclick=cart;cart();
$('run').onclick=async()=>{ $('run').disabled=true;$('verdict').textContent='Executing baseline and reported quantity…';
try{const r=await fetch('/api/repro?report='+encodeURIComponent($('report').value)),x=await r.json();if(!r.ok)throw Error(x.error);
$('verdict').className=x.reproduced?'fail':'pass';$('verdict').textContent=x.reproduced?'Bug reproduced. Expected '+money(x.expected_cents)+' · Observed '+money(x.actual_cents):'Verdict: '+x.verdict;
$('evidence').textContent=JSON.stringify(x,null,2);}catch(e){$('verdict').textContent=e.message;$('evidence').textContent='No reproduction evidence generated.';}finally{$('run').disabled=false;}};
</script></main></html>'''
    return head + '''<p class="eyebrow">BLASTLAB / mission → interruption → recovery</p><h1>Finish the mission after reset.</h1>
<p>Calculate the total value of available supplier stock. The supplier feed contains hostile instructions.</p>
<div class="grid"><section class="card"><h2>Mission result</h2><div id="total" class="amount">Loading…</div><p id="summary" aria-live="polite"></p></section>
<section class="card"><h2>Containment evidence</h2><p id="checks">Reading the latest local run…</p><p class="muted">The trusted interruption uses reversible moves of two fixed files inside a disposable child. No deletion or shell commands.</p></section></div>
<section class="card"><h2>Supplier note · untrusted</h2><pre id="note"></pre></section>
<section class="card"><h2>Executed timeline</h2><div id="timeline"></div></section>
<details><summary>Raw execution evidence</summary><pre id="evidence"></pre></details>
<p class="muted">Origin-based capability checks enforce each tool decision. The hostile request is blocked; a separate trusted scenario exercises recovery. No LLM susceptibility measurement.</p>
<script>
const $=id=>document.getElementById(id);
fetch('/api/evidence').then(async r=>{const x=await r.json();if(!r.ok)throw Error('No run evidence. Restart with python spikes.py serve.');const b=x.blastlab;
$('total').textContent='$'+(b.total_value_cents/100).toFixed(2);$('summary').textContent=b.mission_completed?'Mission completed from the restored checkpoint.':'Mission incomplete';
$('checks').textContent='Reset hashes '+(b.reset_verified?'verified':'FAILED')+' · Outside-child sentinel '+(b.parent_sentinel.unchanged?'unchanged':'CHANGED');
$('note').textContent=b.http_evidence[0].body.supplier_note;$('evidence').textContent=JSON.stringify(x,null,2);
for(const e of b.events){const row=document.createElement('div');row.className='event';const title=document.createElement('strong');title.textContent=String(e.seq).padStart(2,'0')+' · '+e.event.replaceAll('_',' ');row.append(title);
const detail=document.createElement('p');detail.className=e.decision==='deny'?'fail':'muted';detail.textContent=e.decision?e.decision.toUpperCase()+' · '+e.action+' · '+e.origin:(e.mechanism||e.reason||(e.total_value_cents!==undefined?'Stock value: $'+(e.total_value_cents/100).toFixed(2):e.at));row.append(detail);$('timeline').append(row);}
}).catch(e=>{$('summary').textContent=e.message;$('total').textContent='Unavailable';});
</script></main></html>'''
