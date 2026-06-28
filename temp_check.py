import json, sys
sys.stdout.reconfigure(encoding="utf-8")
chunks = json.load(open("api/chunks.json", encoding="utf-8"))
duvidas = [c for c in chunks if c["fonte"] == "duvidas-discord"]
print("Total duvidas-discord:", len(duvidas))
for c in duvidas:
    t = c["texto"][:150].replace("\n", " ")
    print(f'  [{len(c["texto"])} chars] {t}')
