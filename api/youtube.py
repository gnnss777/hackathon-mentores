import json
import re
from http.server import BaseHTTPRequestHandler

def chunk_text(texto, fonte, chunk_size=500):
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
    if not partes:
        partes = [texto[:500]]
    return [{"texto": p, "fonte": fonte} for p in partes]

def extract_video_id(url):
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

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
            url = data.get("url", "")

            video_id = extract_video_id(url)
            if not video_id:
                raise ValueError("URL do YouTube inválida")

            from youtube_transcript_api import YouTubeTranscriptApi
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=["pt"])
            text = " ".join([s.text for s in transcript.snippets])

            if not text.strip():
                raise ValueError("Nenhuma legenda encontrada para este vídeo")

            fonte = f"yt_{video_id}"
            chunks = chunk_text(text, fonte)

            response = json.dumps({
                "chunks": chunks,
                "total_chunks": len(chunks),
                "total_chars": len(text),
                "fonte": fonte,
                "video_id": video_id,
                "title": video_id
            }, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response)

        except Exception as e:
            msg = str(e)
            if "Subtitles are disabled" in msg:
                msg = "Este vídeo não possui legendas disponíveis"
            elif "Could not find a transcript" in msg:
                msg = "Nenhuma legenda encontrada para este vídeo"
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"erro": msg}, ensure_ascii=False).encode("utf-8"))
