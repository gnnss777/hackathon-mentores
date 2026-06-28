import json, re, requests
from http.server import BaseHTTPRequestHandler

CACHE = {}
SESSION = None

def get_session():
    global SESSION
    if SESSION is None:
        SESSION = requests.Session()
        SESSION.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        })
        try:
            SESSION.get("https://www.youtube.com/", timeout=8)
        except Exception:
            pass
    return SESSION

def fetch_duration(video_id):
    session = get_session()
    try:
        resp = session.get(
            f"https://www.youtube.com/watch?v={video_id}",
            timeout=12
        )
        html = resp.text
    except Exception as e:
        return None, f"http: {e}"

    # Pattern 1: ytInitialPlayerResponse JSON
    m = re.search(r'ytInitialPlayerResponse\s*=\s*({.*?});\s*var\s+', html)
    if m:
        try:
            data = json.loads(m.group(1))
            vd = data.get("videoDetails", {})
            secs = vd.get("lengthSeconds")
            if secs:
                return int(secs), None
        except Exception:
            pass

    # Pattern 2: legacy approxDurationMs
    for p in [
        r'"approxDurationMs":"(\d+)"',
        r'approxDurationMs["\']?\s*[:=]\s*["\']?(\d+)',
    ]:
        m2 = re.search(p, html)
        if m2:
            val = int(m2.group(1))
            return round(val / 1000) if val > 1000 else val, None

    # Pattern 3: lengthSeconds in any JSON context
    m3 = re.search(r'"lengthSeconds"\s*:\s*"?(\d+)"?', html)
    if m3:
        return int(m3.group(1)), None

    return None, f"no_match len={len(html)}"

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(self.path).query)
        video_id = (params.get("v") or [None])[0]
        if not video_id:
            self.send_error(400, "Missing ?v=VIDEO_ID")
            return
        if video_id in CACHE:
            self._respond(CACHE[video_id])
            return
        try:
            secs, dbg = fetch_duration(video_id)
            if secs:
                result = {"ok": True, "segundos": secs}
            else:
                result = {"ok": False, "erro": dbg or "duration_not_found"}
            CACHE[video_id] = result
            self._respond(result)
        except Exception as e:
            self._respond({"ok": False, "erro": f"{type(e).__name__}: {str(e)[:200]}"})

    def _respond(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
