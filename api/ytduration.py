import json
from http.server import BaseHTTPRequestHandler

CACHE = {}

def fetch_duration(video_id):
    import yt_dlp
    opts = {"quiet": True, "no_warnings": True, "extract_flat": False}
    info = yt_dlp.YoutubeDL(opts).extract_info(
        f"https://www.youtube.com/watch?v={video_id}",
        download=False
    )
    if info and info.get("duration"):
        return info["duration"]
    return None

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
            secs = fetch_duration(video_id)
            if secs:
                result = {"ok": True, "segundos": secs}
            else:
                result = {"ok": False, "erro": "duration_not_found"}
            CACHE[video_id] = result
            self._respond(result)
        except Exception as e:
            self._respond({"ok": False, "erro": f"{type(e).__name__}:{e}"})

    def _respond(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
