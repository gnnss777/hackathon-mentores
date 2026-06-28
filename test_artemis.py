import json, urllib.request

apis = [
    "https://yt.artemislena.eu",
    "https://yt.cherrymint.dev",
]

video_id = "dQw4w9WgXcQ"
for api in apis:
    try:
        req = urllib.request.Request(
            f"{api}/api/v1/videos/{video_id}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        dur = data.get("lengthSeconds")
        print(f"{api}: OK, lengthSeconds={dur}")
    except Exception as e:
        print(f"{api}: FAIL - {type(e).__name__}: {e}")
