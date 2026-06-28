import json
import os
import pickle
import numpy as np
from http.server import BaseHTTPRequestHandler
from openai import OpenAI
from system_prompt import SYSTEM_PROMPT

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
