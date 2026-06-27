import streamlit as st
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import re

PASTA_TXT = Path("C:/OPENCODE/HACKATON/extraido")
PASTA_DB = Path("C:/OPENCODE/HACKATON/chroma_db_simples")
PASTA_DB.mkdir(exist_ok=True)

def chunk_text(texto, fonte, chunk_size=500, overlap=50):
    paragrafos = re.split(r'\n\s*\n', texto)
    chunks = []
    buffer = ""
    for p in paragrafos:
        if len(buffer) + len(p) < chunk_size:
            buffer += p + "\n"
        else:
            if buffer:
                chunks.append({"texto": buffer.strip(), "fonte": fonte})
            buffer = p + "\n"
    if buffer:
        chunks.append({"texto": buffer.strip(), "fonte": fonte})
    return chunks

@st.cache_resource
def carregar_base():
    arquivo_chunks = PASTA_DB / "chunks.pkl"
    arquivo_embeddings = PASTA_DB / "embeddings.npy"

    if arquivo_chunks.exists() and arquivo_embeddings.exists():
        with open(arquivo_chunks, "rb") as f:
            chunks = pickle.load(f)
        embeddings = np.load(arquivo_embeddings)
        modelo = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return modelo, chunks, embeddings

    st.info("Indexando os PDFs pela primeira vez...")
    modelo = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    chunks = []
    for arquivo in PASTA_TXT.glob("*.txt"):
        conteudo = arquivo.read_text(encoding="utf-8")
        chunks.extend(chunk_text(conteudo, arquivo.stem))

    textos = [c["texto"] for c in chunks]
    embeddings = modelo.encode(textos, show_progress_bar=True)

    with open(arquivo_chunks, "wb") as f:
        pickle.dump(chunks, f)
    np.save(arquivo_embeddings, embeddings)

    return modelo, chunks, embeddings

def buscar(pergunta, modelo, chunks, embeddings, k=3):
    emb_pergunta = modelo.encode([pergunta])
    from sklearn.metrics.pairwise import cosine_similarity
    similaridades = cosine_similarity(emb_pergunta, embeddings)[0]
    indices = np.argsort(similaridades)[-k:][::-1]
    resultados = [(chunks[i], similaridades[i]) for i in indices]
    return resultados

st.set_page_config(page_title="haCARthon Chatbot", page_icon="🚗")
st.title("haCARthon - Chatbot de Duvidas")

with st.spinner("Carregando base de conhecimento..."):
    modelo, chunks, embeddings = carregar_base()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["papel"]):
        st.markdown(msg["conteudo"])

pergunta = st.chat_input("Cole sua duvida aqui...")

if pergunta:
    st.session_state.mensagens.append({"papel": "user", "conteudo": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando resposta..."):
            resultados = buscar(pergunta, modelo, chunks, embeddings, k=3)
            partes = []
            fontes = set()
            for chunk, score in resultados:
                partes.append(chunk["texto"])
                fontes.add(chunk["fonte"])
            contexto = "\n\n".join(partes)
            resposta = f"""**Resposta baseada nos documentos:**

{contexto}

---
*Fontes: {", ".join(fontes)}*"""

        st.markdown(resposta)

    st.session_state.mensagens.append({"papel": "assistant", "conteudo": resposta})
