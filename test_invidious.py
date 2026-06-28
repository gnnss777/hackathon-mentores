import json, urllib.request

servers = [
    "https://invidious.snopyta.org",
    "https://yewtu.be",
    "https://inv.vern.cc",
    "https://invidious.private.coffee",
    "https://invidious.lunar.icu",
]

video_id = "dQw4w9WgXcQ"
for srv in servers:
    try:
        req = urllib.request.Request(
            f"{srv}/api/v1/videos/{video_id}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read().decode("utf-8"))
        dur = data.get("lengthSeconds")
        print(f"{srv}: OK, lengthSeconds={dur}")
    except Exception as e:
        print(f"{srv}: FAIL - {type(e).__name__}: {e}")
