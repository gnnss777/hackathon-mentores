import json, os

with open('mentores_final.min.json', 'r', encoding='utf-8') as f:
    minified = f.read()

template = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mentores haCARthon</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700;6..12,800;6..12,900&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Nunito Sans',system-ui,-apple-system,sans-serif;background:#0D0D0D;color:#e0e0f0;min-height:100vh;padding:20px}
.container{max-width:1320px;margin:0 auto}

/* HEADER */
.header{display:flex;align-items:center;gap:20px;margin-bottom:24px;padding:16px 24px;border-radius:12px;background:linear-gradient(135deg,#4A1FA8 0%,#EC008C 100%);position:relative;overflow:hidden}
.header::before{content:'';position:absolute;top:-50%;right:-20%;width:300px;height:300px;background:rgba(0,191,255,.08);border-radius:50%;pointer-events:none}
.header::after{content:'';position:absolute;bottom:-40%;left:10%;width:200px;height:200px;background:rgba(255,255,255,.04);border-radius:50%;pointer-events:none}
.header .logo{height:38px;width:auto;position:relative;z-index:1}
.header-titles{display:flex;align-items:center;gap:14px;position:relative;z-index:1}
.header-hack{font-size:1.3rem;font-weight:900;color:#fff;letter-spacing:-.5px;text-transform:uppercase}
.header .badge{background:rgba(255,255,255,.15);color:#fff;font-size:.85rem;font-weight:900;padding:5px 16px;border-radius:10px;text-transform:uppercase;letter-spacing:1.5px;backdrop-filter:blur(4px);border:1px solid rgba(255,255,255,.15)}
.header .sub{color:rgba(255,255,255,.5);font-size:.75rem;margin-left:auto;font-weight:600;position:relative;z-index:1}

/* LAYOUT SIDEBAR + CONTEUDO */
.layout{display:flex;gap:24px;align-items:flex-start}
.sidebar{width:260px;flex-shrink:0;position:sticky;top:20px}
.main{flex:1;min-width:0}

/* FILTROS SIDEBAR */
.tag-filter-area{background:#1A1A2E;border-radius:12px;padding:18px;border:1px solid rgba(255,255,255,.06)}
.tag-filter-group{margin-bottom:12px}
.tag-filter-group:last-child{margin-bottom:0}
.tag-filter-group .label{font-size:.65rem;font-weight:800;color:#EC008C;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;padding-left:2px}
.tag-filter-group .tags{display:flex;flex-wrap:wrap;gap:5px}
.tag-btn{display:inline-flex;align-items:center;gap:4px;padding:5px 14px;border-radius:8px;border:1px solid rgba(255,255,255,.06);background:rgba(255,255,255,.03);color:rgba(255,255,255,.55);font-size:.75rem;cursor:pointer;user-select:none;font-family:'Nunito Sans',sans-serif;font-weight:600;transition:all .2s;text-transform:uppercase;letter-spacing:.3px}
.tag-btn:hover{border-color:rgba(0,191,255,.2);background:rgba(0,191,255,.05);color:#00BFFF}
.tag-btn.active{background:#EC008C;color:#fff;border-color:#EC008C;box-shadow:0 2px 12px rgba(236,0,140,.3)}
.tag-btn.active:hover{box-shadow:0 2px 16px rgba(236,0,140,.45)}
.tag-btn .count{font-size:.6rem;opacity:.5}

/* BUSCA */
.search-area{margin-bottom:16px;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.search-area input{flex:1;min-width:200px;max-width:400px;padding:10px 16px;border:1px solid rgba(255,255,255,.06);border-radius:8px;font-size:.82rem;outline:none;background:rgba(255,255,255,.04);color:#fff;font-family:'Nunito Sans',sans-serif;transition:all .2s;font-weight:600}
.search-area input::placeholder{color:rgba(255,255,255,.15);font-weight:400}
.search-area input:focus{border-color:#00BFFF;background:rgba(0,191,255,.04);box-shadow:0 0 0 3px rgba(0,191,255,.08)}

/* STATS */
.stats{font-size:.8rem;color:rgba(255,255,255,.3);margin-bottom:16px;font-weight:700;letter-spacing:.5px;text-transform:uppercase}

/* GRID CARDS */
.grid-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(480px,1fr));gap:16px}
.card{background:#1A1A2E;border:1px solid rgba(255,255,255,.05);border-radius:12px;padding:18px 20px;transition:all .2s}
.card:hover{border-color:rgba(236,0,140,.15);transform:translateY(-2px);box-shadow:0 8px 32px rgba(236,0,140,.08)}
.card-row{display:flex;align-items:center;gap:14px}
.card-row-top{margin-bottom:10px}
.card-avatar{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#EC008C,#00BFFF);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:.85rem;color:#fff;flex-shrink:0;box-shadow:0 2px 8px rgba(236,0,140,.2)}
.card-info{flex:1;min-width:0}
.card-nome{font-size:.95rem;font-weight:800;color:#fff;display:flex;align-items:center;gap:8px;letter-spacing:-.3px}
.card-estado{font-size:.65rem;color:rgba(255,255,255,.3);font-weight:400;text-transform:uppercase;letter-spacing:.5px}
.card-discord{display:flex;align-items:center;gap:10px;font-size:.82rem;color:rgba(255,255,255,.5)}
.card-discord svg{width:20px;height:20px}
.card-discord .nick{color:#00BFFF;font-weight:700;cursor:pointer;padding:3px 12px;border-radius:6px;background:rgba(0,191,255,.06);border:1px solid rgba(0,191,255,.1);transition:all .15s;font-size:.8rem}
.card-discord .nick:hover{background:rgba(0,191,255,.12);color:#33D4FF;border-color:rgba(0,191,255,.2)}
.card-discord .status-dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.card-discord .status-dot.on{background:#43b581;box-shadow:0 0 6px rgba(67,181,129,.4)}
.card-discord .status-dot.off{background:rgba(255,255,255,.1)}
.copy-btn{padding:10px 22px;border:none;border-radius:8px;background:#EC008C;color:#fff;font-size:.82rem;cursor:pointer;font-weight:800;font-family:'Nunito Sans',sans-serif;transition:all .2s;text-transform:uppercase;letter-spacing:.5px}
.copy-btn:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(236,0,140,.35)}
.card-linha-contato{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:4px}
.card-wpp{display:inline-flex;align-items:center;gap:6px;font-size:.82rem;color:rgba(255,255,255,.75);cursor:pointer;padding:4px 12px;border-radius:6px;background:rgba(37,211,102,.06);border:1px solid rgba(37,211,102,.08);transition:all .15s;font-weight:600}
.card-wpp:hover{background:rgba(37,211,102,.1);color:#25D366;border-color:rgba(37,211,102,.15)}
.card-wpp.copied{background:rgba(37,211,102,.15);color:#25D366;border-color:rgba(37,211,102,.2)}
.card-email{font-size:.65rem;color:rgba(255,255,255,.2);cursor:pointer;font-weight:400;transition:all .1s;margin-top:1px;letter-spacing:.2px}
.card-email:hover{color:rgba(255,255,255,.4)}
.card-email.copied{color:#00BFFF}
.bio-btn{font-size:.7rem;font-weight:800;color:#EC008C;cursor:pointer;background:rgba(236,0,140,.1);border:1px solid rgba(236,0,140,.2);border-radius:6px;padding:3px 12px;margin-left:8px;transition:all .15s;text-transform:uppercase;letter-spacing:.8px;font-family:'Nunito Sans',sans-serif}
.bio-btn:hover{background:#EC008C;color:#fff;border-color:#EC008C;box-shadow:0 2px 8px rgba(236,0,140,.3)}
.card-tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,.06)}
.tag{display:inline-block;background:rgba(236,0,140,.1);color:#ff5aa0;padding:4px 12px;border-radius:6px;font-size:.65rem;cursor:pointer;transition:all .15s;font-weight:700;text-transform:uppercase;letter-spacing:.5px;border:1px solid rgba(236,0,140,.08)}
.tag:hover{background:#EC008C;color:#fff;border-color:#EC008C;box-shadow:0 2px 8px rgba(236,0,140,.2)}
.tag-desafio{background:rgba(0,191,255,.1);color:#5dcdff;border-color:rgba(0,191,255,.08)}
.tag-desafio:hover{background:#00BFFF;color:#fff;border-color:#00BFFF;box-shadow:0 2px 8px rgba(0,191,255,.2)}

/* PAGINACAO */
.pagination{display:flex;justify-content:center;align-items:center;gap:10px;margin-top:24px;padding-top:20px;border-top:1px solid rgba(255,255,255,.04)}
.pagination button{padding:8px 18px;border:1px solid rgba(255,255,255,.06);border-radius:8px;background:rgba(255,255,255,.03);color:rgba(255,255,255,.5);cursor:pointer;font-family:'Nunito Sans',sans-serif;font-size:.8rem;font-weight:700;transition:all .2s;text-transform:uppercase;letter-spacing:.5px}
.pagination button:hover:not(:disabled){background:rgba(236,0,140,.08);color:#EC008C;border-color:rgba(236,0,140,.15)}
.pagination button:disabled{opacity:.2;cursor:default}
.pagination span{font-size:.8rem;color:rgba(255,255,255,.25);font-weight:600;letter-spacing:.5px}

/* OVERLAY BIO */
.overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);backdrop-filter:blur(6px);z-index:100;align-items:center;justify-content:center;padding:20px}
.overlay.show{display:flex}
.overlay-card{background:#1A1A2E;border:1px solid rgba(255,255,255,.08);border-radius:16px;max-width:560px;width:100%;max-height:80vh;overflow-y:auto;padding:28px;position:relative;animation:fadeIn .2s}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.overlay-close{position:absolute;top:14px;right:16px;background:none;border:none;color:rgba(255,255,255,.3);font-size:1.4rem;cursor:pointer;font-family:'Nunito Sans',sans-serif;transition:all .15s;line-height:1}
.overlay-close:hover{color:#EC008C}
.overlay-card h2{font-size:1.2rem;font-weight:900;color:#fff;margin-bottom:4px}
.overlay-card .subtitle{font-size:.75rem;color:rgba(255,255,255,.3);margin-bottom:16px}
.overlay-card .bio-text{font-size:.85rem;color:rgba(255,255,255,.7);line-height:1.6;white-space:pre-wrap}
.overlay-card .bio-linkedin{display:inline-block;margin-top:14px;color:#00BFFF;font-weight:700;font-size:.8rem;text-decoration:none}
.overlay-card .bio-linkedin:hover{text-decoration:underline}

@media(max-width:768px){
  .layout{flex-direction:column}
  .sidebar{width:100%;position:static}
  .grid-cards{grid-template-columns:1fr}
  .header .sub{display:none}
}
</style>
</head>
<body>
<div class="container">
<div class="header">
<img src="logo_white-de8638da8e90456792c38c13ccc01d73.svg" alt="Panic Lobster" class="logo">
<div class="header-titles">
<span class="header-hack">haCARthon</span>
<span class="badge">MENTORES</span>
</div>
<span class="sub">88 mentores cadastrados</span>
</div>
<div class="layout">
<div class="sidebar">
<div class="tag-filter-area" id="filterArea"></div>
</div>
<div class="main">
<div class="search-area">
<input type="text" id="filterSearch" placeholder="Buscar por nome, email, estado...">
<button class="copy-btn" onclick="copiarTodosVisiveis()">Copiar contatos</button>
</div>
<div class="stats" id="stats"></div>
<div class="grid-cards" id="cardsContainer"></div>
<div class="pagination" id="pagination"></div>
</div>
</div>
</div>
<div class="overlay" id="bioOverlay">
<div class="overlay-card">
<button class="overlay-close" onclick="fecharBio()">&times;</button>
<div id="bioContent"></div>
</div>
</div>
<script>
var DATA = __DATA__;
var N = 20, pg = 1;
var sel = {e:new Set(), d:new Set(), disc:new Set()};
var BIOS = {
  "Rafaella Rodrigues manfrenatti": "Olá, sou Rafaella, mestre em Educação Profissional em Saúde pela Fiocruz e desenvolvedora web. Tenho experiência nas áreas de educação, saúde, tecnologias digitais, desenvolvimento de sistemas e pesquisa científica. Posso contribuir com temas relacionados à transformação digital, desenvolvimento web, inteligência artificial, educação em saúde, metodologias de pesquisa, análise de dados e construção de projetos e apresentações (pitch).",
  "MARCUS DAMIÃO DE LACERDA": "Olá, sou Marcus Damião de Lacerda, Engenheiro Agrônomo, M.Sc. e D.Sc. em Enga. Agrícola (Irrigação e Drenagem), Servidor Público Federal, Chefe do Setor de Operações Agrícolas (SOA) do DNOCS-CEST-PB, professor do IFSERTÃOPB (Campus Sousa). Trabalhei e fiz vários CAR na EMATER-PARÁ, atuo na área de Recursos Hídricos, fiscalização e monitoramento de Reservatórios (Barragens e/ou Açudes) no Estado da Paraíba. Posso ajudar na área de Ciências Agrárias.",
  "Geysa Karla Alves Galvão": "Olá, pessoal! É um prazer estar aqui para compartilhar e aprender.\nSou especialista em Gestão da Qualidade em TIC e mestranda em Gestão do Desenvolvimento Local Sustentável. Meu foco principal é a mentoria nas áreas de Inovação, Acessibilidade e Sustentabilidade.\nSou Mentora certificada pela ABMEN e participo ativamente do ecossistema de inovação, sendo mentora no Porto Social, Armazém da Criatividade e Conecta Startup Brasil – SOFTEX. Minha experiência inclui mentoria e avaliação em eventos como Mega Hack Women, CNJ Inova, Semana SENAI de Inovação, Hackathon Impulso Regional, do Inova Norte e da OCINA.\nAtualmente, trabalho com Recursos Humanos (RH), T&D e Tech Recruiting, complementando minha experiência em docência e pesquisa focada em Inclusão e Acessibilidade.\nEstou à disposição para a troca! Sejam muito bem-vindos! 🙂",
  "José Eduardo de Paula Galdiano": "Olá, pessoal! Tudo bem? Agradeço a oportunidade para aprender e contribuir.\nSou Head de Projetos e Inovação na Value Weavers, Gerente de Relacionamento e Projetos na Great Thinkers, Co-founder do I2H - Instituto para Inovação em Saúde, Avaliador de Projetos nos programas Inovativa, Arena Celta, Sinapse Bioeconomia da Amazônia, Centelha e Parque Tecnológico de Maricá e Mentor nos programas Inovativa, Acelera SP, Startup Day, Inovenow, Feira do Empreendedor Sebrae, IBM, Menos30Fest, Tempu, Canathon, InovaHC, Inova Norte, Poli Ventures MICBR2023 e Campo Tech 2023. Engenheiro Mecânico pela UNESP, MBAs em Gestão Empresarial e Negócios Internacionais pela FGV com experiências diversas em engenharia, vendas, supply chain, M&A, e consultoria nos setores automotivo, máquinas e equipamentos, açúcar e álcool, siderurgia, cimentos, ferrovia, saúde, biotecnologia, agro, meio ambiente, energia, entre outros.\nDesejo sucesso em todos os desafios e vamos fazer desta uma grande oportunidade! 🏆",
  "Emerson Barragán": "Fala, pessoal! Bom estar aqui com vcs.\nSou especialista em Engenharia de Confiabilidade (SRE), Plataforma e Arquitetura de Sistemas. Minha atuação é conectar estratégia, tecnologia e times, ajudando equipes a transformar ideias em soluções robustas, sem perder agilidade.\nAtualmente, estou como Tech Manager com foco em SRE e plataforma, além de atuar como mentor voluntário em comunidades como SouJunior e Agilidade Preta, contribuindo para a formação de novos talentos na tecnologia.\nSe quiser conversar sobre arquitetura, automação ou métricas, tamo aí!",
  "Lorrana Oliveira Nunes": "Olá! Sou Lorrana, doutoranda em Educação, pesquisadora com experiência em inovação, inclusão e impacto social. Atuo apoiando equipes na criação de soluções criativas e colaborativas em hackathons como mentora, madrinha e/ou jurada.\n\nMinha trajetória valoriza diversidade, neurodivergência e pensamento crítico, fortalecendo projetos que unem tecnologia, educação e transformação social.\n\nSerá um prazer compartilhar essa jornada com vocês. 🤓🌱💪💖",
  "Josie Michelle Soares": "Olá, sou Josie Soares, licenciada e técnica em Química, especialista em Processos Industriais e pós-graduanda em Petróleo e Gás. Tenho experiência nas áreas de educação, sustentabilidade, energias renováveis, biocombustíveis e pesquisa científica, com projetos premiados em feiras de ciências. Posso contribuir com temas relacionados à gestão ambiental, economia circular, bioenergia, aproveitamento de resíduos agropecuários, práticas sustentáveis, elaboração de projetos e pesquisa científica.",
  "Louise Fhaedra da Silva Pereira": "Oi. Me chamo Louise Fhaedra, sou Advogada, Analista de Inovação na área do Direito no CDT/UnB, Licenciada e Pós graduada em Dança pelo Instituto Federal de Brasília, Especializada em Neurociência na educação e HIWS na Hanyang University em SEOUL, South Korea. Tenho uma Startup na área da educação inclusiva e será um prazer compartilhar minhas vivências com todos.",
  "Maria Efigênia Farias": "Olá, sou Maria Efigênia Farias. Sou Engenheira de Pesca, com mestrado em Recursos Pesqueiros. Atualmente estou como presidente da Associação dos Engenheiros de Pesca de Pernambuco e professora aposentada do IFPE. Atuo nas áreas de: Aquicultura, Pesca, Meio Ambiente, Qualidade da Água, Ecoturismo e Empreendedorismo. Posso ajudá-los no processo de ideação e no pitch. Participo de Hackathon e Startup Way desde 2019 como mentora.",
  "Humberto Lucas Santos de Sant' Anna": "Olá, sou o Humberto Sant' Anna...\nSou Engenheiro Agrônomo pela Universidade Federal de Alagoas (UFAL), Mestre em Agronomia pela Universidade Federal do Recôncavo da Bahia (UFRB), especialista em Acessibilidade, Inclusão e Direitos Humanos pela Fiocruz e MBA em Gestão de Negócios pela faculdade Sebrae.\nAtualmente sou Analista Técnico do Sebrae Alagoas, atuando nas áreas de agronegócios, agricultura familiar, inovação, startups e gestão de projetos. Possui experiência no desenvolvimento de cadeias produtivas, empreendedorismo rural, articulação institucional e promoção da acessibilidade, inclusão e equidade em ambientes organizacionais.\nAtuo também como mentor e avaliador de startups, contribuindo para o fortalecimento do empreendedorismo, da inovação e do desenvolvimento de micro e pequenas empresas no âmbito do Sistema Sebrae.",
  "Juan Pablo Muniz Pinheiro": "Olá, sou Juan Pablo Pinheiro.\nAtuo nas áreas de tecnologia, inovação, gestão de projetos, segurança da informação, dados, GovTech, economia criativa e impacto socioambiental.\nSou mestrando em Administração na Ibmec, desenvolvedor, Scrum Master, graduado em Ciência da Computação e Matemática.\nMinha trajetória conecta tecnologia, gestão, inovação e impacto público, com experiência em transformação digital, desenvolvimento de soluções, segurança da informação, dados, Terceiro Setor e iniciativas globais de inovação.\nPosso contribuir com as equipes no processo de ideação, modelagem da solução, estruturação do pitch, visão estratégica, uso de dados, tecnologia, sustentabilidade, gestão de projetos e impacto socioambiental.",
  "Carlos Henrique Rodrigues Pereira": "👋 Quem sou eu\nCarlos Henrique Rodrigues Pereira\nTechnical Product Manager e Fullstack Developer\nExperiência em produto, tecnologia, GTM, marketing e negócios\n\n🔥 Por que eu sou um ótimo Mentor\nTransito bem entre estratégia e execução\nEntendo produto, código, usuário e mercado\nJá atuei com produtos financeiros, plataformas digitais e lançamentos internacionais\n\n🛠️ Como posso te ajudar\nOrganizar ideias e problemas\nPensar em MVPs viáveis\nMelhorar UX e fluxos\nIdentificar riscos técnicos\nValidar propostas comerciais\nRefinar pitch e apresentação",
  "Paulo Vítor Guedes de Souza": "Olá Pessoal, Excelente dia! Espero que estejam bem.\nSou Licenciado em Pedagogia pela UENF, possuo formações Técnicas nas áreas de Sistemas de Telecomunicações e Automação Industrial pelo IFF Campos- Centro.\nJá participei de outros Hackathons e espero poder contribuir positivamente no processo inclusivo e equitativo em ambientes empresariais, turismo rural, empreendedorismo contemporâneo, além da elaboração da ideação e construção do pitch.\nMuito boa sorte para todos! 🚀 ✅ 🏆",
  "Jéssica Cunha Nogueira": "Olá, equipes! Sou advogada, internacionalista, empresária no agronegócio e mestra em Agronegócio pela FGV, com formações internacionais na Sorbonne/Paris, Salamanca/Espanha e Roma Tre/Itália, todas com enfoque ambiental. Já participei de hackathons e ganhei subvenções. Posso contribuir estrategicamente em CAR, regularidade ambiental rural, segurança jurídica, dores reais do produtor, modelagem de soluções, viabilidade de negócio, impacto e pitch. Boa sorte a todos! 🌱",
  "LILLIAN MARIA DE MESQUITA ALEXANDRE": "Saudações Juninas! Boa tarde pessoal, aqui é a Lillian Mesquita, diretamente de Aracaju/Sergipe (Capital do Forró), sou turismóloga de formação, mestre em desenvolvimento e meio ambiente, doutora em geografia e professora aposentada da Universidade Federal do Delta do Parnaíba/PI. Atua no seguimento de educação há mais de 20 anos, correlacionados ao turismo, meio ambiente e sustentabilidade. Sou consultora e co-fundadora da Rede Internacional Colaborativa Território Vibrante, que atua no seguimento do Turismo Regenerativo, Territórios e Meio Ambiente e estou mentorando desde 2023, o que vem sendo um desafio gratificante. Tenho um olhar multidisciplinar e inter, onde, neste caso em particular, o Turismo e seus seguimentos: Rural, Pedagógico, Ecológico, de Base Comunitária e Criativo, podem auxiliar nos desafios. Além disso, a Economia Circular, Mudanças Climáticas e demais temas correlacionados, como a Educação Ambiental e ESG, fazem parte da minha formação e gestão. Estou para auxiliar, ajudar e aprender com todos vcs.",
  "José Nivaldo da Silva Júnior": "Olá! sou Nivaldo Jr, Bacharel em Administração, pós-graduado em Gestão de Pessoas, Gestão de Marketing Digital Estratégico e Pós-graduado em Operações do Mercado Financeiro pela FIA/USP. Também sou Consultor Empresarial Estratégico, fui mentor de startups no período em que fui docente pela UFPE. Além de Consultor, também leciono em Faculdades e no Ensino Médio Técnico profissional as disciplinas de Empreendedorismo, Logística e Atualidades em Gestão. Espero ajudar e contribuir na consolidação dos projetos. Durante as mentorias, fui mentor na área de plano de negócios, Estratégia de segmento de mercado e Liderança.",
  "LEANDRO MONTEIRO DOS SANTOS": "Leandro Monteiro é cofundador do Impact Hub Goiânia e líder da Valorize Rural, atuando na estruturação de soluções de regularização ambiental para o agronegócio e na coordenação da Caravana Valorize Rural, que leva orientação técnica e acesso a soluções de sustentabilidade, crédito e adequação ambiental diretamente ao produtor rural. Atua na interface entre desenvolvimento territorial, segurança jurídica e competitividade do campo. Foi consultor da Falconi, com atuação em projetos de gestão e eficiência no setor público e privado. No setor público, exerceu funções de Chefe de Gabinete e Superintendente no Governo de Goiás, além de experiências em estruturas de gestão pública no estado da Paraíba, com foco em governança, planejamento e políticas públicas.\nÉ formado em Economia pela UFG, pós-graduação em Liderança e Gestão Pública pelo CLP, formação executiva pela Harvard Kennedy School e é mestre em Cidades pela London School of Economics (LSE).",
  "Eloi Chad": "Filósofo, Advogado, Jornalista, Consultor e pesquisador de Inteligência Artificial e computação quântica. Coautor de livros sobre IA e filosofia da tecnologia, atua como mentor para hackathons, startups e com experiência em desenvolvimento full stack, inovação e resolução de problemas críticos e estratégicos.",
  "Alexandra Gonçalves Alcantara": "Olá, pessoal! Sou Alexandra, formada em Gestão Ambiental e Análise e Desenvolvimento de Sistemas. Sou desenvolvedora de software no Grupo Boticário e também possuo experiência no desenvolvimento de protótipos no Figma. Já atuei como mentora no Programa Desenvolve do Grupo Boticário e no Hackathon Janelas para o Amanhã. Posso ajudar com os seguintes temas: Tech, Ideação, Design, Protótipo e posso ajudar na construção do pitch também.\nDesejo sucesso a todos! 🚀",
  "Andressa Proença Aldrighi": "Bom dia pessoal, sou a Andressa Aldrighi, empreendedora e fundadora da startup FreelaFy, criada para conectar oportunidades e pessoas por meio da tecnologia e da inovação. Acredito no poder das conexões, da colaboração e do empreendedorismo como ferramentas de transformação social e econômica. Minha trajetória passa pela construção de comunidades, eventos e iniciativas voltadas ao desenvolvimento de negócios e talentos. Como mentora, gosto de compartilhar experiências reais, aprendizados e desafios de quem empreende todos os dias, sempre com foco em gerar impacto e abrir caminhos para outras pessoas.",
  "Isabel Tavares Galindo Nepomuceno": "Sou Isabel Nepomuceno, Engenheira Florestal formada pela Universidade Federal de Alagoas (UFAL), com experiência em regularização ambiental de imóveis rurais. Atuo com o Sistema do Cadastro Ambiental Rural (SICAR), elaboração, retificação e análise do Cadastro Ambiental Rural (CAR) e do Programa de Regularização Ambiental (PRA). No Instituto do Meio Ambiente de Alagoas (IMA/AL), exerci a função de Coordenadora do Cadastro Ambiental Rural, sendo responsável pela gestão e análise de CARs e pelo apoio à implementação da agenda de regularização ambiental no estado.\nAtualmente, sou fundadora da Florestar Consultoria Ambiental, auxiliando produtores rurais, empresas e consultores na regularização ambiental e na adequação ao Código Florestal.",
  "Alexandre de Cássio Rodrigues": "Olá! Sou Alexandre Rodrigues. Há 20 anos atuo como Especialista em Tecnologia da Informação na Agência Nacional de Mineração. Atualmente, sou Superintendente de Arrecadação e Fiscalização de Receitas. Tenho doutorado em Administração, mestrados em Administração e Engenharia de Produção e graduações em Administração, Engenharia de Produção e Computação. Consigo contribuir nas etapas de ideação, protótipo e produção do pitch.",
  "Eduardo POZITIVO": "Eduardo POZITIVO, administrador de empresas com especialização em informática, rh e marketing, atuando como Gestor de Empresas, com larga experiencia em empresas e projetos de diversos segmentos. Habilidade em reestruturar empresas, assessoria estratégica, transformando resultados negativos em POZITIVOS. 🤟 💥 🇧🇷",
  "Ebert Ryan Silva Santos": "Olá, pessoal! Sou Ebert Ryan, empreendedor, CEO da Codepacce, soft house e venture builder focada em transformar ideias em produtos digitais reais. Sou bacharel em Ciência da Computação e tenho MBA em Inteligência Artificial e Big Data, atuando com tecnologia, desenvolvimento de plataformas, automações, IA, produtos SaaS, validação de negócios e estruturação de MVPs.\nComo mentor, posso contribuir ajudando equipes a tirar ideias do papel, organizar melhor a proposta de valor, pensar em soluções tecnológicas viáveis, estruturar MVPs, melhorar a modelagem do negócio, definir caminhos de monetização e entender como usar tecnologia, IA e automação de forma estratégica para gerar impacto e escala.\nTambém posso apoiar em temas como arquitetura de sistemas, desenvolvimento de plataformas digitais, pitch, validação com mercado, jornada do usuário, posicionamento do produto e construção de soluções mais simples, funcionais e escaláveis.",
  "MAYRA AIRES DE CASTRO COSTA": "Meu nome é Mayra. Tenho experiência em análise do Cadastro Ambiental Rural (CAR), incluindo análise técnica, validação e regularização ambiental de imóveis rurais.",
  "Davidson de Oliveira Lima": "Boa tarde a todos! Me chamo Davidson, sou técnico em química e engenheiro químico, pós-graduado em inteligência artificial. Sou líder técnico e trabalho com projetos de engenharia e software para a indústria, envolvendo vários segmentos como óleo e gás, setor elétrico, manufatura e papel e celulose.\nTenho experiência em desenvolvimento de software (frontend, backend e banco), possuo conhecimentos em Python, web design (HTML, CSS, JavaScript), criação de telas e softwares específicos de dados, descoberta do conhecimento, BI, e outros. Também gosto de experiência do usuário e otimização de sistemas!\nCuriosidade: meu time foi ganhador do Desafio #2 do Hackathon Radix 2022, no Rio de Janeiro.\nSucesso a todos e que comecem os jogos! 🎉🎉",
  "Sarah Fernandes da Silva Nascimento": "Sarah F. Fernn\nFoco em: Diversidade Cognitiva, Astropolítica e Tecnologia de Fronteira\nÁreas de Formação: Eng. Elétrica e de Computação; RI; Adm. Pública\n\nEmpreendedora social autista e TDAH, fundadora na Stardust Zone (Social Deeptech em Diversidade Cognitiva e Inclusão Produtiva para Adultos Neurodivergentes em STEAM, trabalhando junto com empresas privadas e governos para aumentar a empregabilidade e permanência neurodivergente no mercado de trabalho). Além disso, sou co-fundadora do Zenith Space (1º think tank brasileiro em astropolítica, new space e spacetech).\n\nEmpreendo há ~11 anos, na área tech, de diplomacia, governo digital e de impacto social já tive o prazer de mentorar em outras competições diversas e estou muito feliz de poder contribuir nesse evento.\n\nEm que posso ajudar (essencialmente): UX/Design/Pesquisa com Usuários; Estratégia e Plano de Negócios; Arquitetura de Sistemas; Planejamento de Pitch",
  "LUIZ CLAUDIO OLIVEIRA DE ALMEIDA": "Olá! Sou Luiz Almeida Administrador e Analista de Dados na esfera pública, graduado em Análise de Sistemas e especialista em Gestão de Informática em Saúde. Tenho experiência prática na gestão e automação de grandes bases de dados governamentais. Posso ajudar vocês em: Estruturação e Tratamento de Dados, Soluções de Automação, Engenharia de Software e na viabilidade técnica do projeto frente às demandas do setor público. Boa maratona!👊",
  "Claude Adélia Moema Jeanne Cohen": "Boa tarde pessoal! Sou professora de Microeconomia, Empreendedorismo Sustentável e Economia do Meio Ambiente na graduação e no Programa de Pós Graduação em Economia - PPGE da UFF, coordeno o NIMAS/UFF - Núcleo de Inovação Meio Ambiente e Sustentabilidade da UFF (laboratório multidisciplinar e interprofissional de des. tecnológico e extensão que presta assessoria a empresas públicas e privadas; identifica oportunidades de novos produtos e serviços no mercado, projetos de iniciação científica e tecnológica nas áreas de empreendedorismo, meio ambiente e energia) desde 2009, sou mentora do NEXUS Hub de Inovação do Parque de Inovação Tecnológica de São José dos Campos - PIT desde 2024 e Líder de Inovação do Nosso Estado - LINE pela FAPERJ. Já orientei uma série de TCCs, dissertações e teses sobre desmatamento e uso do solo, abordando o tema central desse Hackathon.",
  "Andreia souza Santana da Silva": "Olá, me chamo Andreia (mas fique à vontade para me chamar de Deia!). Sou formada em Sistemas de Informação, especialista em Big Data e apaixonada pela área técnica. Minha trajetória é marcada pela atuação em projetos de engenharia de alta complexidade, incluindo operações estratégicas para a Petrobras, e atualmente trabalho com desenvolvimento de software na Alemanha.\nSempre em busca de inovação, sou Master em Arquitetura de Software Distribuído (PUC Minas) e possuo pós-graduações em Inteligência Artificial e Gestão do Agronegócio (IFMT). Além da atuação corporativa internacional, dedico minha energia ao desenvolvimento de pessoas e à inclusão na tecnologia: sou membro do conselho do Women Techmakers na América Latina e já realizei mentorias com o Google, Microsoft e Amazon, focadas em diversidade e desenvolvimento de apps e software.\nEstou sempre de portas abertas para orientar alunos e ajudar novos talentos a decolarem na área. Precisa de Ajuda no seu projeto, Me chame, conte comigo!",
  "Gabriel Vargas Zanatta": "Boa tarde! Sou Gabriel Zanatta, Professor de Política e Legislação Florestal do curso de Eng. Florestal da Universidade Federal do Tocantins. Estou em exercício no Ministério dos Povos Indígenas onde, entre outras funções, coordenei a Implementação e o Monitoramento da Política Nacional de Gestão Ambiental e Territorial Indígena. Sou doutorando em Ecologia Tropical na Universidad Veracruzana (México) e tenho Mestrado em Ciências de Florestas Tropicais (INPA) e sou Eng. Florestal (UnB). Tenho experiência de 15 anos de docência, pesquisa e extensão e faço parte do Fórum de Professoras e Professores de Extensão Rural.",
  "emerson rocha": "Boa tarde a todos, me chamo Emerson, tenho formação em engenharia mecânica, pós em gerenciamento de projetos, com MBA em gestão de qualidade e AI para negócios. Passei por mais de 36 anos de experiência em manufatura, dos quais 20 anos foram em gestão, a partir de então, empreendi no ramo de serviços ligados a soluções de engenharia e qualidade, dirigi laboratório de análises ambientais e mais recentemente lecionando tecnicamente. Primeiramente cursos de engenharia para técnicos da ETE Júlio de Mesquita e ultimamente para o Senai SP. Dentro de minha experiência, estou a disposição para agregar valor às equipes.",
  "Wagner de Oliveira Pequeno": "Boa noite, meu nome é Wagner, sou professor universitário e cientista de dados. Sou graduado em Matemática, pós graduado em computação e educação, Mestrado em Ciência de Materiais. Na minha trajetória profissional de mais de 30 anos, trabalhei em empresas como Banco Central do Brasil, Banco do Brasil, Ministério da Educação, TAM Linhas Aéreas, VisaVale, UnB, Tribunal de Contas do Distrito Federal e na SEEDF nas áreas de análise, desenvolvimento, arquitetura e gestão de equipes de tecnologia, bem como no Planejamento estratégico e construção de painéis de acompanhamento e gestão da informação e modelagem de indicadores.\nEstou a disposição para ajudar a acelerar as ideias para um projeto de excelência.",
  "Paul Pessoa": "Fala, galera! Me chamo Paul.\nSou desenvolvedor de software com experiência internacional e passagem pela agro fintech Traive.\nGraduado em Sistemas de Informação e Administração de Empresas, com especialização em Arquitetura de Software.\nLíder na comunidade Monolitos Valley (CE) e mentor ativo na Chingu (USA) e Abstartups.\n\nHackathons: Já conquistei o pódio em algumas maratonas e gosto muito de apoiar quem está participando pela primeira vez. Para mim, o prêmio de um hackathon você escolhe: ele vai muito além do pódio e está na visibilidade, nos contatos, na experiência e no aprendizado que você constrói.\n\nPosso ajudar seu time: Engenharia de produto, front-end, UI/UX, arquitetura de software e validação de ideias.",
  "Andreia Maria Roque": "Meu caminho sempre teve como linha condutora 'procurar projetos interessantes' que pudessem fazer a diferença no território rural, desenvolvendo conhecimento e assim melhorando nosso relacionamento com a natureza. Engenheira Agrônoma com quase 40 anos de experiência trabalhando com o desenvolvimento sustentável, turismo rural, desenvolvimento rural e políticas públicas do campo. Atuo na gestão de projetos estratégicos e transformadores em missões na América Latina, África e Europa na área de desenvolvimento rural regenerativo.",
  "PAULO AMENDOEIRA": "Bom dia, aqui é o Amendoeira.\nSou estrategista de negócios, branding, experiência do cliente (CX) e Inteligência Artificial, com mais de 25 anos de experiência ajudando empresas a transformar complexidade em decisões melhores. Ao longo da carreira liderei mais de 120 projetos para organizações como Vale, Petrobras, TV Globo, Cyrela, Renault, Cultura Inglesa e Eletrobras.\nDesde 2019 participo ativamente do ecossistema de hackathons como mentor e jurado, colaborando em iniciativas como NASA Space Apps, MIT Hackathon, GameJam+, Rio Info, Porto Hack e desafios de inovação corporativa e universitária. Para mim, hackathons são ambientes de aprendizado acelerado, colaboração e construção de soluções com potencial real.\nPosso ajudar os times com: estratégia de negócios, validação de ideias, proposta de valor, branding, Customer Experience (CX), IA aplicada, modelagem de negócios, storytelling, pitch e tomada de decisão sob incerteza.\nSerá um prazer trocar experiências com as equipes e também conhecer outros mentores e me conectar com novos profissionais do ecossistema de inovação.",
  "Ricardo Esteves Kneipp": "Boa tarde! Sou o Prof. Ricardo Kneipp | Mentor de Soluções Tecnológicas\nDoutor em Educação, professor de graduação e pós-graduação, mentor de startups e consultor em inovação. Atuo no desenvolvimento de soluções tecnológicas, gestão de projetos, inteligência artificial, educação digital e transformação de ideias em produtos e negócios de impacto. Minha missão é conectar tecnologia, empreendedorismo e educação para gerar resultados práticos."
};

function $(s){return document.querySelector(s)}
function $$(s){return document.querySelectorAll(s)}

function esp(r){return (r['\u00c1rea de atua\u00e7\u00e3o/conhecimento/especialidade (escolha at\u00e9 3 op\u00e7\u00f5es) *']||'').split(';').map(function(s){return s.trim()}).filter(Boolean)}
function des(r){return (r['Qual dos desafios voc\u00ea acredita que pode colaborar com as equipes? Selecione em ordem de prioridade e fique \u00e0 vontade para selecionar quantos desejar. *']||'').split(';').map(function(s){return s.trim().replace(/^DESAFIO \d: /,'')}).filter(Boolean)}
function inf(r){var v=(r['Informe qual *']||'').trim();return v?[v]:[]}

function contar(){
  var ec={},dc={};
  DATA.forEach(function(r){
    esp(r).concat(inf(r)).forEach(function(e){ec[e]=(ec[e]||0)+1});
    des(r).forEach(function(d){dc[d]=(dc[d]||0)+1});
  });
  return {e:Object.entries(ec).sort(function(a,b){return b[1]-a[1]}), d:Object.entries(dc).sort(function(a,b){return b[1]-a[1]})};
}

function montarFiltros(){
  var c=contar(),h='';
  h+='<div class="tag-filter-group"><div class="label">Especialidades</div><div class="tags">';
  c.e.forEach(function(x){var t=x[0],n=x[1],a=sel.e.has(t)?'active':'';h+='<button class="tag-btn '+a+'" data-g="e" data-t="'+esc(t)+'">'+esc(t)+' <span class="count">('+n+')</span></button>'});
  h+='</div></div><div class="tag-filter-group"><div class="label">Desafios</div><div class="tags">';
  c.d.forEach(function(x){var t=x[0],n=x[1],a=sel.d.has(t)?'active':'';h+='<button class="tag-btn '+a+'" data-g="d" data-t="'+esc(t)+'">'+esc(t)+' <span class="count">('+n+')</span></button>'});
  h+='</div></div><div class="tag-filter-group"><div class="label">Discord</div><div class="tags">';
  var discOpts=[["Com Discord",DATA.filter(function(r){var nk=r['NICK DISCORD']||'';return nk&&nk!='N\u00e3o Entrou'}).length],["Sem Discord",DATA.filter(function(r){var nk=r['NICK DISCORD']||'';return !nk||nk=='N\u00e3o Entrou'||nk=='N\u00e3o'}).length]];
  discOpts.forEach(function(x){var t=x[0],n=x[1],a=sel.disc.has(t)?'active':'';h+='<button class="tag-btn '+a+'" data-g="disc" data-t="'+esc(t)+'">'+esc(t)+' <span class="count">('+n+')</span></button>'});
  h+='</div></div>';
  $('#filterArea').innerHTML=h;
  $$('#filterArea .tag-btn').forEach(function(b){b.addEventListener('click',function(){var m=b.dataset.g==='e'?sel.e:b.dataset.g==='d'?sel.d:sel.disc;if(m.has(b.dataset.t)){m.delete(b.dataset.t);b.classList.remove('active')}else{m.add(b.dataset.t);b.classList.add('active')}render(1)})});
}

function filtrar(){
  var q=$('#filterSearch').value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  return DATA.filter(function(r){
    if(sel.e.size&&!esp(r).some(function(e){return sel.e.has(e)}))return false;
    if(sel.d.size&&!des(r).some(function(d){return sel.d.has(d)}))return false;
    if(sel.disc.size){var nk=r['NICK DISCORD']||'';var hasDisc=nk&&nk!='N\u00e3o Entrou'&&nk!='N\u00e3o';if(sel.disc.has('Com Discord')&&!hasDisc)return false;if(sel.disc.has('Sem Discord')&&hasDisc)return false}
    if(q){var h=((r['Nome Completo *']||'')+' '+(r['E-mail *']||'')+' '+(r['Estado *']||'')).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');if(!h.includes(q))return false}
    return true;
  });
}

function atualizarBtns(){$$('#filterArea .tag-btn').forEach(function(b){var m=b.dataset.g==='e'?sel.e:b.dataset.g==='d'?sel.d:sel.disc;b.classList.toggle('active',m.has(b.dataset.t))})}

function copia(texto,el){
  navigator.clipboard.writeText(texto).then(function(){
    if(el){var o=el.textContent;el.textContent='Copiado!';el.classList.add('copied');setTimeout(function(){el.textContent=o;el.classList.remove('copied')},1200)}
  });
}

function render(p){
  var f=filtrar(),tp=Math.ceil(f.length/N)||1;
  if(p<1)p=1;if(p>tp)p=tp;pg=p;
  $('#stats').textContent=f.length+' mentor(es) encontrados';
  var s=(p-1)*N,pd=f.slice(s,s+N),c=$('#cardsContainer');
  c.innerHTML='';
  pd.forEach(function(r){
    var n=r['Nome Completo *']||'', em=r['E-mail *']||'', tel=r['Telefone (WhatsApp) *']||'', est=r['Estado *']||'', el=esp(r),dl=des(r),il=inf(r);
    var nick=r['NICK DISCORD']||'', taDisc=r['TA NO DISCORD?']||'';
    var iniciais=n.split(' ').map(function(s){return s[0]}).filter(Boolean).slice(0,2).join('').toUpperCase();
    var discExibe = (nick&&nick!='N\u00e3o Entrou') ? nick : '';
    var discOn = taDisc=='Sim';
    var card=document.createElement('div');
    card.className='card';
        var cargo = r['Cargo que ocupa']||'', linkedin = r['Link do curr\u00edculo ou linkedin *']||'', formacao = r['Forma\u00e7\u00e3o Acad\u00eamica *']||'', atua = r['Atualmente, voc\u00ea atua onde? *']||'';
    var bioTxt = (cargo?cargo+'\n':'')+(formacao?formacao+'\n':'')+(atua?'Atua: '+atua:'');
    card.innerHTML='<div class="card-row card-row-top"><div class="card-avatar">'+esc(iniciais)+'</div><div class="card-info"><div class="card-nome">'+esc(n)+' <span class="card-estado">'+esc(est)+'</span><button class="bio-btn" data-bio=\''+esc(bioTxt)+'\' data-linkedin="'+esc(linkedin)+'" data-nome="'+esc(n)+'">BIO</button></div><div class="card-email" data-copy="'+esc(em)+'">'+esc(em)+'</div></div></div><div class="card-linha-contato"><div class="card-discord">'+(discExibe?'<svg width="18" height="18" viewBox="0 0 24 24" fill="#5865F2"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.054C1.482 8.205.726 11.937.925 15.604a.074.074 0 0 0 .042.059 19.916 19.916 0 0 0 5.994 3.032.076.076 0 0 0 .08-.025 14.09 14.09 0 0 0 1.226-1.994.072.072 0 0 0-.04-.1 13.116 13.116 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.1c.36.698.772 1.362 1.225 1.994a.076.076 0 0 0 .08.025 19.839 19.839 0 0 0 6.12-3.032.077.077 0 0 0 .041-.059c.238-4.202-.668-7.895-2.757-11.18a.063.063 0 0 0-.031-.054zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.095 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.095 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/></svg>':'')+(discExibe?'<span class="nick" data-copy="'+esc(discExibe)+'">'+esc(discExibe)+'</span>':'<span style="color:rgba(255,255,255,.25);font-size:.7rem">Sem Discord</span>')+' <span class="status-dot '+(discOn?'on':'off')+'"></span></div>'+
      '<span class="card-wpp" data-copy="'+esc(tel)+'"><svg width="14" height="14" viewBox="0 0 24 24" fill="#25D366"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-1.099-1.028-1.84-2.268-2.055-2.65-.216-.382-.023-.589.163-.775.166-.166.373-.433.56-.65.187-.217.25-.372.374-.62.124-.248.062-.468-.031-.65-.093-.182-.67-1.616-.92-2.214-.242-.58-.487-.48-.67-.488-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.199 2.095 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.545.796 4.913 2.156 6.84L.808 23.293l4.674-1.33A11.943 11.943 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.86 0-3.636-.51-5.186-1.473l-.373-.224-2.36.672.654-2.263-.249-.392A9.962 9.962 0 012 12C2 6.486 6.486 2 12 2s10 4.486 10 10-4.486 10-10 10z"/></svg> '+esc(tel)+'</span>'+
    '</div><div class="card-tags">'+
      el.concat(il).map(function(x){return '<span class="tag" data-g="e" data-t="'+esc(x)+'">'+esc(x)+'</span>'}).join('')+
      dl.map(function(x){return '<span class="tag tag-desafio" data-g="d" data-t="'+esc(x)+'">'+esc(x)+'</span>'}).join('')+
    '</div></div>';
    c.appendChild(card);
  });

  // clique nas tags dos cards
  $$('#cardsContainer .tag').forEach(function(t){t.addEventListener('click',function(){var m=t.dataset.g==='e'?sel.e:sel.d;if(!m.has(t.dataset.t)){m.add(t.dataset.t);atualizarBtns();render(1)}})});

  // clique p/ copiar (email, tel, discord, botao)
  $$('#cardsContainer [data-copy]').forEach(function(el){el.addEventListener('click',function(){copia(el.dataset.copy,el)})});
  // clique bio
  $$('#cardsContainer .bio-btn').forEach(function(b){
    b.addEventListener('click',function(){
      var nome=b.dataset.nome, txt=BIOS[nome], li=b.dataset.linkedin;
      var h='<h2>'+esc(nome)+'</h2>';
      if(li) h+='<a class="bio-linkedin" href="'+esc(li)+'" target="_blank">LinkedIn</a>';
      h+='<div class="bio-text">'+esc(txt||'Bio n\u00e3o dispon\u00edvel')+'</div>';
      $('#bioContent').innerHTML=h;
      $('#bioOverlay').classList.add('show');
    });
  });

  $('#pagination').innerHTML='<button onclick="go('+(p-1)+')"'+(p<=1?' disabled':'')+'>Anterior</button><span>Pagina '+p+' de '+tp+'</span><button onclick="go('+(p+1)+')"'+(p>=tp?' disabled':'')+'>Proxima</button>';
}

function go(p){render(p)}
function fecharBio(){$$('#bioOverlay').forEach(function(o){o.classList.remove('show')})}
$('#bioOverlay').addEventListener('click',function(e){if(e.target===this)fecharBio()});

function copiarTodosVisiveis(){
  var v=filtrar(),t=v.map(function(r){return (r['Nome Completo *']||'')+' - '+(r['E-mail *']||'')+' - '+(r['Telefone (WhatsApp) *']||'')+(r['NICK DISCORD']&&r['NICK DISCORD']!='N\u00e3o Entrou'?' - '+r['NICK DISCORD']:'')}).join('\n');
  navigator.clipboard.writeText(t).then(function(){alert(t.split('\n').length+' contatos copiados!')});
}

function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML}

$('#filterSearch').addEventListener('input',function(){render(1)})
montarFiltros()
render(1)
</script>
</body>
</html>'''

html = template.replace('__DATA__', minified)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('OK size:', os.path.getsize('index.html'))
print('Has cards:', 'grid-cards' in html)
