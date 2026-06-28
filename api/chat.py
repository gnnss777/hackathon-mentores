import json
import os
from http.server import BaseHTTPRequestHandler
from openai import OpenAI
import re

cliente = OpenAI(api_key=os.environ.get("DEEPSEEK_KEY", ""), base_url="https://api.deepseek.com")

with open("api/chunks.json", encoding="utf-8") as f:
    CHUNKS = json.load(f)

def buscar(query, k=8):
    q_words = set(re.sub(r'[^a-z0-9\s]', '', query.lower()).split())
    scores = []
    for i, c in enumerate(CHUNKS):
        c_words = set(re.sub(r'[^a-z0-9\s]', '', c["texto"].lower()).split())
        overlap = len(q_words & c_words)
        if overlap > 0:
            scores.append((overlap, i))
    scores.sort(key=lambda x: (-x[0], -len(CHUNKS[x[1]]["texto"])))
    indices = [i for _, i in scores[:k]]

    temas_mentor = any(w in query.lower() for w in ["mentor", "mentoria", "quem pode ajudar"])
    partes = []
    fontes = set()
    props_mentor = 0
    for i in indices:
        c = CHUNKS[i]
        is_mentor = c["fonte"] == "mentores"
        if is_mentor and not temas_mentor and props_mentor >= 1:
            continue
        if is_mentor:
            props_mentor += 1
        partes.append(c["texto"])
        fontes.add(c["fonte"])
    return partes, fontes

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

            if not pergunta:
                raise ValueError("Pergunta vazia")

            partes, fontes = buscar(pergunta)
            contexto = "\n\n".join(partes)

            prompt = f"""Você é um assistente especializado no haCARthon, um hackathon do Cadastro Ambiental Rural (CAR).

REGRAS:
1. Priorize lives de tira-dúvidas, lives de orientação, PDFs e documentos oficiais.
2. Se encontrar a resposta nos documentos, responda com base neles e NÃO mencione mentores.
3. Se NÃO encontrar resposta nos documentos, sugira procurar um mentor especialista e diga "Você pode pedir mentoria no Discord com !queromentoria".
4. Só liste mentores específicos se a pergunta for sobre "mentor", "mentoria" ou "quem pode ajudar".
5. Use o histórico da conversa para manter contexto.

Responda em português de forma clara, natural e completa.

HISTÓRICO RECENTE:
{historico}
DOCUMENTOS RELEVANTES:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""

            resposta_api = cliente.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1200
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
