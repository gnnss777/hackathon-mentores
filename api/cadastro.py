import json
import csv
import urllib.request
import io
from http.server import BaseHTTPRequestHandler

SHEET_URL = "https://docs.google.com/spreadsheets/d/1Crxg12HWMXegI2lLJIevkfu4SllnRV86yFDrFRS35SU/export?format=csv&gid=1121424127"

def fetch():
    resp = urllib.request.urlopen(SHEET_URL)
    content = resp.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    result = {}
    for r in reader:
        team = (r.get("Qual o n\u00famero da sua equipe? (se n\u00e3o souber pergunte pra organiza\u00e7\u00e3o) *") or "").strip()
        completo = (r.get("Inscri\u00e7\u00e3o Completa?") or "").strip()
        desafio = (r.get("1. Selecione qual desafio a sua equipe ir\u00e1 resolver no HaCARthon. *") or "").strip()
        if team:
            # Normalize desafio
            d = ""
            if "1" in desafio or "Simplificar" in desafio:
                d = "D1"
            elif "2" in desafio or "geoespaciais" in desafio or "dados" in desafio.lower():
                d = "D2"
            elif "3" in desafio or "Legisla" in desafio or "entendimento" in desafio.lower():
                d = "D3"
            result[team] = {"completo": completo, "desafio": d}
    return result

CACHE = None

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        global CACHE
        try:
            if CACHE is None:
                CACHE = fetch()
            response = json.dumps({
                "total": len(CACHE),
                "teams": CACHE
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

    def do_POST(self):
        global CACHE
        try:
            CACHE = fetch()
            response = json.dumps({"ok": True, "total": len(CACHE)}, ensure_ascii=False).encode("utf-8")
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
