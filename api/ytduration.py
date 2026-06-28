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

def extract_json(html, key):
    start_marker = 'var ' + key + ' = '
    pos = html.find(start_marker)
    if pos == -1:
        start_marker2 = key + ' = '
        pos = html.find(start_marker2)
        if pos >= 0:
            pos += len(start_marker2)
            if pos < len(html) and html[pos] == '{':
                return _parse_json(html, pos)
    else:
        pos += len(start_marker)
        if pos < len(html) and html[pos] == '{':
            return _parse_json(html, pos)

    # Try with \\s* between key and =
    m = re.search(re.escape(key) + r'\s*=\s*{', html)
    if m:
        return _parse_json(html, m.end() - 1)
    return None

def _parse_json(html, pos):
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
                json_str = html[pos:i+1]
                try:
                    return json.loads(json_str)
                except Exception:
                    return None
    return None

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

    # Debug: check if key strings exist
    has_ytipr = 'ytInitialPlayerResponse' in html
    has_ytid = 'ytInitialData' in html
    debug = f"ytIPR={has_ytipr} ytID={has_ytid}"

    data = extract_json(html, "ytInitialPlayerResponse")
    if data:
        vd = data.get("videoDetails", {})
        secs = vd.get("lengthSeconds")
        if secs and str(secs) != "0":
            return int(secs), None

    data2 = extract_json(html, "ytInitialData")
    if data2:
        try:
            contents = data2.get("contents", {})
            two_col = contents.get("twoColumnWatchNextResults", {})
            results = two_col.get("results", {}).get("results", {})
            for item in results.get("contents", []):
                vp = item.get("videoPrimaryInfoRenderer", {})
                dur = vp.get("length", 0)
                if dur and str(dur) != "0":
                    return int(dur), None
        except Exception:
            pass

    for p in [r'"approxDurationMs"\s*:\s*"?(\d+)"?', r'"lengthSeconds"\s*:\s*"?(\d+)"?']:
        m = re.search(p, html)
        if m:
            val = int(m.group(1))
            return round(val / 1000) if val > 1000 else val, None

    return None, debug + f" len={len(html)}"

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
