import json, re, urllib.request
from http.server import BaseHTTPRequestHandler

CACHE = {}

# Multiple Invidious instances as fallback
INVIDIOUS_INSTANCES = [
    "https://inv.nadeko.net",
    "https://invidious.xyz",
    "https://yewtu.be",
    "https://invidious.protokolla.fi",
]

def fetch_duration(video_id):
    for instance in INVIDIOUS_INSTANCES:
        try:
            req = urllib.request.Request(
                f"{instance}/api/v1/videos/{video_id}",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("lengthSeconds"):
                return int(data["lengthSeconds"]), instance
        except Exception:
            continue
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
            secs, used = fetch_duration(video_id)
            if secs:
                result = {"ok": True, "segundos": secs, "source": used}
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
