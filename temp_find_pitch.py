import json, sys
sys.stdout.reconfigure(encoding="utf-8")

chunks = json.load(open("api/chunks.json", encoding="utf-8"))
for c in chunks:
    txt = c["texto"].lower()
    if "pitch" in txt or "prototipo" in txt or "prototipagem" in txt:
        if "plataforma" in txt or "youtube" in txt or "link" in txt or "grav" in txt:
            print("=== %s ===" % c["fonte"])
            print(c["texto"][:400])
            print()
