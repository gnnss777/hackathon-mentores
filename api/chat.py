import json
import os
from http.server import BaseHTTPRequestHandler
from openai import OpenAI
import re

cliente = OpenAI(api_key=os.environ.get("DEEPSEEK_KEY", ""), base_url="https://api.deepseek.com")

with open("api/chunks.json", encoding="utf-8") as f:
    CHUNKS = json.load(f)

CUSTOM_CHUNKS = []
custom_path = "api/custom_chunks.json"
if os.path.exists(custom_path):
    with open(custom_path, encoding="utf-8") as f:
        CUSTOM_CHUNKS = json.load(f)

def merge_chunks(custom_chunks=None, hidden_fontes=None):
    base = list(CHUNKS)
    for c in CUSTOM_CHUNKS:
        if "texto" in c and "fonte" in c:
            base.append(c)
    if hidden_fontes and isinstance(hidden_fontes, list):
        base = [c for c in base if c["fonte"] not in hidden_fontes]
    if custom_chunks and isinstance(custom_chunks, list):
        for c in custom_chunks:
            if "texto" in c and "fonte" in c:
                base.append(c)
    return base

def buscar(query, k=12, custom_chunks=None, hidden_fontes=None):
    all_chunks = merge_chunks(custom_chunks, hidden_fontes)
    q_words = set(re.sub(r'[^a-z0-9\s]', '', query.lower()).split())
    scores = []
    for i, c in enumerate(all_chunks):
        c_words = set(re.sub(r'[^a-z0-9\s]', '', c["texto"].lower()).split())
        overlap = len(q_words & c_words)
        if overlap > 0:
            scores.append((overlap, i))
    scores.sort(key=lambda x: (-x[0], -len(all_chunks[x[1]]["texto"])))
    indices = [i for _, i in scores[:k]]

    temas_mentor = any(w in query.lower() for w in ["mentor", "mentoria", "quem pode ajudar"])
    partes = []
    fontes = set()
    props_mentor = 0
    for i in indices:
        c = all_chunks[i]
        is_mentor = c["fonte"] == "mentores"
        if is_mentor and not temas_mentor and props_mentor >= 1:
            continue
        if is_mentor:
            props_mentor += 1
        partes.append(c["texto"])
        fontes.add(c["fonte"])
    return partes, fontes, all_chunks

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            pergunta = data.get("pergunta", "").strip()
            historico = data.get("historico", "")
            custom_chunks = data.get("customChunks", None)
            hidden_fontes = data.get("hiddenFontes", None)

            if not pergunta:
                raise ValueError("Pergunta vazia")

            partes, fontes, _ = buscar(pergunta, custom_chunks=custom_chunks, hidden_fontes=hidden_fontes)
            contexto = "\n\n".join(partes)

            prompt = f"""Você é a Panic Lobster, a assistente oficial do haCARthon (hackathon do CAR). Seu estilo é:
- Amigável e acolhedor(a), como se estivesse conversando com um participante no Discord
- Responde de forma direta e prática, mas completa — nada de respostas de uma linha só
- Usa um tom humano, com emojis leves como 😉, 🙂 quando apropriado
- Inclui links, tutoriais e orientações passo-a-passo sempre que possível
- NUNCA use introduções como "Com base nos documentos" — vá direto ao ponto
- Responda em português, de forma clara e natural

Primeiro, identifique o tipo de dúvida do usuário:
- Se for sobre ORGANIZAÇÃO DO HACKATHON (regras, prazos, entregas, inscrição, problemas com equipe, mudanças de última hora, processo do hackathon, tipos de entrega, dúvidas sobre o edital, canais do Discord, etc.) → direcione para o canal de voz "Fale com a Organização" no Discord. A organização do evento ajuda com essas questões.
- Se for sobre PROJETO TÉCNICO (tecnologia, implementação, código, dúvidas técnicas sobre o projeto que será avaliado, mentoria, ajuda com desafio) → direcione para os mentores acadêmicos usando o comando !queromentoria no Discord. Os mentores são acadêmicos especialistas em diversas áreas que ajudam os alunos com dúvidas técnicas dos projetos.

REGRAS:
1. Responda de forma completa e útil — explique o contexto, dê os detalhes, mostre o caminho.
2. Se encontrar a resposta nos documentos, responda com os fatos e detalhes disponíveis.
3. SEMPRE indique qual canal procurar ao final, quando a dúvida não for totalmente resolvida pelos documentos.
4. Use o histórico pra manter contexto e evitar repetições.
5. Quando mencionar uma plataforma, URL, ferramenta, sistema, ambiente ou recurso, inclua o link completo se ele estiver disponível nos documentos. Ex: "plataforma de entregas: https://hacarthon.paniclobster.com/entregas" ou "site do CAR: https://car.gov.br".
6. Seja completa — se o documento tiver a informação, entregue ela inteira, não resumida demais.

HISTÓRICO RECENTE:
{historico}
DOCUMENTOS RELEVANTES:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""

            resposta_api = cliente.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            texto = resposta_api.choices[0].message.content

            response = json.dumps({
                "resposta": texto,
                "fontes": sorted(fontes)
            }, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response)

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"erro": str(e)}, ensure_ascii=False).encode("utf-8"))
