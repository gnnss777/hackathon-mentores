import json
import os
from http.server import BaseHTTPRequestHandler

CUSTOM_PATH = "api/custom_chunks.json"

def load_custom():
    if os.path.exists(CUSTOM_PATH):
        with open(CUSTOM_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_custom(chunks):
    with open(CUSTOM_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        try:
            chunks = load_custom()
            response = json.dumps({"customChunks": chunks, "total": len(chunks)}, ensure_ascii=False).encode("utf-8")
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

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            novos = data.get("chunks", [])
            if not novos:
                raise ValueError("Nenhum chunk enviado")
            existentes = load_custom()
            existentes.extend(novos)
            save_custom(existentes)
            response = json.dumps({"ok": True, "total": len(existentes)}, ensure_ascii=False).encode("utf-8")
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

    def do_DELETE(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            data = json.loads(body) if body else {}
            fontes_remover = data.get("fontes", [])
            if not fontes_remover:
                fontes_remover = ["__all__"]
            existentes = load_custom()
            if "__all__" in fontes_remover:
                novos = []
            else:
                novos = [c for c in existentes if c.get("fonte") not in fontes_remover]
            removidos = len(existentes) - len(novos)
            save_custom(novos)
            response = json.dumps({"ok": True, "removidos": removidos, "total": len(novos)}, ensure_ascii=False).encode("utf-8")
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
