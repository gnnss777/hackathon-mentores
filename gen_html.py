import json, os

with open('mentores_final.min.json', 'r', encoding='utf-8') as f:
    minified = f.read()

html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mentores haCARthon</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,sans-serif;background:#f5f7fa;color:#1a1a2e;padding:20px}}
.container{{max-width:1200px;margin:0 auto}}
h1{{font-size:1.5rem;margin-bottom:16px;color:#16213e}}
.tag-filter-area{{margin-bottom:20px}}
.tag-filter-group{{margin-bottom:12px}}
.tag-filter-group .label{{font-size:.8rem;font-weight:600;color:#555;margin-bottom:6px}}
.tag-filter-group .tags{{display:flex;flex-wrap:wrap;gap:6px}}
.tag-btn{{display:inline-flex;align-items:center;gap:4px;padding:5px 12px;border-radius:20px;border:1.5px solid #ccc;background:#fff;font-size:.8rem;cursor:pointer;user-select:none}}
.tag-btn:hover{{border-color:#999;background:#f0f0f0}}
.tag-btn.active{{background:#16213e;color:#fff;border-color:#16213e}}
.tag-btn.active:hover{{background:#1a2a5e}}
.tag-btn .count{{font-size:.7rem;opacity:.7}}
.search-area{{margin-bottom:16px}}
.search-area input{{padding:8px 14px;border:1.5px solid #ccc;border-radius:20px;font-size:.9rem;width:100%;max-width:400px;outline:none}}
.search-area input:focus{{border-color:#16213e}}
.stats{{font-size:.85rem;color:#666;margin-bottom:12px}}
.contato-rapido{{margin-bottom:16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
.contato-rapido button{{padding:6px 14px;border:1.5px solid #16213e;border-radius:20px;background:#fff;color:#16213e;font-size:.8rem;cursor:pointer}}
.contato-rapido button:hover{{background:#16213e;color:#fff}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
th{{background:#16213e;color:#fff;padding:10px 12px;text-align:left;font-size:.8rem;font-weight:600;white-space:nowrap}}
td{{padding:10px 12px;font-size:.85rem;border-bottom:1px solid #eee}}
tr:hover td{{background:#f0f4ff}}
.tag{{display:inline-block;background:#e8eaf6;color:#283593;padding:2px 8px;border-radius:10px;font-size:.7rem;margin:1px;cursor:pointer;transition:all .15s}}
.tag:hover{{background:#283593;color:#fff}}
.tag-desafio{{background:#fff3e0;color:#e65100}}
.tag-desafio:hover{{background:#e65100;color:#fff}}
.copy-btn{{background:#0f3460;color:#fff;border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:.75rem}}
.copy-btn:hover{{background:#1a5276}}
.pagination{{display:flex;justify-content:center;align-items:center;gap:8px;margin-top:16px}}
.pagination button{{padding:6px 14px;border:1px solid #ccc;border-radius:6px;background:#fff;cursor:pointer}}
.pagination button:disabled{{opacity:.4;cursor:default}}
.pagination span{{font-size:.85rem}}
</style>
</head>
<body>
<div class="container">
<h1>Mentores haCARthon</h1>
<div class="tag-filter-area" id="filterArea"></div>
<div class="search-area">
<input type="text" id="filterSearch" placeholder="Buscar nome, email, cidade...">
</div>
<div class="contato-rapido">
<button onclick="copiarTodosVisiveis()">Copiar contatos visiveis</button>
</div>
<div class="stats" id="stats"></div>
<div style="overflow-x:auto">
<table>
<thead><tr>
<th>Nome</th><th>Email</th><th>Telefone</th><th>Estado</th><th>Especialidades</th><th>Desafios</th><th>Acoes</th>
</tr></thead>
<tbody id="tbody"></tbody>
</table>
</div>
<div class="pagination" id="pagination"></div>
</div>
<script>
var DATA = {minified};

const N = 25;
var pg = 1;
var sel = {{e:new Set(), d:new Set()}};

function $(s){{return document.querySelector(s)}}
function $$(s){{return document.querySelectorAll(s)}}

function init(){{
  render();
}}

function esp(r){{
  return (r['Área de atuação/conhecimento/especialidade (escolha até 3 opções) *']||'').split(';').map(function(s){{return s.trim()}}).filter(Boolean);
}}

function des(r){{
  return (r['Qual dos desafios você acredita que pode colaborar com as equipes? Selecione em ordem de prioridade e fique à vontade para selecionar quantos desejar. *']||'').split(';').map(function(s){{return s.trim()}}).filter(Boolean);
}}

function contar(){{
  var ec={{}},dc={{}};
  DATA.forEach(function(r){{
    esp(r).forEach(function(e){{ec[e]=(ec[e]||0)+1}});
    des(r).forEach(function(d){{dc[d]=(dc[d]||0)+1}});
  }});
  return {{e:Object.entries(ec).sort(function(a,b){{return b[1]-a[1]}}), d:Object.entries(dc).sort(function(a,b){{return b[1]-a[1]}})}};
}}

function montarFiltros(){{
  var c=contar();
  var h='<div class="tag-filter-group"><div class="label">Especialidades</div><div class="tags">';
  c.e.forEach(function(x){{
    var t=x[0],n=x[1],a=sel.e.has(t)?'active':'';
    h+='<button class="tag-btn '+a+'" data-g="e" data-t="'+esc(t)+'">'+esc(t)+' <span class="count">('+n+')</span></button>';
  }});
  h+='</div></div><div class="tag-filter-group"><div class="label">Desafios</div><div class="tags">';
  c.d.forEach(function(x){{
    var t=x[0],n=x[1],a=sel.d.has(t)?'active':'';
    h+='<button class="tag-btn '+a+'" data-g="d" data-t="'+esc(t)+'">'+esc(t)+' <span class="count">('+n+')</span></button>';
  }});
  h+='</div></div>';
  $('#filterArea').innerHTML=h;
  $$('#filterArea .tag-btn').forEach(function(b){{
    b.addEventListener('click',function(){{
      var m=b.dataset.g==='e'?sel.e:sel.d;
      if(m.has(b.dataset.t)){{m.delete(b.dataset.t);b.classList.remove('active')}}
      else{{m.add(b.dataset.t);b.classList.add('active')}}
      render(1);
    }});
  }});
}}

function filtrar(){{
  var q=$('#filterSearch').value.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
  return DATA.filter(function(r){{
    if(sel.e.size){{var l=esp(r);if(!l.some(function(e){{return sel.e.has(e)}}))return false}}
    if(sel.d.size){{var l=des(r);if(!l.some(function(d){{return sel.d.has(d)}}))return false}}
    if(q){{
      var h=((r['Nome Completo *']||'')+' '+(r['E-mail *']||'')+' '+(r['Cidade *']||'')+' '+(r['Estado *']||'')).toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
      if(!h.includes(q))return false}}
    return true;
  }});
}}

function atualizarBtns(){{
  $$('#filterArea .tag-btn').forEach(function(b){{
    var m=b.dataset.g==='e'?sel.e:sel.d;
    b.classList.toggle('active',m.has(b.dataset.t));
  }});
}}

function render(p){{
  var f=filtrar(),tp=Math.ceil(f.length/N)||1;
  if(p<1)p=1;if(p>tp)p=tp;pg=p;
  $('#stats').textContent=f.length+' mentor(es) encontrados';
  var s=(p-1)*N, pd=f.slice(s,s+N), tb=$('#tbody');
  tb.innerHTML='';
  pd.forEach(function(r){{
    var n=r['Nome Completo *']||'', e=r['E-mail *']||'', t=r['Telefone (WhatsApp) *']||'', est=r['Estado *']||'', el=esp(r), dl=des(r);
    var tr=document.createElement('tr');
    tr.innerHTML='<td><strong>'+esc(n)+'</strong></td><td><a href="mailto:'+esc(e)+'">'+esc(e)+'</a></td><td>'+esc(t)+'</td><td>'+esc(est)+'</td><td>'+el.map(function(x){{return '<span class="tag" data-g="e" data-t="'+esc(x)+'">'+esc(x)+'</span>'}}).join(' ')+'</td><td>'+dl.map(function(x){{return '<span class="tag tag-desafio" data-g="d" data-t="'+esc(x)+'">'+esc(x)+'</span>'}}).join(' ')+'</td><td><div style="display:flex;gap:4px;flex-wrap:wrap"><button class="copy-btn" data-c="'+esc(n+' - '+e+' - '+t)+'">Copiar</button></div></td>';
    tb.appendChild(tr);
  }});
  $$('#tbody .tag').forEach(function(t){{
    t.addEventListener('click',function(){{
      var m=t.dataset.g==='e'?sel.e:sel.d;
      if(!m.has(t.dataset.t)){{m.add(t.dataset.t);atualizarBtns();render(1)}}
    }});
  }});
  $$('.copy-btn').forEach(function(b){{
    b.addEventListener('click',function(){{
      navigator.clipboard.writeText(b.dataset.c).then(function(){{
        var o=b.textContent;b.textContent='Copiado!';b.style.background='#27ae60';
        setTimeout(function(){{b.textContent=o;b.style.background=''}},1500);
      }});
    }});
  }});
  $('#pagination').innerHTML='<button onclick="go('+(p-1)+')"'+(p<=1?' disabled':'')+'>Anterior</button><span>Pagina '+p+' de '+tp+'</span><button onclick="go('+(p+1)+')"'+(p>=tp?' disabled':'')+'>Proxima</button>';
}}

function go(p){{render(p)}}

function copiarTodosVisiveis(){{
  var v=filtrar(), t=v.map(function(r){{return (r['Nome Completo *']||'')+' - '+(r['E-mail *']||'')+' - '+(r['Telefone (WhatsApp) *']||'')}}).join('\\n');
  navigator.clipboard.writeText(t).then(function(){{alert(t.split('\\n').length+' contatos copiados!')}});
}}

function esc(s){{var d=document.createElement('div');d.textContent=s;return d.innerHTML;}}

$('#filterSearch').addEventListener('input',function(){{render(1)}});
montarFiltros();
render(1);
</script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('OK size:', os.path.getsize('index.html'))
