import streamlit as st
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import re
import csv
import json
import os
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from PyPDF2 import PdfReader
import tempfile
import shutil

cliente = OpenAI(api_key=os.environ.get("DEEPSEEK_KEY", ""), base_url="https://api.deepseek.com")

PASTA_HACK = Path("C:/OPENCODE/HACKATON")
PASTA_TXT = PASTA_HACK / "extraido"
PASTA_DB = PASTA_HACK / "chroma_db_simples"
ARQUIVO_META = PASTA_HACK / "documentos_meta.json"
PASTA_TXT.mkdir(exist_ok=True)
PASTA_DB.mkdir(exist_ok=True)

def carregar_metadados():
    if ARQUIVO_META.exists():
        with open(ARQUIVO_META, encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_metadados(meta):
    with open(ARQUIVO_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

def chunk_text(texto, fonte, chunk_size=500, overlap=50):
    if fonte.startswith("yt_"):
        linhas = texto.split("\n")
        partes = []
        parte = []
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            parte.append(linha)
            if len(" ".join(parte)) >= chunk_size:
                partes.append(" ".join(parte))
                parte = []
        if parte:
            partes.append(" ".join(parte))
        chunks = [{"texto": p, "fonte": fonte} for p in partes]
        if not chunks:
            chunks = [{"texto": texto[:500], "fonte": fonte}]
        return chunks
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

def ler_markdown():
    caminho = PASTA_HACK / "DOCUMENTOS HACARTON INFOS.md"
    if not caminho.exists():
        return []
    texto = caminho.read_text(encoding="utf-8")
    return chunk_text(texto, "avisos-programacao")

def ler_mentores():
    caminho_json = PASTA_HACK / "mentores_final.json"
    caminho_csv = PASTA_HACK / "haCARthon - Inscri\u00e7\u00f5es - Mentor.csv"
    dados = []
    if caminho_json.exists():
        with open(caminho_json, encoding="utf-8") as f:
            dados = json.load(f)
    elif caminho_csv.exists():
        with open(caminho_csv, encoding="utf-8-sig") as f:
            dados = list(csv.DictReader(f))
    chunks = []
    for mentor in dados:
        nome = (mentor.get("Nome Completo *") or "").strip()
        if not nome:
            continue
        especialidade = mentor.get("\u00c1rea de atua\u00e7\u00e3o/conhecimento/especialidade (escolha at\u00e9 3 op\u00e7\u00f5es) *", "")
        desafios = mentor.get("Qual dos desafios voc\u00ea acredita que pode colaborar com as equipes? Selecione em ordem de prioridade e fique \u00e0 vontade para selecionar quantos desejar. *", "")
        cargo = mentor.get("Cargo que ocupa", "")
        estado = mentor.get("Estado *", "")
        cidade = mentor.get("Cidade *", "")
        linkedin = mentor.get("Link do curr\u00edculo ou linkedin *", "")
        discord = mentor.get("NICK DISCORD", "")
        texto = f"Mentor: {nome}. Cargo: {cargo}. Localiza\u00e7\u00e3o: {cidade}/{estado}. Especialidades: {especialidade}. Desafios que pode ajudar: {desafios}. Discord: {discord}. LinkedIn: {linkedin}."
        chunks.append({"texto": texto, "fonte": "mentores"})
    return chunks

def extrair_pdf_texto(conteudo_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(conteudo_bytes)
        tmp_path = tmp.name
    try:
        reader = PdfReader(tmp_path)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() + "\n"
        return texto
    finally:
        Path(tmp_path).unlink(missing_ok=True)

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
    st.info("Indexando documentos...")
    modelo = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    chunks = []
    for arquivo in PASTA_TXT.glob("*.txt"):
        if arquivo.name == "mentores_padrao.txt":
            continue
        conteudo = arquivo.read_text(encoding="utf-8")
        chunks.extend(chunk_text(conteudo, arquivo.stem))
    chunks.extend(ler_markdown())
    chunks.extend(ler_mentores())
    textos = [c["texto"] for c in chunks]
    embeddings = modelo.encode(textos, show_progress_bar=True)
    with open(arquivo_chunks, "wb") as f:
        pickle.dump(chunks, f)
    np.save(arquivo_embeddings, embeddings)
    return modelo, chunks, embeddings

def limpar_cache():
    for f in PASTA_DB.glob("*"):
        f.unlink()
    st.cache_resource.clear()

def buscar(pergunta, modelo, chunks, embeddings, k=5):
    emb_pergunta = modelo.encode([pergunta])
    from sklearn.metrics.pairwise import cosine_similarity
    similaridades = cosine_similarity(emb_pergunta, embeddings)[0]
    indices = np.argsort(similaridades)[-k:][::-1]
    resultados = [(chunks[i], similaridades[i]) for i in indices]
    return resultados

st.set_page_config(page_title="haCARthon Chatbot", page_icon="🚗", layout="wide")

with st.sidebar:
    st.image("https://placehold.co/200x60/1A1A2E/EC008C?text=haCARthon&font=source-sans-pro")
    st.divider()
    pagina = st.radio("", ["Chat", "Gerenciar Documentos"])

meta = carregar_metadados()

if pagina == "Gerenciar Documentos":
    st.title("Gerenciar Documentos")

    aba_adicionar, aba_youtube, aba_listar = st.tabs(["Adicionar PDF", "Adicionar YouTube", "Ver/Remover Documentos"])

    with aba_adicionar:
        uploaded = st.file_uploader("Upload de PDF, TXT ou MD", type=["pdf", "txt", "md"], accept_multiple_files=True)
        if uploaded:
            for arquivo in uploaded:
                if arquivo.name.endswith(".pdf"):
                    texto = extrair_pdf_texto(arquivo.read())
                    nome_base = Path(arquivo.name).stem
                else:
                    texto = arquivo.read().decode("utf-8")
                    nome_base = Path(arquivo.name).stem
                caminho = PASTA_TXT / f"{nome_base}.txt"
                if not caminho.exists():
                    caminho.write_text(texto, encoding="utf-8")
                    meta[str(caminho.name)] = {"tipo": "upload", "nome_original": arquivo.name}
                    salvar_metadados(meta)
                    st.success(f"Adicionado: {arquivo.name}")
                else:
                    st.warning(f"J existe: {arquivo.name}")
            limpar_cache()
            st.rerun()

    with aba_youtube:
        url = st.text_input("URL do YouTube")
        nome_personalizado = st.text_input("Nome personalizado (opcional)")
        if st.button("Adicionar Transcrição") and url:
            match = re.search(r"(?:v=|youtu\.be/|/shorts/)([a-zA-Z0-9_-]{11})", url)
            if not match:
                st.error("URL inválida")
            else:
                video_id = match.group(1)
                try:
                    api_yt = YouTubeTranscriptApi()
                    transcricao = api_yt.fetch(video_id, languages=["pt"])
                    texto = " ".join([s.text for s in transcricao.snippets])
                    nome = nome_personalizado.strip() or f"youtube_{video_id}"
                    caminho = PASTA_TXT / f"{nome}.txt"
                    if not caminho.exists():
                        caminho.write_text(texto, encoding="utf-8")
                        meta[str(caminho.name)] = {"tipo": "youtube", "url": url, "video_id": video_id}
                        salvar_metadados(meta)
                        st.success(f"Transcrição adicionada: {nome}")
                    else:
                        st.warning(f"J existe um documento com esse nome")
                    limpar_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    with aba_listar:
        arquivos = sorted(PASTA_TXT.glob("*.txt"))
        if not arquivos:
            st.info("Nenhum documento extra encontrado.")
        for caminho in arquivos:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                info = meta.get(caminho.name, {})
                tipo = info.get("tipo", "padrão")
                nome_exibicao = info.get("nome_original", caminho.stem)
                st.write(f"**{nome_exibicao}** ({tipo})")
                st.caption(f"{caminho.name} - {len(caminho.read_text(encoding='utf-8'))} chars")
            with col2:
                if st.button("Abrir", key=f"abrir_{caminho.name}"):
                    st.session_state["arquivo_visualizar"] = caminho.name
            with col3:
                if tipo in ("upload", "youtube"):
                    if st.button("Excluir", key=f"del_{caminho.name}"):
                        caminho.unlink()
                        meta.pop(caminho.name, None)
                        salvar_metadados(meta)
                        limpar_cache()
                        st.rerun()

        if "arquivo_visualizar" in st.session_state:
            nome_arquivo = st.session_state["arquivo_visualizar"]
            caminho = PASTA_TXT / nome_arquivo
            if caminho.exists():
                with st.expander(f"Conteúdo: {nome_arquivo}", expanded=True):
                    st.text(caminho.read_text(encoding="utf-8")[:5000])
                    if len(caminho.read_text(encoding="utf-8")) > 5000:
                        st.caption("Mostrando primeiros 5000 caracteres")

else:
    st.title("haCARthon - Chatbot de Dúvidas")
    st.caption("Pergunte sobre o hackathon, desafios, mentores, programação e documentos")

    with st.spinner("Carregando base de conhecimento..."):
        modelo, chunks, embeddings = carregar_base()

    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    for msg in st.session_state.mensagens:
        with st.chat_message(msg["papel"]):
            st.markdown(msg["conteudo"])

    pergunta = st.chat_input("Cole sua dúvida aqui...")

    if pergunta:
        st.session_state.mensagens.append({"papel": "user", "conteudo": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)

        with st.chat_message("assistant"):
            with st.spinner("Consultando documentos..."):
                k = 8 if any(w in pergunta.lower() for w in ["mentor", "mentoria", "quem pode ajudar"]) else 5
                resultados = buscar(pergunta, modelo, chunks, embeddings, k=k)

                partes = []
                fontes = set()
                props_mentor = 0
                for chunk, score in resultados:
                    is_mentor = chunk["fonte"] == "mentores"
                    temas_mentor = any(w in pergunta.lower() for w in ["mentor", "mentoria", "quem pode ajudar"])
                    if is_mentor and not temas_mentor and props_mentor >= 1:
                        continue
                    if is_mentor:
                        props_mentor += 1
                    partes.append(chunk["texto"])
                    fontes.add(chunk["fonte"])
                contexto = "\n\n".join(partes)

                historico = ""
                for msg in st.session_state.mensagens[-6:-1]:
                    papel = "Usuário" if msg["papel"] == "user" else "Assistente"
                    historico += f"{papel}: {msg['conteudo']}\n\n"

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
1. Priorize lives de tira-dúvidas, lives de orientação, PDFs e documentos oficiais.
2. Se encontrar a resposta nos documentos, responda com base neles de forma completa.
3. SEMPRE indique qual canal procurar ao final, quando a dúvida não for totalmente resolvida pelos documentos.
4. Só liste mentores específicos se a pergunta for sobre "mentor", "mentoria" ou "quem pode ajudar".
5. Use o histórico da conversa para manter contexto e melhorar as respostas.
6. Seja completa — se o documento tiver a informação, entregue ela inteira, não resumida demais.

HISTÓRICO RECENTE:
{historico}
DOCUMENTOS RELEVANTES:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""

                try:
                    resposta_api = cliente.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=1200
                    )
                    texto_resposta = resposta_api.choices[0].message.content
                except Exception as e:
                    texto_resposta = f"Erro ao consultar DeepSeek: {e}"

                resposta = f"""{texto_resposta}

---
*Fontes: {", ".join(sorted(set(fontes)))}*"""

            st.markdown(resposta)

        st.session_state.mensagens.append({"papel": "assistant", "conteudo": resposta})
