import json, re, urllib.request
from http.server import BaseHTTPRequestHandler

CACHE = {}

MOBILE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.147 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_duration(video_id):
    # Strategy 1: try mobile YouTube (better chance than desktop)
    try:
        req = urllib.request.Request(
            f"https://m.youtube.com/watch?v={video_id}",
            headers=MOBILE_HEADERS
        )
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8", errors="replace")

        patterns = [
            (r'approxDurationMs["\']?\s*[:=]\s*["\']?(\d+)', int),
            (r'"lengthSeconds":"?(\d+)"?', int),
            (r'length_seconds["\']?\s*[:=]\s*["\']?(\d+)', int),
            (r'videoDetails.*?"lengthSeconds":"(\d+)"', int),
        ]
        for pat, cast in patterns:
            m = re.search(pat, html)
            if m:
                return cast(m.group(1)), None
    except Exception:
        pass

    # Strategy 2: try desktop YouTube with curl-like headers
    try:
        req2 = urllib.request.Request(
            f"https://www.youtube.com/watch?v={video_id}",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        resp2 = urllib.request.urlopen(req2, timeout=15)
        html2 = resp2.read().decode("utf-8", errors="replace")
        patterns2 = [
            (r'approxDurationMs["\']?\s*[:=]\s*["\']?(\d+)', int),
            (r'"lengthSeconds":"?(\d+)"?', int),
        ]
        for pat, cast in patterns2:
            m2 = re.search(pat, html2)
            if m2:
                return cast(m2.group(1)), None
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
