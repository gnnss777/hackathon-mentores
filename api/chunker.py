import re

def chunk_text(texto, fonte, chunk_size=500):
    if fonte.startswith("yt_"):
        linhas = [l.strip() for l in texto.split("\n") if l.strip()]
        partes = []
        parte = []
        for linha in linhas:
            parte.append(linha)
            if len(" ".join(parte)) >= chunk_size:
                partes.append(" ".join(parte))
                parte = []
        if parte:
            partes.append(" ".join(parte))
        chunks = [{"texto": p, "fonte": fonte} for p in partes]
        return chunks if chunks else [{"texto": texto[:500], "fonte": fonte}]
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
