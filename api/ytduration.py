import json, re, urllib.request
from http.server import BaseHTTPRequestHandler

CACHE = {}
INVIDIOUS = "https://invidious.snopyta.org"

def fetch_duration(video_id):
    # Try Invidious API first (lightweight, no JS)
    req = urllib.request.Request(
        f"{INVIDIOUS}/api/v1/videos/{video_id}",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        if data.get("lengthSeconds"):
            return int(data["lengthSeconds"]), None
    except Exception:
        pass

    # Fallback: try YouTube oembed (returns some data)
    try:
        req2 = urllib.request.Request(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        resp2 = urllib.request.urlopen(req2, timeout=10)
        data2 = json.loads(resp2.read().decode("utf-8"))
        return None, None
    except Exception:
        pass

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
            secs, _ = fetch_duration(video_id)
            if secs:
                result = {"ok": True, "segundos": secs}
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
