import json, os

with open('mentores_final.min.json', 'r', encoding='utf-8') as f:
    minified = f.read()

# Read the template HTML (without DATA)
template = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mentores haCARthon</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',system-ui,-apple-system,sans-serif;background:#0d0d2b;color:#e0e0f0;padding:20px;min-height:100vh}
.container{max-width:1200px;margin:0 auto}
.header{display:flex;align-items:center;gap:14px;margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.06)}
.header h1{font-size:1.3rem;font-weight:800;color:#fff;letter-spacing:-.5px}
.header .badge{background:#ff6b4a;color:#fff;font-size:.65rem;font-weight:700;padding:4px 10px;border-radius:20px;text-transform:uppercase;letter-spacing:.5px}
.header .sub{color:rgba(255,255,255,.4);font-size:.8rem;margin-left:auto}
.tag-filter-area{margin-bottom:24px;background:rgba(255,255,255,.04);border-radius:16px;padding:20px}
.tag-filter-group{margin-bottom:16px}
.tag-filter-group:last-child{margin-bottom:0}
.tag-filter-group .label{font-size:.7rem;font-weight:700;color:rgba(255,255,255,.35);margin-bottom:10px;text-transform:uppercase;letter-spacing:.8px}
.tag-filter-group .tags{display:flex;flex-wrap:wrap;gap:6px}
.tag-btn{display:inline-flex;align-items:center;gap:5px;padding:6px 14px;border-radius:20px;border:1.5px solid rgba(255,255,255,.1);background:rgba(255,255,255,.04);color:rgba(255,255,255,.7);font-size:.78rem;cursor:pointer;user-select:none;font-family:'Inter',sans-serif;font-weight:500;transition:all .2s}
.tag-btn:hover{border-color:rgba(255,255,255,.2);background:rgba(255,255,255,.08);color:#fff}
.tag-btn.active{background:#ff6b4a;color:#fff;border-color:#ff6b4a}
.tag-btn.active:hover{background:#ff5833}
.tag-btn .count{font-size:.65rem;opacity:.6}
.search-area{margin-bottom:20px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.search-area input{padding:10px 18px;border:1.5px solid rgba(255,255,255,.1);border-radius:12px;font-size:.85rem;width:100%;max-width:380px;outline:none;background:rgba(255,255,255,.06);color:#fff;font-family:'Inter',sans-serif;transition:border-color .2s}
.search-area input::placeholder{color:rgba(255,255,255,.25)}
.search-area input:focus{border-color:#ff6b4a;background:rgba(255,255,255,.08)}
.stats{font-size:.8rem;color:rgba(255,255,255,.4);margin-bottom:14px;font-weight:500}
.contato-rapido{margin-bottom:20px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.contato-rapido button{padding:8px 18px;border:none;border-radius:10px;background:linear-gradient(135deg,#ff6b4a,#ff8a6f);color:#fff;font-size:.8rem;cursor:pointer;font-weight:600;font-family:'Inter',sans-serif;transition:all .2s}
.contato-rapido button:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(255,107,74,.35)}
.table-wrapper{background:rgba(255,255,255,.04);border-radius:16px;overflow-x:auto;border:1px solid rgba(255,255,255,.06)}
table{width:100%;border-collapse:collapse}
th{background:rgba(255,255,255,.06);color:rgba(255,255,255,.5);padding:8px 8px;text-align:left;font-size:.65rem;font-weight:700;white-space:nowrap;text-transform:uppercase;letter-spacing:.4px}
td{padding:8px 8px;font-size:.75rem;border-bottom:1px solid rgba(255,255,255,.04);color:rgba(255,255,255,.8);vertical-align:top}
tr:hover td{background:rgba(255,255,255,.04)}
tr:last-child td{border-bottom:none}
td a{color:#ff8a6f;text-decoration:none;font-weight:500;font-size:.7rem;word-break:break-all}
td a:hover{color:#ff6b4a;text-decoration:underline}
.tag{display:inline-block;background:rgba(255,255,255,.08);color:rgba(255,255,255,.8);padding:2px 7px;border-radius:8px;font-size:.62rem;margin:1px;cursor:pointer;transition:all .15s;font-weight:500}
.tag:hover{background:rgba(255,255,255,.15);color:#fff}
.tag-desafio{background:rgba(255,107,74,.15);color:#ff8a6f}
.tag-desafio:hover{background:rgba(255,107,74,.3);color:#ff6b4a}
.tag-info{background:rgba(46,125,50,.2);color:#81c784}
.tag-info:hover{background:rgba(46,125,50,.35);color:#a5d6a7}
.copy-btn{background:rgba(255,255,255,.08);color:rgba(255,255,255,.7);border:none;padding:3px 8px;border-radius:6px;cursor:pointer;font-size:.65rem;font-family:'Inter',sans-serif;font-weight:500;transition:all .2s}
.copy-btn:hover{background:rgba(255,255,255,.14);color:#fff}
.pagination{display:flex;justify-content:center;align-items:center;gap:10px;margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,.06)}
.pagination button{padding:7px 16px;border:1px solid rgba(255,255,255,.1);border-radius:10px;background:rgba(255,255,255,.04);color:rgba(255,255,255,.6);cursor:pointer;font-family:'Inter',sans-serif;font-size:.8rem;font-weight:500;transition:all .2s}
.pagination button:hover:not(:disabled){background:rgba(255,255,255,.1);color:#fff;border-color:rgba(255,255,255,.2)}
.pagination button:disabled{opacity:.3;cursor:default}
.pagination span{font-size:.8rem;color:rgba(255,255,255,.4)}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>haCARthon</h1>
<span class="badge">Mentores</span>
<span class="sub">88 mentores cadastrados</span>
</div>
<div class="tag-filter-area" id="filterArea"></div>
<div class="search-area">
<input type="text" id="filterSearch" placeholder="Buscar nome, email, cidade...">
<button class="contato-rapido" onclick="copiarTodosVisiveis()">Copiar contatos visiveis</button>
</div>
<div class="stats" id="stats"></div>
<div class="table-wrapper">
<table>
<thead><tr>
<th>Nome</th><th>Email</th><th>Telefone</th><th>Discord</th><th>Estado</th><th>Especialidades</th><th>Info</th><th>Desafios</th><th>Acoes</th>
</tr></thead>
<tbody id="tbody"></tbody>
</table>
</div>
<div class="pagination" id="pagination"></div>
</div>
<script>
var DATA = __DATA__;

const N = 25;
var pg = 1;
var sel = {e:new Set(), d:new Set(), i:new Set()};

function $(s){return document.querySelector(s)}
function $$(s){return document.querySelectorAll(s)}

function init(){
  render();
}

function esp(r){
  return (r['\u00c1rea de atua\u00e7\u00e3o/conhecimento/especialidade (escolha at\u00e9 3 op\u00e7\u00f5es) *']||'').split(';').map(function(s){return s.trim()}).filter(Boolean);
}

function des(r){
  return (r['Qual dos desafios você acredita que pode colaborar com as equipes? Selecione em ordem de prioridade e fique à vontade para selecionar quantos desejar. *']||'').split(';').map(function(s){return s.trim().replace(/^DESAFIO \d: /,'')}).filter(Boolean);
}

function inf(r){
  var v = (r['Informe qual *']||'').trim();
  return v ? [v] : [];
}

function contar(){
  var ec={},dc={},ic={};
  DATA.forEach(function(r){
    esp(r).forEach(function(e){ec[e]=(ec[e]||0)+1});
    des(r).forEach(function(d){dc[d]=(dc[d]||0)+1});
    inf(r).forEach(function(i){ic[i]=(ic[i]||0)+1});
  });
  return {e:Object.entries(ec).sort(function(a,b){return b[1]-a[1]}), d:Object.entries(dc).sort(function(a,b){return b[1]-a[1]}), i:Object.entries(ic).sort(function(a,b){return b[1]-a[1]})};
}

function montarFiltros(){
  var c=contar();
  var h='<div class="tag-filter-group"><div class="label">Especialidades</div><div class="tags">';
  c.e.forEach(function(x){
    var t=x[0],n=x[1],a=sel.e.has(t)?'active':'';
    h+='<button class="tag-btn '+a+'" data-g="e" data-t="'+esc(t)+'">'+esc(t)+' <span class="count">('+n+')</span></button>';
  });
  h+='</div></div><div class="tag-filter-group"><div class="label">Desafios</div><div class="tags">';
  c.d.forEach(function(x){
    var t=x[0],n=x[1],a=sel.d.has(t)?'active':'';
    h+='<button class="tag-btn '+a+'" data-g="d" data-t="'+esc(t)+'">'+esc(t.replace(/^DESAFIO \d: /,''))+' <span class="count">('+n+')</span></button>';
  });
  h+='</div></div><div class="tag-filter-group"><div class="label">Outras especialidades (Informe qual)</div><div class="tags">';
  c.i.forEach(function(x){
    var t=x[0],n=x[1],a=sel.i.has(t)?'active':'';
    h+='<button class="tag-btn '+a+'" data-g="i" data-t="'+esc(t)+'">'+esc(t)+' <span class="count">('+n+')</span></button>';
  });
  h+='</div></div>';
  $('#filterArea').innerHTML=h;
  $$('#filterArea .tag-btn').forEach(function(b){
    b.addEventListener('click',function(){
      var m=b.dataset.g==='e'?sel.e:b.dataset.g==='d'?sel.d:sel.i;
      if(m.has(b.dataset.t)){m.delete(b.dataset.t);b.classList.remove('active')}
      else{m.add(b.dataset.t);b.classList.add('active')}
      render(1);
    });
  });
}

function filtrar(){
  var q=$('#filterSearch').value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  return DATA.filter(function(r){
    if(sel.e.size){var l=esp(r);if(!l.some(function(e){return sel.e.has(e)}))return false}
    if(sel.d.size){var l=des(r);if(!l.some(function(d){return sel.d.has(d)}))return false}
    if(sel.i.size){var l=inf(r);if(!l.some(function(i){return sel.i.has(i)}))return false}
    if(q){
      var h=((r['Nome Completo *']||'')+' '+(r['E-mail *']||'')+' '+(r['Estado *']||'')).toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
      if(!h.includes(q))return false}
    return true;
  });
}

function atualizarBtns(){
  $$('#filterArea .tag-btn').forEach(function(b){
    var m=b.dataset.g==='e'?sel.e:b.dataset.g==='d'?sel.d:sel.i;
    b.classList.toggle('active',m.has(b.dataset.t));
  });
}

function render(p){
  var f=filtrar(),tp=Math.ceil(f.length/N)||1;
  if(p<1)p=1;if(p>tp)p=tp;pg=p;
  $('#stats').textContent=f.length+' mentor(es) encontrados';
  var s=(p-1)*N, pd=f.slice(s,s+N), tb=$('#tbody');
  tb.innerHTML='';
  pd.forEach(function(r){
    var n=r['Nome Completo *']||'', e=r['E-mail *']||'', t=r['Telefone (WhatsApp) *']||'', est=r['Estado *']||'', el=esp(r), dl=des(r), il=inf(r);
    var nick=r['NICK DISCORD']||'', taDiscord=r['TA NO DISCORD?']||'';
    var tr=document.createElement('tr');
    var discIcon = (nick&&nick!='N\u00e3o Entrou') ? esc(nick) : '<span style="color:rgba(255,255,255,.3);font-size:.7rem">-</span>';
var discStatus = taDiscord=='Sim' ? '<span style="color:#81c784;font-size:.7rem">OK</span>' : (taDiscord ? '<span style="color:rgba(255,255,255,.35);font-size:.7rem">'+esc(taDiscord)+'</span>' : '<span style="color:rgba(255,255,255,.3);font-size:.7rem">-</span>');
tr.innerHTML='<td><strong>'+esc(n)+'</strong></td><td><a href="mailto:'+esc(e)+'"><span style="font-size:.75rem">'+esc(e)+'</span></a></td><td style="white-space:nowrap;font-size:.78rem">'+esc(t)+'</td><td style="white-space:nowrap;font-size:.75rem">'+discIcon+' '+discStatus+'</td><td style="white-space:nowrap;font-size:.78rem">'+esc(est)+'</td><td>'+el.map(function(x){return '<span class="tag" data-g="e" data-t="'+esc(x)+'">'+esc(x)+'</span>'}).join(' ')+'</td><td>'+il.map(function(x){return '<span class="tag tag-info" data-g="i" data-t="'+esc(x)+'">'+esc(x)+'</span>'}).join(' ')+'</td><td>'+dl.map(function(x){return '<span class="tag tag-desafio" data-g="d" data-t="'+esc(x)+'">'+esc(x)+'</span>'}).join(' ')+'</td><td><div style="display:flex;gap:4px;flex-wrap:wrap"><button class="copy-btn" data-c="'+esc(n+' - '+e+' - '+t)+'">Copiar</button></div></td>';
    tb.appendChild(tr);
  });
  $$('#tbody .tag').forEach(function(t){
    t.addEventListener('click',function(){
      var m=t.dataset.g==='e'?sel.e:sel.d;
      if(!m.has(t.dataset.t)){m.add(t.dataset.t);atualizarBtns();render(1)}
    });
  });
  $$('.copy-btn').forEach(function(b){
    b.addEventListener('click',function(){
      navigator.clipboard.writeText(b.dataset.c).then(function(){
        var o=b.textContent;b.textContent='Copiado!';b.style.background='#27ae60';
        setTimeout(function(){b.textContent=o;b.style.background=''},1500);
      });
    });
  });
  $('#pagination').innerHTML='<button onclick="go('+(p-1)+')"'+(p<=1?' disabled':'')+'>Anterior</button><span>Pagina '+p+' de '+tp+'</span><button onclick="go('+(p+1)+')"'+(p>=tp?' disabled':'')+'>Proxima</button>';
}

function go(p){render(p)}

function copiarTodosVisiveis(){
  var v=filtrar(), t=v.map(function(r){return (r['Nome Completo *']||'')+' - '+(r['E-mail *']||'')+' - '+(r['Telefone (WhatsApp) *']||'')}).join('\\n');
  navigator.clipboard.writeText(t).then(function(){alert(t.split('\\n').length+' contatos copiados!')});
}

function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}

$('#filterSearch').addEventListener('input',function(){render(1)});
montarFiltros();
render(1);
</script>
</body>
</html>'''

html = template.replace('__DATA__', minified)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('OK size:', os.path.getsize('index.html'))
print('Has data-g:', 'data-g' in html)
