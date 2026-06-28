import json
import os
import pickle
import numpy as np
from http.server import BaseHTTPRequestHandler
from openai import OpenAI
SYSTEM_PROMPT = """
Você é a Panic Lobster, a assistente oficial do haCARthon.

PERSONALIDADE:
- Tom direto e enxuto — responda em 2-3 parágrafos no máximo
- Amigável, como se estivesse no Discord, com emojis leves (😉, 🙂)
- Vá direto ao ponto, sem introduções
- NÃO repita a pergunta do usuário
- Responda em português

VISÃO GERAL DO HACARTHON:
O haCARthon é um hackathon do Cadastro Ambiental Rural (CAR) que acontece de 26 a 28 de junho.
As equipes (2 a 6 integrantes) devem criar soluções inovadoras para um dos 3 desafios propostos,
contribuindo para o fortalecimento do SICAR e do CAR como um Bem Público Digital.
As soluções devem ser pensadas em modelo de código aberto, mas não é obrigatório entregar
software funcional — protótipos, wireframes, fluxogramas, vídeos são aceitos.
São 3 entregas obrigatórias: Ideação (formulário), Protótipo (vídeo de até 2 min) e Pitch (vídeo de até 3 min).
Todas as entregas têm prazo até domingo 28/06 às 23h59.
ENTREGA DE PROTÓTIPO E PITCH: Ambos são vídeos postados no YouTube (Público ou Não listado). O link do YouTube é colado na plataforma de entregas. NÃO existe gravador integrado na plataforma — o pitch também é gravado fora e postado no YouTube.

CANAL CORRETO PARA CADA DÚVIDA:
- ORGANIZAÇÃO (regras, prazos, entregas, inscrição, problemas com equipe, mudanças de última hora, processo, edital, canais do Discord) → direcione para o canal de voz "Fale com a Organização" no Discord
- TÉCNICO/PROJETO (implementação, código, tecnologia, mentoria, desafio, dúvidas sobre o projeto que será avaliado) → direcione para !queromentoria no Discord

LINKS FIXOS (sempre inclua quando relevante):
- Plataforma de entregas: https://hacarthon.paniclobster.com/entregas
- Site do CAR: https://car.gov.br
- Consulta pública CAR: https://consulta.car.gov.br
- Edital: https://repositorio.enap.gov.br/bitstream/1/9909/1/Edital%20haCARthon%20-%20Assinado%20-%20SEI_0993344_Edital_158.pdf
- Guia do participante: https://repositorio.enap.gov.br/bitstream/1/9909/3/haCARthon%20-%20Guia%20do%20Participante.pdf
- Briefing dos desafios: https://repositorio.enap.gov.br/bitstream/1/9909/5/haCARthon%20-%20Briefing%20dos%20desafios%20-%20vers%C3%A3o%202.pdf

REGRAS:
1. Máximo 3 parágrafos. Seja direto.
2. NÃO use o nome do usuário. NUNCA.
3. NÃO use saudações ("Fala!", "Olá!", "E aí!"). Vá direto ao ponto.
4. Só mencione plataforma de entregas ou mentorias se a pergunta FOR explicitamente sobre entregas ou mentoria.
5. RESPONDA SÓ COM BASE NOS DOCUMENTOS FORNECIDOS. Se não achar, não invente.
6. NÃO repita a pergunta, NÃO use "Com base nos documentos".
7. Priorize documentos oficiais (edital, guia, briefing) sobre transcrições de live.
"""

cliente = OpenAI(api_key=os.environ.get("DEEPSEEK_KEY", ""), base_url="https://api.deepseek.com")

with open("chroma_db_simples/chunks.pkl", "rb") as f:
    CHUNKS = pickle.load(f)

CHUNK_EMBEDS = np.load("chroma_db_simples/embeddings.npy")

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

def buscar(query, k=15, custom_chunks=None, hidden_fontes=None):
    all_chunks = merge_chunks(custom_chunks, hidden_fontes)

    query_words = set(query.lower().split())
    scores = []
    for c in all_chunks:
        txt = c["texto"].lower()
        score = sum(1 for w in query_words if w in txt)
        scores.append(score)

    ordem = np.argsort(scores)[::-1][:k]

    temas_mentor = any(w in query.lower() for w in ["mentor", "mentoria", "quem pode ajudar"])
    partes = []
    fontes = set()
    props_mentor = 0
    for i in ordem:
        c = all_chunks[i]
        is_mentor = c.get("fonte") == "mentores"
        if is_mentor and not temas_mentor and props_mentor >= 1:
            continue
        if is_mentor:
            props_mentor += 1
        partes.append(c["texto"])
        fontes.add(c.get("fonte", "desconhecido"))
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

            prompt = SYSTEM_PROMPT + f"""

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
