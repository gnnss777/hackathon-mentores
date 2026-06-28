import json
import re
from http.server import BaseHTTPRequestHandler

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

def chunk_text(texto, fonte, chunk_size=500):
    linhas = [l.strip() for l in texto.replace(". ", ".\n").replace("? ", "?\n").replace("! ", "!\n").split("\n") if l.strip()]
    partes = []
    parte = []
    for linha in linhas:
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

def fetch_via_library(video_id):
    from youtube_transcript_api import YouTubeTranscriptApi
    import requests
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    api = YouTubeTranscriptApi(http_client=session)
    transcript = api.fetch(video_id, languages=["pt", "pt-BR", "en"])
    parts = []
    for seg in transcript:
        if seg.text.strip():
            parts.append(seg.text)
    return " ".join(parts)

def fetch_via_innertube(video_id):
    import requests
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Content-Type": "application/json"})
    payload = {
        "context": {"client": {"clientName": "ANDROID", "clientVersion": "20.10.38"}},
        "videoId": video_id
    }
    r = session.post(
        "https://www.youtube.com/youtubei/v1/player?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        json=payload, timeout=20
    )
    if r.status_code != 200:
        raise ValueError(f"Innertube API retornou status {r.status_code}")
    data = r.json()
    tracks = data.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])
    if not tracks:
        raise ValueError("Este vídeo não possui legendas disponíveis")
    base = tracks[0]["baseUrl"]
    r2 = session.get(base, timeout=15)
    if not r2.text:
        raise ValueError("Resposta vazia ao baixar legendas")
    texts = re.findall(r'<text[^>]*>([^<]*)</text>', r2.text)
    if not texts:
        raise ValueError("Nenhuma legenda encontrada no XML")
    full = " ".join(t.replace("&#39;", "'").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"') for t in texts)
    return full

def fetch_captions(video_id):
    erros = []
    try:
        return fetch_via_library(video_id)
    except Exception as e1:
        erros.append(f"lib: {e1}")
    try:
        return fetch_via_innertube(video_id)
    except Exception as e2:
        erros.append(f"innertube: {e2}")
    raise ValueError("Não foi possível obter legendas. " + " | ".join(erros))

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
            text = fetch_captions(video_id)
            text = re.sub(r'\s+', ' ', text).strip()
            if not text or len(text) < 20:
                raise ValueError("Nenhuma legenda encontrada para este vídeo")
            fonte = f"yt_{video_id}"
            chunks = chunk_text(text, fonte)
            response = json.dumps({
                "chunks": chunks,
                "total_chunks": len(chunks),
                "total_chars": len(text),
                "fonte": fonte,
                "video_id": video_id
            }, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response)
        except Exception as e:
            msg = str(e)
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"erro": msg}, ensure_ascii=False).encode("utf-8"))
