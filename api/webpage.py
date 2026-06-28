import json
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

def chunk_text(texto, fonte, chunk_size=500):
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
            url = data.get("url", "").strip()
            if not url:
                raise ValueError("URL vazia")
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("URL inválida")
            import trafilatura
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                raise ValueError("Não foi possível acessar a URL")
            texto = trafilatura.extract(downloaded, output_format="txt", include_links=True, include_tables=True)
            if not texto or not texto.strip():
                raise ValueError("Nenhum conteúdo textual encontrado na página")
            domain = parsed.netloc.replace("www.", "")
            fonte = f"webpage_{domain}"
            chunks = chunk_text(texto, fonte)
            response = json.dumps({
                "chunks": chunks,
                "total_chars": len(texto),
                "total_chunks": len(chunks),
                "fonte": fonte,
                "url": url
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
