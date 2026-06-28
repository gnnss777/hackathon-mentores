import json, re, urllib.request, os, sys
from http.server import BaseHTTPRequestHandler

CACHE = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

def fetch_duration(video_id):
    req = urllib.request.Request(
        f"https://www.youtube.com/watch?v={video_id}",
        headers=HEADERS
    )
    resp = urllib.request.urlopen(req, timeout=20)
    raw = resp.read()
    html = raw.decode("utf-8", errors="replace")

    # try multiple patterns
    patterns = [
        r'approxDurationMs["\']?\s*[:=]\s*["\']?(\d+)',
        r'"approxDurationMs":"(\d+)"',
        r'approxDurationMs[=:]\s*(\d+)',
        r'length_seconds["\']?\s*[:=]\s*["\']?(\d+)',
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            return int(m.group(1)), None
    return None, html[:2000]  # snippet for debug

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
            ms, snippet = fetch_duration(video_id)
            if ms:
                secs = round(ms / 1000)
                result = {"ok": True, "segundos": secs}
            else:
                result = {"ok": False, "erro": "duration_not_found", "debug": f"html_len={len(snippet) if snippet else 0}", "snippet": (snippet[:500] if snippet else "")}
            CACHE[cache_key] = result
            self._respond(result)
        except Exception as e:
            self._respond({"ok": False, "erro": str(e), "debug": f"{type(e).__name__}: {e}"})

    def _respond(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
