import json
import os
import pickle
import numpy as np
from http.server import BaseHTTPRequestHandler
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from system_prompt import SYSTEM_PROMPT

cliente = OpenAI(api_key=os.environ.get("DEEPSEEK_KEY", ""), base_url="https://api.deepseek.com")

with open("api/chunks.json", encoding="utf-8") as f:
    CHUNKS = json.load(f)

modelo = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
CHUNK_EMBEDS = modelo.encode([c["texto"] for c in CHUNKS], show_progress_bar=False)

CUSTOM_CHUNKS = []
custom_path = "api/custom_chunks.json"
if os.path.exists(custom_path):
    with open(custom_path, encoding="utf-8") as f:
        CUSTOM_CHUNKS = json.load(f)
CUSTOM_EMBEDS = None
if CUSTOM_CHUNKS:
    CUSTOM_EMBEDS = modelo.encode([c["texto"] for c in CUSTOM_CHUNKS], show_progress_bar=False)

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
    query_emb = modelo.encode([query], show_progress_bar=False)[0]

    base_emb = CHUNK_EMBEDS
    if CUSTOM_EMBEDS is not None:
        base_emb = np.vstack([base_emb, CUSTOM_EMBEDS])

    if custom_chunks:
        extra_texts = [c["texto"] for c in custom_chunks if "texto" in c]
        if extra_texts:
            extra_emb = modelo.encode(extra_texts, show_progress_bar=False)
            base_emb = np.vstack([base_emb, extra_emb])

    if hidden_fontes:
        mask = np.ones(len(all_chunks), dtype=bool)
        for i, c in enumerate(all_chunks):
            if c.get("fonte") in hidden_fontes:
                mask[i] = False
        all_chunks = [c for i, c in enumerate(all_chunks) if mask[i]]
        base_emb = base_emb[mask]

    query_norm = query_emb / (np.linalg.norm(query_emb) + 1e-10)
    emb_norm = base_emb / (np.linalg.norm(base_emb, axis=1, keepdims=True) + 1e-10)
    scores = np.dot(emb_norm, query_norm)

    ordem = np.argsort(scores)[::-1][:k]
    indices = []
    pesos = []
    for i in ordem:
        indices.append(i)
        peso = scores[i]
        c = all_chunks[i]
        if c.get("tipo") == "alta":
            peso *= 1.3
        elif c.get("tipo") == "baixa":
            peso *= 0.7
        pesos.append(peso)
    ordem_pesos = np.argsort(pesos)[::-1]
    indices = [indices[i] for i in ordem_pesos]

    temas_mentor = any(w in query.lower() for w in ["mentor", "mentoria", "quem pode ajudar"])
    partes = []
    fontes = set()
    props_mentor = 0
    for i in indices:
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
