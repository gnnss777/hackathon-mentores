import json, sys
sys.stdout.reconfigure(encoding="utf-8")
chunks = json.load(open("api/chunks.json", encoding="utf-8"))
for c in chunks:
    t = c["texto"].lower()
    if "paniclobster" in t or "entregas" in t:
        muestra = c["texto"][:250].replace("\n", " ")
        print("=== %s ===" % c["fonte"])
        print(muestra)
        print()
