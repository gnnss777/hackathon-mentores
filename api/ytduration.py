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

def try_parse(html, pos, label):
    depth = 0
    in_string = False
    escape = False
    last_safe = pos
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
                    return json.loads(json_str), label + "_ok"
                except json.JSONDecodeError as e:
                    return None, f"{label}_json_err:{e}"
    return None, f"{label}_no_end"

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

    # Try regex match for ytInitialPlayerResponse
    m = re.search(r'var\s+ytInitialPlayerResponse\s*=\s*{', html)
    if m:
        data, status = try_parse(html, m.end() - 1, "ipr")
        if data:
            vd = data.get("videoDetails", {})
            secs = str(vd.get("lengthSeconds", ""))
            if secs and secs != "0":
                return int(secs), None
            return None, f"ipr_secs={secs}"
        return None, status

    # Check if string exists at all
    idx = html.find("ytInitialPlayerResponse")
    if idx >= 0:
        snippet = html[idx:idx+100]
        return None, f"ytipr_exists_but_no_match:{snippet[:80]}"

    # Fallback: direct regex for lengthSeconds
    for p in [r'"approxDurationMs"\s*:\s*"?(\d+)"?', r'"lengthSeconds"\s*:\s*"?(\d+)"?']:
        m2 = re.search(p, html)
        if m2:
            val = int(m2.group(1))
            return round(val / 1000) if val > 1000 else val, None

    return None, f"no_ytipr len={len(html)}"

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
            self._respond({"ok": False, "erro": f"{type(e).__name__}:{e}"})

    def _respond(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
