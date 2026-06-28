import json, re, requests, sys
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
        return None, f"http_error: {e}"
    patterns = [
        r'"approxDurationMs":"(\d+)"',
        r'approxDurationMs["\']?\s*[:=]\s*["\']?(\d+)',
        r'"lengthSeconds":"(\d+)"',
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            val = int(m.group(1))
            secs = round(val / 1000) if val > 1000 else val
            return secs, None
    snippet = html[:300] if html else ""
    has_captcha = "captcha" in html.lower() or "recaptcha" in html.lower()
    return None, f"not_found len={len(html)} captcha={has_captcha} snippet={snippet[:100]}"

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
        cache_key = video_id
        if cache_key in CACHE:
            self._respond(CACHE[cache_key])
            return
        try:
            secs, dbg = fetch_duration(video_id)
            if secs:
                result = {"ok": True, "segundos": secs}
            else:
                result = {"ok": False, "erro": dbg or "duration_not_found"}
            CACHE[cache_key] = result
            self._respond(result)
        except Exception as e:
            self._respond({"ok": False, "erro": f"{type(e).__name__}: {str(e)[:200]}"})

    def _respond(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
