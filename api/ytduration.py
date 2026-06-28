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

def try_parse(html, pos):
    depth = 0
    in_string = False
    escape = False
    for i in range(pos, len(html)):
        c = html[i]
        if escape:
            escape = False
            continue
        if c == '\\' and in_string:
            escape = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(html[pos:i+1])
                except Exception:
                    return None
    return None

def fetch_duration(video_id):
    session = get_session()
    try:
        resp = session.get(
            f"https://www.youtube.com/watch?v={video_id}",
            timeout=15
        )
        html = resp.text
    except Exception as e:
        return None, f"http:{e}"

    m = re.search(r'var\s+ytInitialPlayerResponse\s*=\s*{', html)
    if not m:
        return None, f"no_regex_match len={len(html)}"

    data = try_parse(html, m.end() - 1)
    if not data:
        return None, f"json_parse_fail"

    vd = data.get("videoDetails", {})
    if not vd:
        vd_keys = list(data.keys())[:5]
        return None, f"no_videoDetails keys={vd_keys}"

    ls = vd.get("lengthSeconds")
    if ls:
        return int(str(ls)), None

    # Try alternate fields
    for alt in ["duration", "length", "videoDuration"]:
        v = vd.get(alt)
        if v:
            return int(str(v)), None

    keys = list(vd.keys())[:15]
    return None, f"vd_keys={keys}"

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
                result = {"ok": False, "erro": dbg or "?"}
            CACHE[video_id] = result
            self._respond(result)
        except Exception as e:
            self._respond({"ok": False, "erro": str(e)[:200]})

    def _respond(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
