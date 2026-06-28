import json
import csv
import urllib.request
import io
from http.server import BaseHTTPRequestHandler

SHEET_URL = "https://docs.google.com/spreadsheets/d/1Crxg12HWMXegI2lLJIevkfu4SllnRV86yFDrFRS35SU/export?format=csv"

def fetch_sheet():
    resp = urllib.request.urlopen(SHEET_URL)
    content = resp.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    for r in reader:
        rows.append(r)
    return rows

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
                CACHE = fetch_sheet()
            response = json.dumps({
                "total": len(CACHE),
                "rows": CACHE
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
            CACHE = fetch_sheet()
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
