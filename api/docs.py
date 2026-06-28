import json
from http.server import BaseHTTPRequestHandler

with open("api/chunks.json", encoding="utf-8") as f:
    CHUNKS = json.load(f)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        try:
            grupos = {}
            for c in CHUNKS:
                f = c["fonte"]
                if f not in grupos:
                    grupos[f] = {"fonte": f, "total": 0, "total_chars": 0, "amostra": ""}
                grupos[f]["total"] += 1
                grupos[f]["total_chars"] += len(c["texto"])
                if not grupos[f]["amostra"]:
                    grupos[f]["amostra"] = c["texto"][:120]

            legendas = {
                "briefing": "Briefing dos Desafios (PDF)",
                "guia": "Guia do Participante (PDF)",
                "acesso_cadastro": "Acesso ao Cadastro (PDF)",
                "edital": "Edital (PDF)",
                "yt_ideacao_prototipo": "Live: Ideação e Protótipo",
                "yt_orientacoes_gerais": "Live: Orientações Gerais",
                "yt_pitch": "Live: Pitch",
                "yt_tira_duvidas1": "Live: Tira-dúvidas 1",
                "yt_tira_duvidas2": "Live: Tira-dúvidas 2",
                "avisos-programacao": "Avisos e Programação (Markdown)",
                "mentores": "Mentores (88 fichas)",
                "duvidas-discord": "Dúvidas do Discord (FAQ)"
            }

            docs = []
            for f in sorted(grupos.keys()):
                g = grupos[f]
                docs.append({
                    "fonte": f,
                    "nome": legendas.get(f, f),
                    "total": g["total"],
                    "total_chars": g["total_chars"],
                    "amostra": g["amostra"]
                })

            response = json.dumps({
                "total_chunks": len(CHUNKS),
                "documentos": docs
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
