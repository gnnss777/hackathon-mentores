import json, re
import urllib.request
from http.server import BaseHTTPRequestHandler

CACHE = {}

def fetch_duration(video_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    req = urllib.request.Request(
        f"https://www.youtube.com/watch?v={video_id}",
        headers=headers
    )
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode("utf-8", errors="replace")

    patterns = [
        r'approxDurationMs["\']?\s*[:=]\s*["\']?(\d+)',
        r'"lengthSeconds":"?(\d+)"?',
        r'length_seconds["\']?\s*[:=]\s*["\']?(\d+)',
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            return int(m.group(1)), p
    return None, None

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
        video_id = (params.get('v') or [None])[0]
        if not video_id:
            self.send_error(400, "Missing ?v=VIDEO_ID")
            return
        cache_key = video_id
        if cache_key in CACHE:
            self._respond(CACHE[cache_key])
            return
        try:
            ms, pat = fetch_duration(video_id)
            if ms:
                secs = round(ms / 1000) if ms > 1000 else ms
                result = {"ok": True, "segundos": secs, "ms": ms, "pat": pat}
            else:
                result = {"ok": False, "erro": "duration_not_found"}
            CACHE[cache_key] = result
            self._respond(result)
        except Exception as e:
            self._respond({"ok": False, "erro": str(e)})

    def _respond(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
