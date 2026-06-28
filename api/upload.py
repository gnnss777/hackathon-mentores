import json
import os
import re
import base64
import io
from http.server import BaseHTTPRequestHandler

def chunk_text(texto, fonte, chunk_size=500):
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

def extract_text_pdf(content_bytes):
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content_bytes))
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        return "\n".join(text_parts)
    except ImportError:
        raise Exception("pypdf library not available")

def extract_text_docx(content_bytes):
    try:
        from docx import Document
        doc = Document(io.BytesIO(content_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        raise Exception("python-docx library not available")

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

            filename = data.get("filename", "documento.txt")
            content_b64 = data.get("content", "")
            file_type = data.get("type", "")

            if not content_b64:
                raise ValueError("Nenhum arquivo enviado")

            content_bytes = base64.b64decode(content_b64)

            lower = filename.lower()
            if file_type == "pdf" or lower.endswith(".pdf"):
                text = extract_text_pdf(content_bytes)
            elif file_type == "docx" or lower.endswith(".docx"):
                text = extract_text_docx(content_bytes)
            else:
                text = content_bytes.decode("utf-8", errors="replace")

            if not text.strip():
                raise ValueError("Nenhum texto extraído do arquivo")

            fonte = f"custom_{filename.replace('.', '_')}"
            chunks = chunk_text(text, fonte)

            response = json.dumps({
                "chunks": chunks,
                "total_chars": len(text),
                "total_chunks": len(chunks),
                "fonte": fonte,
                "filename": filename
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
