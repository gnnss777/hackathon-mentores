import json, re, urllib.request
from http.server import BaseHTTPRequestHandler

CACHE = {}

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
        if video_id in CACHE:
            self._respond(CACHE[video_id])
            return
        try:
            req = urllib.request.Request(
                f"https://www.youtube.com/watch?v={video_id}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
            m = re.search(r'"approxDurationMs":"(\d+)"', html)
            if m:
                secs = round(int(m.group(1)) / 1000)
                result = {"ok": True, "segundos": secs}
            else:
                result = {"ok": False, "erro": "duration_not_found"}
            CACHE[video_id] = result
            self._respond(result)
        except Exception as e:
            self._respond({"ok": False, "erro": str(e)})

    def _respond(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
